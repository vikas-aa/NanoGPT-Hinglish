from pathlib import Path
from collections import Counter

INPUT_FILE = Path("data/final_train_clean.txt")
REPORT_FILE = Path("data/dataset_check_report.txt")

USER_TAG = "<|user|>"
ASSISTANT_TAG = "<|assistant|>"

print("=" * 70)
print("NanoGPT Dataset Validator")
print("=" * 70)

if not INPUT_FILE.exists():
    print(f"ERROR: File not found: {INPUT_FILE}")
    raise SystemExit(1)

print(f"Input: {INPUT_FILE}")
print("Reading dataset...")

text = INPUT_FILE.read_text(encoding="utf-8")

# Split according to user marker
raw_blocks = text.split(USER_TAG)

total = 0
valid = 0
missing_assistant = 0
empty_user = 0
empty_assistant = 0
multiple_user = 0
multiple_assistant = 0
duplicates = 0
suspicious = 0

seen = set()

lengths = []
suspicious_examples = []
invalid_examples = []

for block in raw_blocks[1:]:
    total += 1

    # Count role markers inside the block
    user_count = block.count(USER_TAG)
    assistant_count = block.count(ASSISTANT_TAG)

    if user_count > 0:
        multiple_user += 1

    if assistant_count == 0:
        missing_assistant += 1
        invalid_examples.append(
            f"[Missing assistant]\n{block[:500]}\n{'-' * 50}"
        )
        continue

    if assistant_count > 1:
        multiple_assistant += 1

    user_part, assistant_part = block.split(ASSISTANT_TAG, 1)

    user = user_part.strip()
    assistant = assistant_part.strip()

    if not user:
        empty_user += 1
        invalid_examples.append(
            f"[Empty user]\n{block[:500]}\n{'-' * 50}"
        )
        continue

    if not assistant:
        empty_assistant += 1
        invalid_examples.append(
            f"[Empty assistant]\n{block[:500]}\n{'-' * 50}"
        )
        continue

    key = (user, assistant)

    if key in seen:
        duplicates += 1
        continue

    seen.add(key)

    # Basic suspicious-content checks.
    # These DO NOT delete anything.
    suspicious_reasons = []

    if len(user) < 2:
        suspicious_reasons.append("very short user")

    if len(assistant) < 2:
        suspicious_reasons.append("very short assistant")

    if assistant.count("<|user|>") > 0:
        suspicious_reasons.append("user marker inside assistant")

    if assistant.count("<|assistant|>") > 0:
        suspicious_reasons.append("assistant marker inside assistant")

    if user.count("<|assistant|>") > 0:
        suspicious_reasons.append("assistant marker inside user")

    if "\x00" in user or "\x00" in assistant:
        suspicious_reasons.append("NULL character")

    if suspicious_reasons:
        suspicious += 1

        suspicious_examples.append(
            f"REASONS: {', '.join(suspicious_reasons)}\n"
            f"USER:\n{user[:1000]}\n"
            f"ASSISTANT:\n{assistant[:1000]}\n"
            + "-" * 70
        )

    valid += 1
    lengths.append((len(user), len(assistant)))


# Length statistics
if lengths:
    user_lengths = [x[0] for x in lengths]
    assistant_lengths = [x[1] for x in lengths]

    avg_user = sum(user_lengths) / len(user_lengths)
    avg_assistant = sum(assistant_lengths) / len(assistant_lengths)

    max_user = max(user_lengths)
    max_assistant = max(assistant_lengths)

    min_user = min(user_lengths)
    min_assistant = min(assistant_lengths)
else:
    avg_user = avg_assistant = 0
    max_user = max_assistant = 0
    min_user = min_assistant = 0


report = []

report.append("=" * 70)
report.append("NANOGPT DATASET CHECK REPORT")
report.append("=" * 70)
report.append("")
report.append(f"Input file                 : {INPUT_FILE}")
report.append(f"File size (bytes)          : {INPUT_FILE.stat().st_size}")
report.append("")
report.append(f"Total detected examples   : {total}")
report.append(f"Valid examples             : {valid}")
report.append(f"Missing assistant marker   : {missing_assistant}")
report.append(f"Empty user                 : {empty_user}")
report.append(f"Empty assistant            : {empty_assistant}")
report.append(f"Multiple user markers     : {multiple_user}")
report.append(f"Multiple assistant markers: {multiple_assistant}")
report.append(f"Duplicate examples         : {duplicates}")
report.append(f"Suspicious examples        : {suspicious}")
report.append("")
report.append("-" * 70)
report.append("LENGTH STATISTICS")
report.append("-" * 70)
report.append(f"Average user chars         : {avg_user:.2f}")
report.append(f"Average assistant chars    : {avg_assistant:.2f}")
report.append(f"Minimum user chars         : {min_user}")
report.append(f"Maximum user chars         : {max_user}")
report.append(f"Minimum assistant chars    : {min_assistant}")
report.append(f"Maximum assistant chars    : {max_assistant}")
report.append("")
report.append("-" * 70)
report.append("IMPORTANT")
report.append("-" * 70)
report.append(
    "This script ONLY analyzes the dataset. "
    "It does not modify or delete any examples."
)
report.append("")


if invalid_examples:
    report.append("=" * 70)
    report.append("INVALID EXAMPLE SAMPLES")
    report.append("=" * 70)

    for item in invalid_examples[:50]:
        report.append(item)

if suspicious_examples:
    report.append("")
    report.append("=" * 70)
    report.append("SUSPICIOUS EXAMPLE SAMPLES")
    report.append("=" * 70)

    for item in suspicious_examples[:100]:
        report.append(item)


REPORT_FILE.write_text(
    "\n".join(report),
    encoding="utf-8"
)


print()
print("=" * 70)
print("RESULT")
print("=" * 70)
print(f"Total examples            : {total}")
print(f"Valid examples            : {valid}")
print(f"Missing assistant         : {missing_assistant}")
print(f"Empty user                : {empty_user}")
print(f"Empty assistant           : {empty_assistant}")
print(f"Multiple user markers     : {multiple_user}")
print(f"Multiple assistant markers: {multiple_assistant}")
print(f"Duplicates                : {duplicates}")
print(f"Suspicious                : {suspicious}")
print()
print(f"Report saved to:")
print(REPORT_FILE)
print("=" * 70)