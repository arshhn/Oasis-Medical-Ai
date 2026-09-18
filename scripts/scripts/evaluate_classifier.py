import torch
import torch.nn as nn
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os

# ========================
# Paths and Device
# ========================
DATA_DIR = r"C:\Users\USER\OneDrive\Desktop\Oasis_AI\dataset\val"
MODEL_PATH = r"C:\Users\USER\OneDrive\Desktop\Oasis_AI\classifier_model.pth"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# ========================
# Model Definition (match training version)
# ========================
class SimpleCNN(nn.Module):
    def __init__(self, num_classes=6):
        super(SimpleCNN, self).__init__()
        self.embedding = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4))
        )

        self.fc = nn.Sequential(
            nn.Linear(128 * 4 * 4, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, 128),
            nn.ReLU()
        )

        self.classifier = nn.Linear(128, num_classes)

    def forward(self, x):
        x = self.embedding(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        x = self.classifier(x)
        return x

# ========================
# Load model
# ========================
model = SimpleCNN(num_classes=6).to(device)
state_dict = torch.load(MODEL_PATH, map_location=device, weights_only=True)
model.load_state_dict(state_dict, strict=False)
model.eval()

# ========================
# Data Loading
# ========================
transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor()
])

test_dataset = datasets.ImageFolder(root=DATA_DIR, transform=transform)
test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)

# ========================
# Evaluation
# ========================
all_preds, all_labels = [], []

with torch.no_grad():
    for images, labels in test_loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        _, preds = torch.max(outputs, 1)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

# ========================
# Reports and Confusion Matrix
# ========================
print("Classification Report:")
print(classification_report(all_labels, all_preds, target_names=test_dataset.classes))

cm = confusion_matrix(all_labels, all_preds)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=test_dataset.classes,
            yticklabels=test_dataset.classes)
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()
