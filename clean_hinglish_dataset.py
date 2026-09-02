from datasets import load_dataset
from pathlib import Path
import re

# ============================================================
# CONFIG
# ============================================================

DATASET_NAME = "theguywithblacktie/hinglish-conversations"
OUTPUT_FILE = "data/large_hinglish_clean.txt"

MAX_LENGTH = 5000

# ============================================================
# FUNCTIONS
# ============================================================

def has_devanagari(text):
    return bool(re.search(r"[\u0900-\u097F]", text))


def has_url(text):
    return bool(
        re.search(
            r"https?://|www\.",
            text,
            re.IGNORECASE
        )
    )


def extract_content(value):
    """
    Dataset format:
    [{'role': 'user', 'content': '...'}]
    """

    if not isinstance(value, list):
        return ""

    parts = []

    for item in value:

        if not isinstance(item, dict):
            continue

        content = item.get("content", "")

        if content:
            parts.append(str(content).strip())

    return "\n".join(parts).strip()


# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 60)
print("CLEANING HINGLISH DATASET")
print("=" * 60)

print("\nLoading dataset...")

dataset = load_dataset(
    DATASET_NAME,
    "large"
)

data = dataset["train"]

print("Total examples:", len(data))


# ============================================================
# COUNTERS
# ============================================================

kept = 0
removed_empty = 0
removed_duplicate = 0
removed_url = 0
removed_long = 0

seen = set()

output_blocks = []


# ============================================================
# PROCESS
# ============================================================

print("\nProcessing dataset...\n")

for i, row in enumerate(data):

    user = extract_content(
        row.get("input", [])
    )

    assistant = extract_content(
        row.get("output", [])
    )

    # Empty
    if not user or not assistant:
        removed_empty += 1
        continue

    combined = user + "\n" + assistant

    # Very long
    if len(combined) > MAX_LENGTH:
        removed_long += 1
        continue

    # URLs
    if has_url(combined):
        removed_url += 1
        continue

    # Duplicate
    pair = (
        user.strip(),
        assistant.strip()
    )

    if pair in seen:
        removed_duplicate += 1
        continue

    seen.add(pair)

    # ========================================================
    # CHAT FORMAT
    # ========================================================

    block = (
        "<|user|>\n"
        + user.strip()
        + "\n"
        + "<|assistant|>\n"
        + assistant.strip()
        + "\n"
    )

    output_blocks.append(block)

    kept += 1

    # Progress
    if (i + 1) % 20000 == 0:
        print(
            f"Processed: {i + 1}/{len(data)} | "
            f"Kept: {kept}"
        )


# ============================================================
# SAVE
# ============================================================

Path("data").mkdir(
    exist_ok=True
)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    f.write("\n".join(output_blocks))


# ============================================================
# RESULT
# ============================================================

print("\n" + "=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)

print("Original examples :", len(data))
print("Kept examples     :", kept)
print("Empty removed     :", removed_empty)
print("Duplicates removed:", removed_duplicate)
print("URLs removed      :", removed_url)
print("Long removed      :", removed_long)

print("\nOutput:")
print(OUTPUT_FILE)

size_kb = Path(
    OUTPUT_FILE
).stat().st_size / 1024

print(
    "File size         :",
    round(size_kb, 2),
    "KB"
)

print("=" * 60)

print("\nFirst example:")
print("-" * 60)

if output_blocks:
    print(output_blocks[0])

print("-" * 60)