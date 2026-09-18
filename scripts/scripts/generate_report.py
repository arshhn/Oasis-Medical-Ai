import pandas as pd
import os

# ============================
# CONFIG
# ============================
CSV_FILE = "predictions.csv"
OUTPUT_FILE = "clinical_report.txt"

# Map your 6 classes to clinical statements
TEMPLATES = {
    "CXR": "Chest X-ray demonstrates {}.",
    "ChestCT": "Chest CT scan reveals {}.",
    "HeadCT": "Head CT findings indicate {}.",
    "AbdomenCT": "Abdominal CT scan shows {}.",
    "BreastMRI": "Breast MRI presents {}.",
    "Hand": "Hand X-ray reveals {}."
}

DEFAULT_FINDING = "no acute abnormality detected"


def generate_sentence(label):
    if label not in TEMPLATES:
        return f"No template available for {label}."
    return TEMPLATES[label].format(DEFAULT_FINDING)


if not os.path.exists(CSV_FILE):
    print(f"❌ CSV file '{CSV_FILE}' not found!")
    exit()

df = pd.read_csv(CSV_FILE)

# Force UTF-8 (Windows needs this)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("=========== AUTOMATED CLINICAL REPORT ===========\n\n")

    for idx, row in df.iterrows():
        pred = row["prediction"]
        conf = round(float(row["confidence"]), 4)

        f.write(f"Image: {row['image']}\n")
        f.write(f"Prediction: {pred}\n")
        f.write(f"Confidence: {conf}\n")
        f.write(f"Impression: {generate_sentence(pred)}\n")
        f.write("\n")

print("Clinical report successfully saved as clinical_report.txt")
