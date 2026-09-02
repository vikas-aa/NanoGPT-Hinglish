import torch
from tokenizers import Tokenizer
from model import NanoGPT, GPTConfig


# ============================================================
# DEVICE
# ============================================================

device = "cuda" if torch.cuda.is_available() else "cpu"

print("Device:", device)


# ============================================================
# TOKENIZER
# ============================================================

print("Loading tokenizer...")

tokenizer = Tokenizer.from_file(
    "data/tokenizer.json"
)

print("Tokenizer loaded.")


# ============================================================
# LOAD BEST CHECKPOINT
# ============================================================

print("Loading model...")

checkpoint = torch.load(
    "checkpoints/best_nanogpt.pt",
    map_location=device
)

config = GPTConfig()

config.vocab_size = checkpoint["config"]["vocab_size"]
config.block_size = checkpoint["config"]["block_size"]
config.n_embd = checkpoint["config"]["n_embd"]
config.n_head = checkpoint["config"]["n_head"]
config.n_layer = checkpoint["config"]["n_layer"]
config.dropout = checkpoint["config"]["dropout"]


# ============================================================
# MODEL
# ============================================================

model = NanoGPT(config).to(device)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()

print("Model loaded successfully!")
print("Parameters:", sum(p.numel() for p in model.parameters()))


# ============================================================
# SPECIAL TOKENS
# ============================================================

USER_TOKEN = tokenizer.token_to_id("<|user|>")
ASSISTANT_TOKEN = tokenizer.token_to_id("<|assistant|>")


# ============================================================
# GENERATION
# ============================================================

@torch.no_grad()
def generate(
    prompt,
    max_new_tokens=100,
    temperature=0.7,
    top_k=40,
    top_p=0.90,
    repetition_penalty=1.10
):

    encoded = tokenizer.encode(prompt)

    tokens = encoded.ids

    x = torch.tensor(
        [tokens],
        dtype=torch.long,
        device=device
    )

    generated_tokens = []

    for _ in range(max_new_tokens):

        # Keep only model context window
        x_cond = x[:, -config.block_size:]

        logits, _ = model(x_cond)

        # Last token logits
        logits = logits[:, -1, :]

        # ----------------------------------------------------
        # REPETITION PENALTY
        # ----------------------------------------------------

        if repetition_penalty > 1.0:

            for token_id in set(x[0].tolist()):

                if logits[0, token_id] > 0:
                    logits[0, token_id] /= repetition_penalty
                else:
                    logits[0, token_id] *= repetition_penalty

        # ----------------------------------------------------
        # TEMPERATURE
        # ----------------------------------------------------

        logits = logits / temperature

        # ----------------------------------------------------
        # TOP-K
        # ----------------------------------------------------

        if top_k is not None:

            top_k_value = min(
                top_k,
                logits.size(-1)
            )

            values, indices = torch.topk(
                logits,
                top_k_value
            )

            filtered_logits = torch.full_like(
                logits,
                float("-inf")
            )

            filtered_logits.scatter_(
                1,
                indices,
                values
            )

            logits = filtered_logits

        # ----------------------------------------------------
        # TOP-P / NUCLEUS SAMPLING
        # ----------------------------------------------------

        if top_p is not None and top_p < 1.0:

            sorted_logits, sorted_indices = torch.sort(
                logits,
                descending=True
            )

            sorted_probs = torch.softmax(
                sorted_logits,
                dim=-1
            )

            cumulative_probs = torch.cumsum(
                sorted_probs,
                dim=-1
            )

            remove_mask = cumulative_probs > top_p

            # Always keep at least one token
            remove_mask[:, 0] = False

            sorted_logits[remove_mask] = float("-inf")

            logits = torch.full_like(logits, float("-inf"))

            logits.scatter_(
                1,
                sorted_indices,
                sorted_logits
            )

        # ----------------------------------------------------
        # SAMPLE
        # ----------------------------------------------------

        probabilities = torch.softmax(
            logits,
            dim=-1
        )

        next_token = torch.multinomial(
            probabilities,
            num_samples=1
        )

        token_id = next_token.item()

        # ----------------------------------------------------
        # STOP SPECIAL TOKENS
        # ----------------------------------------------------

        if token_id == USER_TOKEN:
            break

        if token_id == ASSISTANT_TOKEN:
            break

        generated_tokens.append(token_id)

        x = torch.cat(
            [x, next_token],
            dim=1
        )

    # Decode ONLY generated response
    response = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True
    )

    return response.strip()


# ============================================================
# CHAT HISTORY
# ============================================================

conversation = []


def build_prompt(user_message):

    conversation_text = ""

    for user_msg, assistant_msg in conversation:

        conversation_text += (
            "<|user|>\n"
            + user_msg
            + "\n"
            + "<|assistant|>\n"
            + assistant_msg
            + "\n"
        )

    conversation_text += (
        "<|user|>\n"
        + user_message
        + "\n"
        + "<|assistant|>\n"
    )

    # --------------------------------------------------------
    # Keep prompt within model context
    # --------------------------------------------------------

    encoded = tokenizer.encode(conversation_text)

    if len(encoded.ids) > config.block_size - 100:

        # Keep the newest part of conversation
        recent_ids = encoded.ids[
            -(config.block_size - 100):
        ]

        conversation_text = tokenizer.decode(
            recent_ids,
            skip_special_tokens=False
        )

        # Make sure current assistant turn exists
        if not conversation_text.endswith(
            "<|assistant|>\n"
        ):
            conversation_text += "\n<|assistant|>\n"

    return conversation_text


# ============================================================
# CHAT UI
# ============================================================

print("\n" + "=" * 60)
print("NanoGPT Chat")
print("=" * 60)

print("Type 'exit' to quit.")
print("Type 'clear' to clear conversation.\n")


# ============================================================
# CHAT LOOP
# ============================================================

while True:

    user_input = input("You: ").strip()

    if user_input.lower() == "exit":

        print("Goodbye!")

        break

    if user_input.lower() == "clear":

        conversation.clear()

        print("\nConversation cleared.\n")

        continue

    if not user_input:

        continue

    # --------------------------------------------------------
    # Build conversation prompt
    # --------------------------------------------------------

    prompt = build_prompt(user_input)

    # --------------------------------------------------------
    # Generate
    # --------------------------------------------------------

    response = generate(
    prompt,
    max_new_tokens=60,
    temperature=0.3,
    top_k=20,
    top_p=0.85,
    repetition_penalty=1.05
)

    # --------------------------------------------------------
    # Safety cleanup
    # --------------------------------------------------------

    response = response.replace(
        "<|user|>",
        ""
    ).replace(
        "<|assistant|>",
        ""
    ).strip()

    # Remove accidental prefixes
    if response.lower().startswith("assistant:"):
        response = response[len("assistant:"):].strip()

    if response.lower().startswith("nanogpt:"):
        response = response[len("nanogpt:"):].strip()

    # --------------------------------------------------------
    # Save conversation
    # --------------------------------------------------------

    conversation.append(
        (user_input, response)
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print("\nNanoGPT:", response)
    print()