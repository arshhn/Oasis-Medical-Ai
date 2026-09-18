import os
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import pandas as pd

MODEL_PATH = "models/best_model.pth"
IMAGE_FOLDER = "sample_images/"
OUTPUT_CSV = "predictions.csv"

# Preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# Load model
print("🔍 Loading model...")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Rebuild architecture
model = models.resnet18(weights=None)
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 6)   # FIXED CLASS COUNT

# Load weights
state_dict = torch.load(MODEL_PATH, map_location=device)
model.load_state_dict(state_dict)


model = model.to(device)
model.eval()

# Class labels
class_names = [
    "AbdomenCT", "BreastMRI", "CXR", "ChestCT", 
    "Hand", "HeadCT"
]

results = []

print("📂 Running batch prediction...")

for filename in os.listdir(IMAGE_FOLDER):
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
        image_path = os.path.join(IMAGE_FOLDER, filename)

        image = Image.open(image_path).convert("RGB")
        img_tensor = transform(image).unsqueeze(0).to(device)

        with torch.no_grad():
            output = model(img_tensor)
            _, predicted = torch.max(output, 1)
            confidence = torch.softmax(output, dim=1)[0][predicted].item()

        pred_class = class_names[predicted]

        results.append({
            "image": filename,
            "prediction": pred_class,
            "confidence": round(confidence, 4)
        })

        print(f"✔ {filename} → {pred_class} ({confidence:.2f})")

# Save results
df = pd.DataFrame(results)
df.to_csv(OUTPUT_CSV, index=False)

print("\n📄 Results saved to predictions.csv")
