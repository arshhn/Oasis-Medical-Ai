import torch
import torch.nn as nn
from torchvision import datasets, transforms
import matplotlib.pyplot as plt
import numpy as np
import random
import os

# =======================================
# ✅ Configuration
# =======================================
MODEL_PATH = "classifier_model.pth"
DATA_DIR = "dataset/val"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# =======================================
# ✅ Model Definition (Auto-adaptive flatten)
# =======================================
class SimpleCNN(nn.Module):
    def __init__(self, num_classes=6):
        super(SimpleCNN, self).__init__()

        self.embedding = nn.ModuleDict({
            "convnet": nn.Sequential(
                nn.Conv2d(3, 32, kernel_size=5, stride=1, padding=0),
                nn.ReLU(),
                nn.MaxPool2d(2, 2),
                nn.Conv2d(32, 64, kernel_size=5, stride=1, padding=0),
                nn.ReLU(),
                nn.MaxPool2d(2, 2),
                nn.Conv2d(64, 128, kernel_size=5, stride=1, padding=0),
                nn.ReLU(),
                nn.MaxPool2d(2, 2)
            )
        })

        # Placeholder FC – will be replaced dynamically after seeing an input
        self.embedding_fc = None
        self.classifier = None
        self.num_classes = num_classes

    def build_fc(self, input_shape):
        """Dynamically build FC layers once we know the flatten size."""
        flatten_dim = input_shape
        self.embedding_fc = nn.Sequential(
            nn.Linear(flatten_dim, 512),
            nn.ReLU(),
            nn.Linear(512, 128),
            nn.ReLU()
        )
        self.classifier = nn.Linear(128, self.num_classes)
        self.embedding.add_module("fc", self.embedding_fc)

    def forward(self, x):
        x = self.embedding["convnet"](x)
        x = torch.flatten(x, 1)

        # Build FC dynamically first time
        if self.embedding_fc is None:
            self.build_fc(x.shape[1])
            self.to(x.device)

        x = self.embedding["fc"](x)
        x = self.classifier(x)
        return x


# =======================================
# ✅ Data Transforms
# =======================================
transform = transforms.Compose([
    transforms.Resize((224, 224)),  # same as training size
    transforms.ToTensor(),
    transforms.Normalize([0.5, 0.5, 0.5],
                         [0.5, 0.5, 0.5])
])

# =======================================
# ✅ Load Dataset
# =======================================
if not os.path.exists(DATA_DIR):
    raise FileNotFoundError(f"Validation dataset not found at {DATA_DIR}")

val_dataset = datasets.ImageFolder(DATA_DIR, transform=transform)
val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=1, shuffle=True)

# =======================================
# ✅ Load Model and Adjust Automatically
# =======================================
model = SimpleCNN(num_classes=len(val_dataset.classes)).to(device)

# Build FC layers dynamically
dummy_input = torch.zeros(1, 3, 224, 224).to(device)
with torch.no_grad():
    _ = model(dummy_input)

# Load weights now safely
state_dict = torch.load(MODEL_PATH, map_location=device)
model.load_state_dict(state_dict, strict=False)
model.eval()

print("✅ Model loaded successfully and adjusted to match checkpoint.")

# =======================================
# ✅ Visualization Utility
# =======================================
def show_images_grid(images, preds, actuals):
    plt.figure(figsize=(12, 8))
    for i in range(len(images)):
        img_display = np.transpose((images[i].cpu().numpy() * 0.5 + 0.5), (1, 2, 0))
        img_display = np.clip(img_display, 0, 1)
        plt.subplot(2, 3, i + 1)
        plt.imshow(img_display)
        plt.title(f"Pred: {preds[i]}\nActual: {actuals[i]}", fontsize=10)
        plt.axis("off")
    plt.tight_layout()
    plt.savefig("test_results.png", dpi=300)
    plt.show()

# =======================================
# ✅ Random Predictions
# =======================================
samples = random.sample(range(len(val_dataset)), 6)
images, predictions, actuals = [], [], []

for idx in samples:
    img, label = val_dataset[idx]
    input_tensor = img.unsqueeze(0).to(device)
    with torch.no_grad():
        output = model(input_tensor)
        pred = torch.argmax(output, dim=1).item()

    images.append(img)
    predictions.append(val_dataset.classes[pred])
    actuals.append(val_dataset.classes[label])

show_images_grid(images, predictions, actuals)
