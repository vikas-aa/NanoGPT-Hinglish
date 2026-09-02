"""
NanoGPT FastAPI Backend
Serves the trained NanoGPT model for the web chatbot.
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Optional
from contextlib import asynccontextmanager

import torch
from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

# ============================================================
# PATH SETUP
# ============================================================

# Resolve paths relative to this file so the server works
# regardless of working directory.
BACKEND_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = BACKEND_DIR.parent.resolve()

HF_REPO_ID = "vikas0905/nano-gpt-hinglish"
TOKENIZER_FILENAME = "tokenizer.json"
CHECKPOINT_FILENAME = "best_nanogpt.pt"

# Add project root to sys.path so we can import model.py
sys.path.insert(0, str(PROJECT_ROOT))

from model import NanoGPT, GPTConfig  # noqa: E402 (after sys.path insert)

# ============================================================
# GLOBALS (loaded once at startup)
# ============================================================

_model: Optional[NanoGPT] = None
_tokenizer: Optional[Tokenizer] = None
_config: Optional[GPTConfig] = None
_device: str = "cpu"

# ============================================================
# STARTUP / SHUTDOWN
# ============================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model and tokenizer once at startup."""
    global _model, _tokenizer, _config, _device

    _device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\nDevice: {_device.upper()}")

    # --- Tokenizer ---
    tokenizer_path = hf_hub_download(
        repo_id=HF_REPO_ID,
        filename=TOKENIZER_FILENAME,
    )
    print(f"Loading tokenizer from {tokenizer_path} ...")
    _tokenizer = Tokenizer.from_file(tokenizer_path)
    print("Tokenizer loaded.")

    # --- Checkpoint ---
    checkpoint_path = hf_hub_download(
        repo_id=HF_REPO_ID,
        filename=CHECKPOINT_FILENAME,
    )
    print(f"Loading checkpoint from {checkpoint_path} ...")
    checkpoint = torch.load(checkpoint_path, map_location=_device)

    # Build config from checkpoint
    _config = GPTConfig()
    _config.vocab_size = checkpoint["config"]["vocab_size"]
    _config.block_size = checkpoint["config"]["block_size"]
    _config.n_embd = checkpoint["config"]["n_embd"]
    _config.n_head = checkpoint["config"]["n_head"]
    _config.n_layer = checkpoint["config"]["n_layer"]
    _config.dropout = checkpoint["config"]["dropout"]

    # Build model
    _model = NanoGPT(_config).to(_device)
    _model.load_state_dict(checkpoint["model_state_dict"])
    _model.eval()

    params = sum(p.numel() for p in _model.parameters())
    print(f"Model loaded. Parameters: {params:,}")
    print("NanoGPT backend ready.\n")

    yield  # Server is running

    # Cleanup on shutdown (nothing heavy needed)
    print("Shutting down NanoGPT backend.")


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="NanoGPT API",
    description="FastAPI backend serving the trained NanoGPT model.",
    version="1.0.0",
    lifespan=lifespan,
)

# ============================================================
# CORS
# ============================================================

raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,https://nano-gpt-hinglish.vercel.app"
)
allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# ============================================================
# PYDANTIC MODELS
# ============================================================

MAX_MESSAGE_LENGTH = 1000


class MessageItem(BaseModel):
    role: str
    content: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ("user", "assistant"):
            raise ValueError("role must be 'user' or 'assistant'")
        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("content must not be empty")
        if len(v) > MAX_MESSAGE_LENGTH:
            raise ValueError(
                f"content exceeds maximum length of {MAX_MESSAGE_LENGTH}"
            )
        return v


class ChatRequest(BaseModel):
    # Multi-turn mode
    messages: Optional[List[MessageItem]] = None
    # Single-turn shorthand
    message: Optional[str] = None

    # Generation settings
    max_new_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_k: Optional[int] = None

    @field_validator("max_new_tokens")
    @classmethod
    def validate_max_new_tokens(cls, v):
        if v is not None and not (10 <= v <= 300):
            raise ValueError("max_new_tokens must be between 10 and 300")
        return v

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v):
        if v is not None and not (0.1 <= v <= 1.5):
            raise ValueError("temperature must be between 0.1 and 1.5")
        return v

    @field_validator("top_k")
    @classmethod
    def validate_top_k(cls, v):
        if v is not None and not (1 <= v <= 100):
            raise ValueError("top_k must be between 1 and 100")
        return v


class ChatResponse(BaseModel):
    response: str


class HealthResponse(BaseModel):
    status: str
    model: str
    device: str

# ============================================================
# GENERATION
# ============================================================

# Special tokens used during training
USER_TOKEN = "<|user|>"
ASSISTANT_TOKEN = "<|assistant|>"


def build_prompt(messages: List[MessageItem], config: GPTConfig, tokenizer: Tokenizer) -> str:
    """
    Convert a list of messages into the training-format prompt.
    Truncates from the oldest messages if the prompt is too long
    to fit within block_size.

    Format used during training:
        <|user|>
        USER_TEXT
        <|assistant|>
        ASSISTANT_TEXT
    """
    # Reserve tokens for the response
    MAX_PROMPT_TOKENS = config.block_size - 10

    def fmt(role: str, content: str) -> str:
        if role == "user":
            return f"{USER_TOKEN}\n{content}\n{ASSISTANT_TOKEN}\n"
        else:
            return f"{content}\n"

    # Build from the end, keeping the most recent turns
    segments = []
    for msg in messages:
        segments.append(fmt(msg.role, msg.content))

    # Trim from the front if too many tokens
    while len(segments) > 1:
        candidate = "".join(segments)
        token_count = len(tokenizer.encode(candidate).ids)
        if token_count <= MAX_PROMPT_TOKENS:
            break
        segments.pop(0)

    prompt = "".join(segments)

    # If there's no trailing assistant token (last message was user),
    # append it to signal the model to start the assistant turn.
    if not prompt.rstrip().endswith(ASSISTANT_TOKEN) and not prompt.endswith("\n" + ASSISTANT_TOKEN + "\n"):
        # Ensure we end with the assistant trigger
        if not prompt.endswith(f"{ASSISTANT_TOKEN}\n"):
            # Find last user block and ensure assistant token follows
            if ASSISTANT_TOKEN not in prompt.split(USER_TOKEN)[-1]:
                prompt = prompt.rstrip("\n") + "\n" + ASSISTANT_TOKEN + "\n"

    return prompt


@torch.no_grad()
def generate_response(
    messages: List[MessageItem],
    max_new_tokens: int = 100,
    temperature: float = 0.8,
    top_k: int = 50,
) -> str:
    """
    Generate an assistant response from the conversation history.
    Uses the globally loaded NanoGPT model and tokenizer.
    """
    assert _model is not None, "Model not loaded"
    assert _tokenizer is not None, "Tokenizer not loaded"
    assert _config is not None, "Config not loaded"

    prompt = build_prompt(messages, _config, _tokenizer)

    encoded = _tokenizer.encode(prompt)
    tokens = encoded.ids

    # Clamp to block_size
    if len(tokens) >= _config.block_size:
        tokens = tokens[-(_config.block_size - 1):]

    x = torch.tensor([tokens], dtype=torch.long, device=_device)

    # IDs for stop tokens
    user_token_id = _tokenizer.token_to_id(USER_TOKEN)
    assistant_token_id = _tokenizer.token_to_id(ASSISTANT_TOKEN)

    prompt_length = x.shape[1]

    for _ in range(max_new_tokens):
        x_cond = x[:, -_config.block_size:]

        logits, _ = _model(x_cond)
        logits = logits[:, -1, :]  # last position
        logits = logits / temperature

        # Top-k filtering
        if top_k is not None and top_k > 0:
            values, indices = torch.topk(logits, min(top_k, logits.size(-1)))
            filtered = torch.full_like(logits, float("-inf"))
            filtered.scatter_(1, indices, values)
            logits = filtered

        probs = torch.softmax(logits, dim=-1)
        next_token = torch.multinomial(probs, num_samples=1)

        x = torch.cat([x, next_token], dim=1)

        # Stop at user token (new conversation turn)
        if user_token_id is not None and next_token.item() == user_token_id:
            break

    # Decode only newly generated tokens
    generated_ids = x[0, prompt_length:].tolist()
    raw_output = _tokenizer.decode(generated_ids)

    return clean_response(raw_output)


def clean_response(text: str) -> str:
    """
    Strip special tokens and extraneous formatting from generated text.
    """
    # Remove any user / assistant turn continuation
    for stop in (USER_TOKEN, ASSISTANT_TOKEN):
        if stop in text:
            text = text.split(stop)[0]

    # Remove "You:" or "User:" prefixes the model might hallucinate
    text = re.sub(r"^(you|user)\s*:\s*", "", text, flags=re.IGNORECASE)

    # Normalise whitespace, preserve intentional newlines
    text = text.strip()

    return text


# ============================================================
# ROUTES
# ============================================================


@app.get("/api/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        model="NanoGPT",
        device=_device,
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if _model is None or _tokenizer is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded. Please try again shortly.",
        )

    # Build messages list from either multi-turn or single-message request
    if req.messages:
        messages = req.messages
    elif req.message:
        stripped = req.message.strip()
        if not stripped:
            raise HTTPException(status_code=422, detail="message must not be empty")
        if len(stripped) > MAX_MESSAGE_LENGTH:
            raise HTTPException(
                status_code=422,
                detail=f"message exceeds maximum length of {MAX_MESSAGE_LENGTH}",
            )
        messages = [MessageItem(role="user", content=stripped)]
    else:
        raise HTTPException(
            status_code=422,
            detail="Provide either 'message' or 'messages' in the request body.",
        )

    # Confirm the last message is from the user
    if messages[-1].role != "user":
        raise HTTPException(
            status_code=422,
            detail="The last message must be from the user.",
        )

    # Generation parameters with defaults
    max_new_tokens = req.max_new_tokens if req.max_new_tokens is not None else 100
    temperature = req.temperature if req.temperature is not None else 0.8
    top_k = req.top_k if req.top_k is not None else 50

    try:
        response = generate_response(
            messages=messages,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_k=top_k,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(exc)}",
        ) from exc

    if not response:
        response = "..."  # Graceful fallback for empty generation

    return ChatResponse(response=response)
