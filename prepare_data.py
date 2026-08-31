from datasets import load_dataset

# Dataset load karo
dataset = load_dataset("ankitdhiman/hinglish-conversations")

train_data = dataset["train"]

output_file = "data/chat_train.txt"

count = 0

with open(output_file, "w", encoding="utf-8") as f:

    for row in train_data:

        user = row["user_message"].strip()
        assistant = row["assistant_message"].strip()

        # Empty examples skip karo
        if not user or not assistant:
            continue

        f.write("<|user|>\n")
        f.write(user)
        f.write("\n")

        f.write("<|assistant|>\n")
        f.write(assistant)
        f.write("\n\n")

        count += 1

print("Training examples written:", count)
print("Saved to:", output_file)