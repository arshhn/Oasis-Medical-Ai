import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, WeightedRandomSampler
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, classification_report
import matplotlib.pyplot as plt
from collections import Counter
from tqdm import tqdm
import numpy as np

# =======================
# CONFIG
# =======================
BASE_DIR = os.getcwd()
DATASETS = ["dataset1", "dataset2", "dataset3"]  # modify your folder names
MODEL_DIR = "models"
RESULTS_DIR = "results"
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

BATCH_SIZE = 32
EPOCHS = 10
LR = 1e-4
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"✅ Using device: {DEVICE}")

# =======================
# TRANSFORMS
# =======================
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(brightness=0.1, contrast=0.1),
    transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# =======================
# TRAIN FUNCTION
# =======================
def train_dataset(dataset_path):
    dataset_name = os.path.basename(dataset_path)
    print(f"\n🚀 Training on dataset: {dataset_name}")

    train_dir = os.path.join(dataset_path, "train")
    val_dir = os.path.join(dataset_path, "val")

    if not os.path.exists(train_dir) or not os.path.exists(val_dir):
        print(f"⚠️ Skipping {dataset_name} — missing train/val folders")
        return

    train_data = datasets.ImageFolder(train_dir, transform=train_transform)
    val_data = datasets.ImageFolder(val_dir, transform=val_transform)
    classes = train_data.classes
    print(f"📂 Classes: {classes}")

    labels = [label for _, label in train_data]
    class_counts = Counter(labels)
    print(f"📊 Class counts: {class_counts}")

    class_weights = compute_class_weight('balanced', classes=np.arange(len(classes)), y=labels)
    class_weights = torch.tensor(class_weights, dtype=torch.float).to(DEVICE)
    sample_weights = [1.0 / class_counts[label] for _, label in train_data]
    sampler = WeightedRandomSampler(sample_weights, num_samples=len(sample_weights), replacement=True)

    train_loader = DataLoader(train_data, batch_size=BATCH_SIZE, sampler=sampler)
    val_loader = DataLoader(val_data, batch_size=BATCH_SIZE, shuffle=False)

    # Model setup
    model = models.resnet18(pretrained=True)
    model.fc = nn.Linear(model.fc.in_features, len(classes))
    model = model.to(DEVICE)

    # Train all layers from start
    for param in model.parameters():
        param.requires_grad = True

    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = optim.Adam(model.parameters(), lr=LR, weight_decay=1e-4)

    train_losses, val_losses, train_accs, val_accs = [], [], [], []
    best_val_acc = 0.0

    # =======================
    # TRAINING LOOP
    # =======================
    for epoch in range(EPOCHS):
        print(f"\n📘 Epoch [{epoch+1}/{EPOCHS}]")
        model.train()
        total_loss, correct, total = 0, 0, 0

        for images, labels in tqdm(train_loader, desc="Training", leave=False):
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

        train_loss = total_loss / len(train_loader)
        train_acc = correct / total
        train_losses.append(train_loss)
        train_accs.append(train_acc)

        # =======================
        # VALIDATION
        # =======================
        model.eval()
        val_loss, correct, total = 0, 0, 0
        all_preds, all_labels = [], []

        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(DEVICE), labels.to(DEVICE)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                _, preds = torch.max(outputs, 1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())

        val_loss /= len(val_loader)
        val_acc = correct / total
        val_losses.append(val_loss)
        val_accs.append(val_acc)

        print(f"📉 Train Loss: {train_loss:.4f} | 📈 Train Acc: {train_acc:.4f}")
        print(f"🧪 Val Loss:   {val_loss:.4f} | 🧩 Val Acc:   {val_acc:.4f}")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), f"{MODEL_DIR}/best_model_{dataset_name}.pth")
            print(f"💾 Saved best model for {dataset_name}")

    # =======================
    # PLOT GRAPHS
    # =======================
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.plot(train_losses, label="Train Loss")
    plt.plot(val_losses, label="Val Loss")
    plt.legend(); plt.title("Loss Curve")

    plt.subplot(1, 2, 2)
    plt.plot(train_accs, label="Train Acc")
    plt.plot(val_accs, label="Val Acc")
    plt.legend(); plt.title("Accuracy Curve")

    plt.tight_layout()
    plt.savefig(f"{RESULTS_DIR}/{dataset_name}_training_graph.png")
    plt.close()
    print(f"📊 Saved training graph for {dataset_name}")

    # =======================
    # CONFUSION MATRIX
    # =======================
    cm = confusion_matrix(all_labels, all_preds)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=classes)
    disp.plot(cmap="Blues", values_format="d")
    plt.title(f"Confusion Matrix - {dataset_name}")
    plt.savefig(f"{RESULTS_DIR}/{dataset_name}_confusion_matrix.png")
    plt.close()
    print(f"🧩 Saved confusion matrix for {dataset_name}")

    # =======================
    # CLASSIFICATION REPORT
    # =======================
    print("\n📄 Classification Report:")
    print(classification_report(all_labels, all_preds, target_names=classes, digits=3))
    print(f"\n✅ Training done for {dataset_name}. Best Val Acc: {best_val_acc:.4f}\n")


# =======================
# MAIN
# =======================
for dataset in DATASETS:
    if os.path.exists(dataset):
        train_dataset(dataset)
    else:
        print(f"⚠️ {dataset} not found — skipping")

print("\n🎉 All datasets processed successfully!")
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.savefig(os.path.join(RESULTS_DIR, f"{dataset_name}_confusion_matrix.png"))
plt.close()
print(f"✅ Confusion matrix saved for {dataset_name}")

    # Classification Report
print("\nClassification Report:")
print(classification_report(all_labels, all_preds, target_names=test_dataset.classes))

print(f"\n✅ Evaluation completed for {dataset_name}.\n")