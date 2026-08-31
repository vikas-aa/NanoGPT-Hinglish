import os
import time
import numpy as np
import torch

from model import NanoGPT, GPTConfig


# ============================================================
# DEVICE
# ============================================================

device = "cuda" if torch.cuda.is_available() else "cpu"

print("Device:", device)


# ============================================================
# CONFIG
# ============================================================

config = GPTConfig()

batch_size = 8
learning_rate = 3e-4

max_iters = 5000

eval_interval = 500
eval_iters = 20

print("\nModel configuration:")
print("Vocabulary size:", config.vocab_size)
print("Block size:", config.block_size)
print("Embedding size:", config.n_embd)
print("Attention heads:", config.n_head)
print("Transformer layers:", config.n_layer)
print("Batch size:", batch_size)
print("Learning rate:", learning_rate)
print("Max iterations:", max_iters)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading training data...")

train_data = torch.from_numpy(
    np.fromfile("data/train.bin", dtype=np.uint16)
).long()

val_data = torch.from_numpy(
    np.fromfile("data/val.bin", dtype=np.uint16)
).long()

print("Training tokens:", len(train_data))
print("Validation tokens:", len(val_data))

# ============================================================
# BATCH FUNCTION
# ============================================================

def get_batch(data):

    ix = torch.randint(
        len(data) - config.block_size - 1,
        (batch_size,)
    )

    x = torch.stack(
        [
            data[i:i + config.block_size]
            for i in ix
        ]
    )

    y = torch.stack(
        [
            data[i + 1:i + config.block_size + 1]
            for i in ix
        ]
    )

    return x.to(device), y.to(device)


# ============================================================
# MODEL
# ============================================================

print("\nCreating model...")

model = NanoGPT(config).to(device)

parameters = sum(
    p.numel()
    for p in model.parameters()
)

print("Parameters:", f"{parameters:,}")


# ============================================================
# OPTIMIZER
# ============================================================

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=learning_rate
)


# ============================================================
# EVALUATION
# ============================================================

@torch.no_grad()
def estimate_loss():

    model.eval()

    results = {}

    for name, data in [
        ("train", train_data),
        ("val", val_data)
    ]:

        losses = torch.zeros(eval_iters)

        for k in range(eval_iters):

            X, Y = get_batch(data)

            _, loss = model(X, Y)

            losses[k] = loss.item()

        results[name] = losses.mean().item()

    model.train()

    return results


# ============================================================
# TRAINING
# ============================================================

print("\nStarting training...\n")

start_time = time.time()

for iteration in range(max_iters):

    # Evaluation
    if iteration % eval_interval == 0:

        losses = estimate_loss()

        elapsed = time.time() - start_time

        print(
            f"step {iteration:4d} | "
            f"train loss {losses['train']:.4f} | "
            f"val loss {losses['val']:.4f} | "
            f"time {elapsed:.1f}s"
        )

    # Get batch
    X, Y = get_batch(train_data)

    # Forward
    logits, loss = model(X, Y)

    # Clear gradients
    optimizer.zero_grad(set_to_none=True)

    # Backpropagation
    loss.backward()

    # Update weights
    optimizer.step()


# ============================================================
# SAVE CHECKPOINT
# ============================================================

os.makedirs("checkpoints", exist_ok=True)

checkpoint_path = "checkpoints/nanogpt.pt"

torch.save(
    {
        "model_state_dict": model.state_dict(),
        "config": {
            "vocab_size": config.vocab_size,
            "block_size": config.block_size,
            "n_embd": config.n_embd,
            "n_head": config.n_head,
            "n_layer": config.n_layer,
            "dropout": config.dropout
        }
    },
    checkpoint_path
)

print("\nTraining complete!")

print(
    "Checkpoint saved to:",
    checkpoint_path
)