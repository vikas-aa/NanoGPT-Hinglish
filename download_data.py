from datasets import load_dataset

print("Downloading dataset...")

dataset = load_dataset("ankitdhiman/hinglish-conversations")

print("\nDataset downloaded successfully!")
print(dataset)

print("\nFirst example:")
print(dataset["train"][0])