import os
import shutil
import random

# Paths
raw_data_dir = r"C:\Users\USER\OneDrive\Desktop\Oasis_AI\dataset_raw"
output_dir = r"C:\Users\USER\OneDrive\Desktop\Oasis_AI\dataset"

train_dir = os.path.join(output_dir, "train")
val_dir = os.path.join(output_dir, "val")

# Train/Val split ratio
split_ratio = 0.8  # 80% train, 20% val

# Create train/val dirs
for folder in [train_dir, val_dir]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Go through each class
for class_name in os.listdir(raw_data_dir):
    class_path = os.path.join(raw_data_dir, class_name)
    if not os.path.isdir(class_path):
        continue

    images = os.listdir(class_path)
    random.shuffle(images)

    split_index = int(len(images) * split_ratio)
    train_images = images[:split_index]
    val_images = images[split_index:]

    # Create class folders in train and val
    os.makedirs(os.path.join(train_dir, class_name), exist_ok=True)
    os.makedirs(os.path.join(val_dir, class_name), exist_ok=True)

    # Copy train images
    for img in train_images:
        shutil.copy(os.path.join(class_path, img), os.path.join(train_dir, class_name, img))

    # Copy val images
    for img in val_images:
        shutil.copy(os.path.join(class_path, img), os.path.join(val_dir, class_name, img))

print("✅ Dataset split completed! Train and Val sets are ready.")
