import torch
from torchvision import transforms, models
from PIL import Image
import os

# --- Configuration ---
MODEL_PATH = "models/best_model.pth"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CLASS_NAMES = ['AbdomenCT', 'BreastMRI', 'CXR', 'ChestCT', 'Hand', 'HeadCT']

# --- Define image transformations (must match training) ---
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# --- Load model ---
print(f"🔍 Loading model from {MODEL_PATH}")
model = models.resnet18(weights=None)
num_ftrs = model.fc.in_features
model.fc = torch.nn.Linear(num_ftrs, len(CLASS_NAMES))
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model = model.to(DEVICE)
model.eval()

# --- Prediction function ---
def predict_image(image_path):
    image = Image.open(image_path).convert("RGB")
    img_tensor = transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        outputs = model(img_tensor)
        _, preds = torch.max(outputs, 1)
        predicted_class = CLASS_NAMES[preds.item()]
        confidence = torch.nn.functional.softmax(outputs, dim=1)[0][preds.item()].item()

    print(f"\n🩻 Prediction: **{predicted_class}** (Confidence: {confidence:.2f})")
    return predicted_class, confidence


# --- Run on a sample image ---
if __name__ == "__main__":
    test_image = input("Enter the path of the image to predict: ").strip('"')
    
    if not os.path.exists(test_image):
        print("❌ Image not found! Check the path.")
    else:
        predict_image(test_image)