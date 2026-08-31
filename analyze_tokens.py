import tiktoken
import os

enc = tiktoken.get_encoding("gpt2")

file_path = "data/chat_train.txt"

print("Reading dataset...")

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

print("Characters:", len(text))
print("File size:", round(os.path.getsize(file_path) / (1024 * 1024), 2), "MB")

print("Tokenizing...")

tokens = enc.encode(text)

print("Total tokens:", len(tokens))

print("First 50 tokens:")
print(tokens[:50])

print("\nDecoded:")
print(enc.decode(tokens[:50]))