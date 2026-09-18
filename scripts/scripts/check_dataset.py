import os

train_dir = r"C:\Users\USER\OneDrive\Desktop\Oasis_AI\dataset\train"
val_dir = r"C:\Users\USER\OneDrive\Desktop\Oasis_AI\dataset\val"

def count_images(path):
    total = 0
    for cls in os.listdir(path):
        cls_path = os.path.join(path, cls)
        if os.path.isdir(cls_path):
            num_images = len(os.listdir(cls_path))
            print(f"{cls}: {num_images} images")
            total += num_images
    return total

print("Train Dataset:")
train_total = count_images(train_dir)

print("\nValidation Dataset:")
val_total = count_images(val_dir)

print(f"\nTotal Images -> Train: {train_total}, Val: {val_total}")
print("✅ Dataset check completed!")
