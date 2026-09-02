from pathlib import Path

INPUT = Path("data/final_train_no_blanks.txt")
OUTPUT = Path("data/final_train_clean.txt")
REPORT = Path("data/cleaning_report.txt")

USER = "<|user|>"
ASSISTANT = "<|assistant|>"

text = INPUT.read_text(encoding="utf-8")

# ---------------------------------------------------------
# Extract every USER -> ASSISTANT section independently.
# This fixes cases where several examples were accidentally
# concatenated into one block.
# ---------------------------------------------------------

parts = text.split(USER)

examples = []

for part in parts[1:]:
    if ASSISTANT not in part:
        continue

    # Everything before the first assistant marker = user
    user, rest = part.split(ASSISTANT, 1)

    user = user.strip()
    rest = rest.strip()

    if not user or not rest:
        continue

    # If another USER marker occurs before the next clean
    # boundary, keep only the first conversation.
    if USER in user:
        user = user.split(USER, 1)[0].strip()

    # If another ASSISTANT marker exists, take only the
    # first assistant answer.
    if ASSISTANT in rest:
        rest = rest.split(ASSISTANT, 1)[0].strip()

    assistant = rest

    if not assistant:
        continue

    examples.append((user, assistant))


# ---------------------------------------------------------
# Remove exact duplicate pairs
# ---------------------------------------------------------

unique_examples = []
seen = set()

duplicates = 0

for user, assistant in examples:
    key = (user, assistant)

    if key in seen:
        duplicates += 1
        continue

    seen.add(key)
    unique_examples.append((user, assistant))


# ---------------------------------------------------------
# Basic quality filtering
# ---------------------------------------------------------

clean_examples = []
removed_short = 0
removed_markers = 0

for user, assistant in unique_examples:

    # Too short to be useful
    if len(user.strip()) < 2 or len(assistant.strip()) < 2:
        removed_short += 1
        continue

    # Broken role markers
    if USER in assistant or ASSISTANT in assistant:
        removed_markers += 1
        continue

    if USER in user:
        removed_markers += 1
        continue

    clean_examples.append((user, assistant))


# ---------------------------------------------------------
# Write clean dataset
# ---------------------------------------------------------

with OUTPUT.open("w", encoding="utf-8", newline="\n") as f:

    for user, assistant in clean_examples:

        f.write(USER + "\n")
        f.write(user + "\n")
        f.write(ASSISTANT + "\n")
        f.write(assistant + "\n")


# ---------------------------------------------------------
# Report
# ---------------------------------------------------------

report = f"""
======================================================================
NANOGPT DATASET CLEANING REPORT
======================================================================

Input file:
{INPUT}

Output file:
{OUTPUT}

----------------------------------------------------------------------
COUNTS
----------------------------------------------------------------------

Extracted conversation pairs : {len(examples)}
Duplicate pairs removed      : {duplicates}
Short examples removed       : {removed_short}
Broken marker examples       : {removed_markers}

Final clean examples         : {len(clean_examples)}

----------------------------------------------------------------------
IMPORTANT
----------------------------------------------------------------------

Original files were NOT modified.

The cleaner:
- removed duplicate pairs
- removed empty/very short pairs
- removed broken role-marker examples
- separated examples around role markers
- preserved the original user/assistant text
- did NOT generate new answers
- did NOT rewrite the dataset

======================================================================
"""

REPORT.write_text(report.strip() + "\n", encoding="utf-8")

print("=" * 70)
print("DATASET CLEANING COMPLETE")
print("=" * 70)
print(f"Extracted pairs       : {len(examples)}")
print(f"Duplicates removed    : {duplicates}")
print(f"Short removed         : {removed_short}")
print(f"Bad marker removed    : {removed_markers}")
print(f"Final clean examples  : {len(clean_examples)}")
print()
print(f"Clean dataset:")
print(OUTPUT)
print()
print(f"Report:")
print(REPORT)
print("=" * 70)