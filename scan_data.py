from datasets import load_dataset
import re

DATASET_NAME = "theguywithblacktie/hinglish-conversations"
SUBSET = "large"

print("=" * 60)
print("SCANNING HINGLISH DATASET")
print("=" * 60)

print("\nLoading dataset...")

dataset = load_dataset(
    DATASET_NAME,
    SUBSET
)

data = dataset["train"]

print("\nDataset loaded successfully!")
print("Total examples:", len(data))
print("Columns:", data.column_names)

# ============================================================
# COUNTERS
# ============================================================

empty = 0
duplicates = 0
urls = 0
very_long = 0
suspicious = 0
devanagari = 0
malformed = 0

seen = set()

# ============================================================
# PATTERNS
# ============================================================

suspicious_patterns = [
    r"<script",
    r"javascript:",
    r"powershell",
    r"\bcmd\.exe\b",
    r"\bbase64\b",
    r"\beval\s*\(",
    r"\bsubprocess\b",
    r"\bos\.system\b",
    r"\bwget\s+",
    r"\bcurl\s+",
]

url_pattern = re.compile(
    r"https?://|www\.",
    re.IGNORECASE
)

# Devanagari Unicode range
devanagari_pattern = re.compile(
    r"[\u0900-\u097F]"
)

# ============================================================
# HELPER
# ============================================================

def extract_content(messages):

    if not isinstance(messages, list):
        return ""

    parts = []

    for message in messages:

        if not isinstance(message, dict):
            continue

        content = message.get("content", "")

        if content is None:
            continue

        parts.append(str(content))

    return "\n".join(parts)


# ============================================================
# SCAN
# ============================================================

print("\nScanning dataset...\n")

for i, row in enumerate(data):

    input_messages = row.get("input", [])
    output_messages = row.get("output", [])

    user_text = extract_content(input_messages)
    assistant_text = extract_content(output_messages)

    # --------------------------------------------------------
    # Malformed
    # --------------------------------------------------------

    if not user_text.strip() or not assistant_text.strip():

        empty += 1
        continue

    # --------------------------------------------------------
    # Combined text
    # --------------------------------------------------------

    combined = (
        user_text
        + "\n"
        + assistant_text
    )

    # --------------------------------------------------------
    # Duplicate
    # --------------------------------------------------------

    pair = (
        user_text.strip(),
        assistant_text.strip()
    )

    if pair in seen:

        duplicates += 1

    else:

        seen.add(pair)

    # --------------------------------------------------------
    # URLs
    # --------------------------------------------------------

    if url_pattern.search(combined):

        urls += 1

    # --------------------------------------------------------
    # Very long
    # --------------------------------------------------------

    if len(combined) > 5000:

        very_long += 1

    # --------------------------------------------------------
    # Devanagari
    # --------------------------------------------------------

    if devanagari_pattern.search(combined):

        devanagari += 1

    # --------------------------------------------------------
    # Suspicious patterns
    # --------------------------------------------------------

    found_suspicious = False

    for pattern in suspicious_patterns:

        if re.search(
            pattern,
            combined,
            re.IGNORECASE
        ):

            suspicious += 1
            found_suspicious = True

            if suspicious <= 10:

                print("\nPossible suspicious example")
                print("Index:", i)
                print("User:", user_text[:500])
                print("Assistant:", assistant_text[:500])
                print("-" * 60)

            break

    # --------------------------------------------------------
    # Progress
    # --------------------------------------------------------

    if (i + 1) % 20000 == 0:

        print(
            f"Scanned: {i + 1}/{len(data)}"
        )


# ============================================================
# RESULT
# ============================================================

print("\n" + "=" * 60)
print("SCAN COMPLETE")
print("=" * 60)

print(
    "Total examples       :",
    len(data)
)

print(
    "Empty/malformed      :",
    empty
)

print(
    "Duplicate pairs      :",
    duplicates
)

print(
    "Examples with URLs   :",
    urls
)

print(
    "Very long examples   :",
    very_long
)

print(
    "Devanagari examples  :",
    devanagari
)

print(
    "Suspicious matches   :",
    suspicious
)

print("=" * 60)