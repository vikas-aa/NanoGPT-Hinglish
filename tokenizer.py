text = "hello world"

# 1. Vocabulary create karo
chars = sorted(list(set(text)))

# 2. Character -> Integer
stoi = {ch: i for i, ch in enumerate(chars)}

# 3. Integer -> Character
itos = {i: ch for i, ch in enumerate(chars)}

print("Characters:", chars)
print("Vocabulary size:", len(chars))
print("stoi:", stoi)
print("itos:", itos)


# 4. Encoder
def encode(text):
    return [stoi[ch] for ch in text]


# 5. Decoder
def decode(numbers):
    return ''.join(itos[i] for i in numbers)


# Test
encoded = encode("hello")

print("Encoded:", encoded)
print("Decoded:", decode(encoded))