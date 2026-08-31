from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import ByteLevel
from tokenizers.decoders import ByteLevel as ByteLevelDecoder

# Files
input_file = "data/final_train.txt"
output_file = "data/tokenizer.json"

# BPE tokenizer
tokenizer = Tokenizer(BPE(unk_token="<|unk|>"))

# Byte-level preprocessing
tokenizer.pre_tokenizer = ByteLevel(add_prefix_space=False)
tokenizer.decoder = ByteLevelDecoder()

# Special tokens
special_tokens = [
    "<|unk|>",
    "<|pad|>",
    "<|user|>",
    "<|assistant|>",
]

# Trainer
trainer = BpeTrainer(
    vocab_size=8000,
    min_frequency=2,
    special_tokens=special_tokens,
)

print("Training tokenizer...")
print("Dataset:", input_file)

# Train
tokenizer.train([input_file], trainer)

# Save
tokenizer.save(output_file)

print("\nTokenizer trained successfully!")
print("Vocabulary size:", tokenizer.get_vocab_size())
print("Saved to:", output_file)

# Test
test_texts = [
    "Hello, how are you?",
    "नमस्ते, आप कैसे हैं?",
    "Aaj main Python seekh raha hoon.",
    "<|user|>\nHi\n<|assistant|>\nHello! How are you?"
]

print("\n--- Tokenizer Test ---")

for text in test_texts:
    encoded = tokenizer.encode(text)

    print("\nText:", text)
    print("Tokens:", encoded.tokens)
    print("IDs:", encoded.ids)
    print("Token count:", len(encoded.ids))
    print("Decoded:", tokenizer.decode(encoded.ids))