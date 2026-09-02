from pathlib import Path
import re

# ============================================================
# FILES
# ============================================================

OLD_HINGLISH_FILE = Path("data/chat_train_hinglish.txt")
INSTRUCTION_FILE = Path("data/chat_instruction.txt")
LARGE_FILE = Path("data/large_hinglish_clean.txt")

OUTPUT_FILE = Path("data/final_train.txt")


# ============================================================
# HELPERS
# ============================================================

def contains_devanagari(text):
    return bool(
        re.search(r"[\u0900-\u097F]", text)
    )


def split_blocks(text):
    """
    Split dataset into individual chat examples.
    """

    blocks = re.split(
        r"\n\s*\n",
        text
    )

    return [
        block.strip()
        for block in blocks
        if block.strip()
    ]


def read_dataset(path):
    if not path.exists():
        print(f"WARNING: {path} not found!")
        return []

    print(f"\nReading: {path}")

    text = path.read_text(
        encoding="utf-8"
    )

    print(
        "Characters:",
        len(text)
    )

    blocks = split_blocks(text)

    print(
        "Blocks:",
        len(blocks)
    )

    return blocks


# ============================================================
# START
# ============================================================

print("=" * 60)
print("CREATING LARGE HINGLISH DATASET")
print("=" * 60)


all_blocks = []


# ============================================================
# OLD CLEAN DATA
# ============================================================

for path in [
    OLD_HINGLISH_FILE,
    INSTRUCTION_FILE,
    LARGE_FILE
]:

    blocks = read_dataset(path)

    all_blocks.extend(blocks)


print("\n" + "=" * 60)

print(
    "Total blocks before duplicates:",
    len(all_blocks)
)


# ============================================================
# REMOVE DUPLICATES
# ============================================================

unique_blocks = list(
    dict.fromkeys(all_blocks)
)


print(
    "Unique blocks:",
    len(unique_blocks)
)


# ============================================================
# FINAL DEVANAGARI CHECK
# ============================================================

devanagari_count = 0

for block in unique_blocks:

    if contains_devanagari(block):
        devanagari_count += 1


print(
    "Blocks containing Devanagari:",
    devanagari_count
)


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.write_text(
    "\n\n".join(unique_blocks) + "\n",
    encoding="utf-8"
)


# ============================================================
# RESULT
# ============================================================

print("\n" + "=" * 60)
print("FINAL DATASET CREATED")
print("=" * 60)

print(
    "Output:",
    OUTPUT_FILE
)

print(
    "Total unique blocks:",
    len(unique_blocks)
)

print(
    "Characters:",
    len(
        OUTPUT_FILE.read_text(
            encoding="utf-8"
        )
    )
)

print(
    "Size:",
    round(
        OUTPUT_FILE.stat().st_size
        / (1024 * 1024),
        2
    ),
    "MB"
)

print(
    "Devanagari blocks:",
    devanagari_count
)


# ============================================================
# PREVIEW
# ============================================================

print("\nFirst 1000 characters:")
print("-" * 60)

final_text = OUTPUT_FILE.read_text(
    encoding="utf-8"
)

print(
    final_text[:1000]
)

print("-" * 60)

print("\nSUCCESS!")