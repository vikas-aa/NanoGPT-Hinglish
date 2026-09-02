import os
import time
import math
import numpy as np
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

TOKENIZER_FILE = "data/tokenizer.json"

tokenizer = Tokenizer.from_file(TOKENIZER_FILE)

vocab_size = tokenizer.get_vocab_size()


# ============================================================
# CONFIG
# ============================================================

config = GPTConfig()

# Automatically match tokenizer
config.vocab_size = vocab_size

# Training settings
batch_size = 8

learning_rate = 3e-4
min_learning_rate = 3e-5

max_iters = 10000

warmup_iters = 500

eval_interval = 500
eval_iters = 20

grad_clip = 1.0

weight_decay = 0.1


print("\nModel configuration:")
print("Vocabulary size:", config.vocab_size)
print("Block size:", config.block_size)
print("Embedding size:", config.n_embd)
print("Attention heads:", config.n_head)
print("Transformer layers:", config.n_layer)
print("Batch size:", batch_size)
print("Initial learning rate:", learning_rate)
print("Minimum learning rate:", min_learning_rate)
print("Warmup iterations:", warmup_iters)
print("Max iterations:", max_iters)
print("Weight decay:", weight_decay)
print("Gradient clipping:", grad_clip)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading training data...")

train_data = torch.from_numpy(
    np.fromfile(
        "data/train.bin",
        dtype=np.uint16
    )
).long()

val_data = torch.from_numpy(
    np.fromfile(
        "data/val.bin",
        dtype=np.uint16
    )
).long()


print("Training tokens:", len(train_data))
print("Validation tokens:", len(val_data))


# ============================================================
# BATCH FUNCTION
# ============================================================

def get_batch(data):

    ix = torch.randint(
        0,
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
    lr=learning_rate,
    weight_decay=weight_decay
)


# ============================================================
# LEARNING RATE SCHEDULE
# ============================================================

def get_lr(iteration):

    # Warmup
    if iteration < warmup_iters:

        return learning_rate * (
            iteration + 1
        ) / warmup_iters

    # After warmup
    if iteration >= max_iters:

        return min_learning_rate

    # Cosine decay
    decay_ratio = (
        iteration - warmup_iters
    ) / (
        max_iters - warmup_iters
    )

    coeff = 0.5 * (
        1.0 + math.cos(
            math.pi * decay_ratio
        )
    )

    return (
        min_learning_rate
        + coeff * (
            learning_rate
            - min_learning_rate
        )
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

        losses = torch.zeros(
            eval_iters
        )

        for k in range(eval_iters):

            X, Y = get_batch(data)

            _, loss = model(X, Y)

            losses[k] = loss.item()

        results[name] = losses.mean().item()

    model.train()

    return results


# ============================================================
# CHECKPOINT DIRECTORY
# ============================================================

os.makedirs(
    "checkpoints",
    exist_ok=True
)

best_checkpoint_path = (
    "checkpoints/best_nanogpt.pt"
)

latest_checkpoint_path = (
    "checkpoints/nanogpt.pt"
)


# ============================================================
# TRAINING
# ============================================================

print("\nStarting training...\n")

start_time = time.time()

best_val_loss = float("inf")


for iteration in range(max_iters):


    # --------------------------------------------------------
    # Learning rate
    # --------------------------------------------------------

    current_lr = get_lr(iteration)

    for param_group in optimizer.param_groups:

        param_group["lr"] = current_lr


    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    if iteration % eval_interval == 0:

        losses = estimate_loss()

        elapsed = time.time() - start_time

        print(
            f"step {iteration:5d} | "
            f"lr {current_lr:.6f} | "
            f"train loss {losses['train']:.4f} | "
            f"val loss {losses['val']:.4f} | "
            f"time {elapsed:.1f}s"
        )


        # ----------------------------------------------------
        # Save best model
        # ----------------------------------------------------

        if losses["val"] < best_val_loss:

            best_val_loss = losses["val"]

            torch.save(
                {
                    "model_state_dict":
                        model.state_dict(),

                    "optimizer_state_dict":
                        optimizer.state_dict(),

                    "iteration":
                        iteration,

                    "best_val_loss":
                        best_val_loss,

                    "config": {
                        "vocab_size":
                            config.vocab_size,

                        "block_size":
                            config.block_size,

                        "n_embd":
                            config.n_embd,

                        "n_head":
                            config.n_head,

                        "n_layer":
                            config.n_layer,

                        "dropout":
                            config.dropout
                    }
                },
                best_checkpoint_path
            )

            print(
                f"Best checkpoint saved "
                f"(val loss: {best_val_loss:.4f})"
            )


    # --------------------------------------------------------
    # Get batch
    # --------------------------------------------------------

    X, Y = get_batch(train_data)


    # --------------------------------------------------------
    # Forward
    # --------------------------------------------------------

    logits, loss = model(X, Y)


    # --------------------------------------------------------
    # Backward
    # --------------------------------------------------------

    optimizer.zero_grad(
        set_to_none=True
    )

    loss.backward()


    # --------------------------------------------------------
    # Gradient clipping
    # --------------------------------------------------------

    torch.nn.utils.clip_grad_norm_(
        model.parameters(),
        grad_clip
    )


    # --------------------------------------------------------
    # Optimizer step
    # --------------------------------------------------------

    optimizer.step()


# ============================================================
# SAVE FINAL CHECKPOINT
# ============================================================

torch.save(
    {
        "model_state_dict":
            model.state_dict(),

        "optimizer_state_dict":
            optimizer.state_dict(),

        "iteration":
            max_iters,

        "best_val_loss":
            best_val_loss,

        "config": {
            "vocab_size":
                config.vocab_size,

            "block_size":
                config.block_size,

            "n_embd":
                config.n_embd,

            "n_head":
                config.n_head,

            "n_layer":
                config.n_layer,

            "dropout":
                config.dropout
        }
    },
    latest_checkpoint_path
)


# ============================================================
# COMPLETE
# ============================================================

elapsed = time.time() - start_time

print("\n" + "=" * 60)
print("TRAINING COMPLETE")
print("=" * 60)

print(
    "Final checkpoint:",
    latest_checkpoint_path
)

print(
    "Best checkpoint:",
    best_checkpoint_path
)

print(
    "Best validation loss:",
    best_val_loss
)

print(
    "Total training time:",
    round(elapsed / 60, 2),
    "minutes"
)

print("=" * 60)