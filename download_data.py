from datasets import load_dataset

print("=" * 60)
print("DOWNLOADING HINGLISH CONVERSATIONS DATASET")
print("=" * 60)

print("\nDataset: theguywithblacktie/hinglish-conversations")
print("Subset: large")

dataset = load_dataset(
    "theguywithblacktie/hinglish-conversations",
    "large"
)

print("\nDataset downloaded successfully!")

print(dataset)

print("\nTrain examples:", len(dataset["train"]))
print("Test examples:", len(dataset["test"]))

print("\nFirst example:")
print(dataset["train"][0])