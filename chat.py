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
# LOAD CHECKPOINT
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


# ============================================================
# MODEL
# ============================================================

model = NanoGPT(config).to(device)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()

print("Model loaded successfully!")


# ============================================================
# GENERATION
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

        # Stop when new user turn begins
        if user_token is not None:
            if next_token.item() == user_token:
                break

    return tokenizer.decode(
        x[0].tolist()
    )

# ============================================================
# CHAT LOOP
# ============================================================

print("\n" + "=" * 60)
print("NanoGPT Chat")
print("=" * 60)

print("Type 'exit' to quit.\n")


while True:

    user_input = input("You: ").strip()

    if user_input.lower() == "exit":

        print("Goodbye!")

        break

    if not user_input:
        continue

    prompt = (
        "<|user|>\n"
        + user_input
        + "\n"
        + "<|assistant|>\n"
    )

    output = generate(
        prompt,
        max_new_tokens=80,
        temperature=0.7,
        top_k=40
    )

    # ========================================================
    # EXTRACT ONLY NEW ASSISTANT RESPONSE
    # ========================================================

    if "<|assistant|>" in output:

        response = output.split(
            "<|assistant|>",
            1
        )[1]

    else:

        response = output

    # Stop at next user turn
    if "<|user|>" in response:

        response = response.split(
            "<|user|>",
            1
        )[0]

    # Remove accidental "You:" prefix
    if response.strip().lower().startswith("you:"):

        response = response.strip()[4:].strip()

    response = response.strip()

    print("\nNanoGPT:", response)
    print()