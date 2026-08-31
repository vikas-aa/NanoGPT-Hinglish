from pathlib import Path
import re

HINGLISH_FILE = Path("data/chat_train_hinglish.txt")
INSTRUCTION_FILE = Path("data/chat_instruction.txt")
OUTPUT_FILE = Path("data/final_train.txt")


def contains_devanagari(text):
    """
    True if text contains any Devanagari character.
    """
    return bool(re.search(r"[\u0900-\u097F]", text))


def clean_and_filter(text):
    """
    Remove examples containing Devanagari characters.
    Keep only examples written in Latin/English/Hinglish.
    """

    blocks = re.split(r"\n\s*\n", text)

    kept = []
    removed = 0

    for block in blocks:

        block = block.strip()

        if not block:
            continue

        if contains_devanagari(block):
            removed += 1
            continue

        kept.append(block)

    return kept, removed


print("=" * 60)
print("CREATING CLEAN HINGLISH DATASET")
print("=" * 60)

all_blocks = []

for file in [HINGLISH_FILE, INSTRUCTION_FILE]:

    print(f"\nReading: {file}")

    if not file.exists():
        print("ERROR: File not found!")
        continue

    text = file.read_text(encoding="utf-8")

    print("Characters:", len(text))

    blocks, removed = clean_and_filter(text)

    print("Kept blocks:", len(blocks))
    print("Removed Devanagari blocks:", removed)

    all_blocks.extend(blocks)


# Remove exact duplicate examples
unique_blocks = list(dict.fromkeys(all_blocks))


# Save final dataset
OUTPUT_FILE.write_text(
    "\n\n".join(unique_blocks) + "\n",
    encoding="utf-8"
)


print("\n" + "=" * 60)
print("FINAL DATASET CREATED")
print("=" * 60)

print("Total blocks before duplicates:", len(all_blocks))
print("Unique blocks:", len(unique_blocks))
print("Output:", OUTPUT_FILE)
print(
    "Size:",
    round(OUTPUT_FILE.stat().st_size / 1024, 2),
    "KB"
)


# Final safety check
final_text = OUTPUT_FILE.read_text(encoding="utf-8")

if contains_devanagari(final_text):
    print("\nWARNING: Devanagari text still exists!")
else:
    print("\nSUCCESS: No Devanagari characters found!")


print("\nFirst 1000 characters:")
print("-" * 60)
print(final_text[:1000])
print("-" * 60)