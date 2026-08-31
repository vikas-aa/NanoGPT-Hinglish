from datasets import load_dataset
from pathlib import Path
import re

DATASET_NAME = "ankitdhiman/hinglish-conversations"
OUTPUT_FILE = "data/chat_train_hinglish.txt"

print("Loading dataset...")
dataset = load_dataset(DATASET_NAME)

data = dataset["train"]

print("Total examples:", len(data))

def has_devanagari(text):
    if not text:
        return False

    # Hindi/Devanagari Unicode range
    return bool(re.search(r"[\u0900-\u097F]", text))

def clean_text(text):
    if not text:
        return ""

    text = text.strip()
    text = re.sub(r"\s+", " ", text)

    return text

output = []
removed = 0
duplicates = set()

print("\nFiltering dataset...")

for item in data:

    user = clean_text(item["user_message"])
    assistant = clean_text(item["assistant_message"])

    # Empty examples
    if not user or not assistant:
        removed += 1
        continue

    # Remove Devanagari Hindi
    if has_devanagari(user) or has_devanagari(assistant):
        removed += 1
        continue

    pair = (user, assistant)

    # Remove duplicate pairs
    if pair in duplicates:
        removed += 1
        continue

    duplicates.add(pair)

    output.append(
        "<|user|>\n"
        + user
        + "\n"
        + "<|assistant|>\n"
        + assistant
        + "\n\n"
    )

Path("data").mkdir(exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("".join(output))

print("\n========================================")
print("FILTER COMPLETE")
print("========================================")
print("Original examples :", len(data))
print("Kept examples     :", len(output))
print("Removed examples  :", removed)
print("Output file       :", OUTPUT_FILE)
print("========================================")

# Show samples
print("\n--- Samples ---")

for sample in output[:5]:
    print(sample)