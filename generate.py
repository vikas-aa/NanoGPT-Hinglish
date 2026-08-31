import torch
from tokenizers import Tokenizer

from model import NanoGPT, GPTConfig


# ============================================================
# DEVICE
# ============================================================

device = "cuda" if torch.cuda.is_available() else "cpu"

print("Device:", device)


# ============================================================
# LOAD TOKENIZER
# ============================================================

print("Loading tokenizer...")

tokenizer = Tokenizer.from_file("data/tokenizer.json")

print("Tokenizer loaded.")


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading model...")

checkpoint = torch.load(
    "checkpoints/nanogpt.pt",
    map_location=device
)

config = GPTConfig()

config.vocab_size = checkpoint["config"]["vocab_size"]
config.block_size = checkpoint["config"]["block_size"]
config.n_embd = checkpoint["config"]["n_embd"]
config.n_head = checkpoint["config"]["n_head"]
config.n_layer = checkpoint["config"]["n_layer"]
config.dropout = checkpoint["config"]["dropout"]

model = NanoGPT(config).to(device)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()

print("Model loaded successfully!")


# ============================================================
# GENERATE
# ============================================================

@torch.no_grad()
def generate(
    prompt,
    max_new_tokens=80,
    temperature=0.7,
    top_k=40
):

    encoded = tokenizer.encode(prompt)

    tokens = encoded.ids

    x = torch.tensor(
        [tokens],
        dtype=torch.long,
        device=device
    )

    user_token = tokenizer.token_to_id("<|user|>")

    for _ in range(max_new_tokens):

        x_cond = x[:, -config.block_size:]

        logits, _ = model(x_cond)

        logits = logits[:, -1, :]

        logits = logits / temperature

        if top_k is not None:

            values, indices = torch.topk(
                logits,
                min(top_k, logits.size(-1))
            )

            filtered = torch.full_like(
                logits,
                float("-inf")
            )

            filtered.scatter_(
                1,
                indices,
                values
            )

            logits = filtered

        probabilities = torch.softmax(
            logits,
            dim=-1
        )

        next_token = torch.multinomial(
            probabilities,
            1
        )

        x = torch.cat(
            [x, next_token],
            dim=1
        )

        # Stop when model starts a new user message
        if user_token is not None:
            if next_token.item() == user_token:
                break

    return tokenizer.decode(
        x[0].tolist()
    )


# ============================================================
# TEST
# ============================================================

print("\n" + "=" * 60)
print("NanoGPT Chat")
print("=" * 60)

prompt = "<|user|>\nHi\n<|assistant|>\n"

print("\nPrompt:")
print(prompt)

print("\nGenerating...\n")

output = generate(
    prompt,
    max_new_tokens=80,
    temperature=0.7,
    top_k=40
)

print(output)

print("\n" + "=" * 60)