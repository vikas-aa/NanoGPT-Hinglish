import tiktoken

# GPT-2 tokenizer load karo
enc = tiktoken.get_encoding("gpt2")

texts = [
    "Hello, how are you?",
    "नमस्ते, आप कैसे हैं?",
    "Aaj main Python seekh raha hoon.",
    "<|user|>\nHi\n<|assistant|>\nHello! How are you?"
]

for text in texts:
    tokens = enc.encode(text)

    print("\nText:")
    print(text)

    print("Tokens:")
    print(tokens)

    print("Number of tokens:", len(tokens))

    print("Decoded:")
    print(enc.decode(tokens))