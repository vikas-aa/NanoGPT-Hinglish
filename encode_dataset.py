from tokenizers import Tokenizer
import numpy as np
import os

TEXT_FILE = "data/final_train_clean.txt"
TOKENIZER_FILE = "data/tokenizer.json"

TRAIN_FILE = "data/train.bin"
VAL_FILE = "data/val.bin"

print("Loading tokenizer...")

tokenizer = Tokenizer.from_file(TOKENIZER_FILE)

print("Tokenizer loaded.")
print("Vocabulary size:", tokenizer.get_vocab_size())

print("\nReading dataset...")

with open(TEXT_FILE, "r", encoding="utf-8") as f:
    text = f.read()

print("Characters:", len(text))

print("\nEncoding dataset...")

encoded = tokenizer.encode(text)

tokens = np.array(encoded.ids, dtype=np.uint16)

print("Total tokens:", len(tokens))

# 90% train / 10% validation
split = int(len(tokens) * 0.90)

train_tokens = tokens[:split]
val_tokens = tokens[split:]

# Save binary files
train_tokens.tofile(TRAIN_FILE)
val_tokens.tofile(VAL_FILE)

print("\nDataset encoded successfully!")

print("Training tokens:", len(train_tokens))
print("Validation tokens:", len(val_tokens))

print(
    "Train file size:",
    round(os.path.getsize(TRAIN_FILE) / (1024 * 1024), 2),
    "MB"
)

print(
    "Validation file size:",
    round(os.path.getsize(VAL_FILE) / (1024 * 1024), 2),
    "MB"
)

print("\nFirst 50 token IDs:")
print(train_tokens[:50].tolist())

print("\nDecoded preview:")
print(tokenizer.decode(train_tokens[:50].tolist()))