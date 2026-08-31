from datasets import load_dataset
import re

DATASET_NAME = "ankitdhiman/hinglish-conversations"

print("Loading dataset...")
dataset = load_dataset(DATASET_NAME)

data = dataset["train"]

print(f"\nTotal examples: {len(data)}")

empty = 0
duplicates = 0
suspicious = 0
very_long = 0
urls = 0

seen = set()

# Patterns we want to inspect
suspicious_patterns = [
    r"<script",
    r"javascript:",
    r"powershell",
    r"cmd\.exe",
    r"base64",
    r"eval\(",
    r"subprocess",
    r"os\.system",
    r"wget\s+",
    r"curl\s+",
]

print("\nScanning dataset...\n")

for i, row in enumerate(data):

    user = str(row.get("user_message", ""))
    assistant = str(row.get("assistant_message", ""))

    # Empty records
    if not user.strip() or not assistant.strip():
        empty += 1

    # Duplicate conversation pair
    pair = (user.strip(), assistant.strip())

    if pair in seen:
        duplicates += 1
    else:
        seen.add(pair)

    combined = user + "\n" + assistant

    # URLs
    if re.search(r"https?://|www\.", combined, re.IGNORECASE):
        urls += 1

    # Very long examples
    if len(combined) > 5000:
        very_long += 1

    # Suspicious patterns
    for pattern in suspicious_patterns:
        if re.search(pattern, combined, re.IGNORECASE):
            suspicious += 1
            print("\nPossible suspicious example:")
            print("Index:", i)
            print("User:", user[:500])
            print("Assistant:", assistant[:500])
            print("-" * 60)
            break

    # Progress
    if (i + 1) % 20000 == 0:
        print(f"Scanned: {i + 1}/{len(data)}")

print("\n" + "=" * 50)
print("SCAN COMPLETE")
print("=" * 50)

print("Total examples      :", len(data))
print("Empty examples      :", empty)
print("Duplicate pairs     :", duplicates)
print("Examples with URLs  :", urls)
print("Very long examples  :", very_long)
print("Suspicious matches  :", suspicious)
print("=" * 50)