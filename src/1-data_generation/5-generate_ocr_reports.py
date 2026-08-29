import os
import json
import csv
from datetime import datetime, timedelta
import random

# Input from Bronze Layer
PATIENTS_PATH = "data/1-bronze/csv/patients.csv"

# Outputs
OUTPUT_JSON_PATH = "data/1-bronze/ocr/ocr_extracted.json"
IMAGES_DIR = "data/1-bronze/images/ocr_reports"


def load_patients(path=PATIENTS_PATH):
    """Load patients from CSV and parse dates."""
    patients = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["start_date"] = datetime.strptime(row["start_date"], "%Y-%m-%d")
            patients.append(row)
    return patients


def generate_ocr_reports(output_json_path=OUTPUT_JSON_PATH, images_dir=IMAGES_DIR, n_reports=50):
    """Generate synthetic OCR reports with placeholder PNG images."""
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    patients = load_patients()
    sampled_patients = random.sample(patients, min(n_reports, len(patients)))

    ocr_entries = []
    ocr_id = 1

    for p in sampled_patients:
        patient_id = int(p["patient_id"])
        injury_type = p["injury_type"]
        start_date = p["start_date"]

        # OCR report date (later than clinical report)
        report_date = start_date + timedelta(days=random.randint(5, 20))

        # Extracted clinical values (OCR noise simulated)
        extracted_pain = random.randint(2, 7)
        extracted_mobility = random.randint(30, 80)

        # Simulated OCR text (with typical OCR imperfections)
        extracted_text = (
            f"Physiotherapy Follow-Up Report\n"
            f"Patient ID: {patient_id}\n"
            f"Injury: {injury_type}\n"
            f"Pain Score: {extracted_pain}/10\n"
            f"Mobility: approx {extracted_mobility}%\n"
            f"Notes: patient shows gradual improvement.\n"
        )

        # Placeholder image file
        image_filename = f"ocr_report_{ocr_id}.png"
        image_path = os.path.join(images_dir, image_filename)

        # Create empty placeholder PNG file
        with open(image_path, "wb") as img_f:
            img_f.write(b"")

        # JSON entry
        ocr_entries.append({
            "ocr_id": ocr_id,
            "patient_id": patient_id,
            "report_date": report_date.strftime("%Y-%m-%d"),
            "extracted_text": extracted_text,
            "extracted_pain": extracted_pain,
            "extracted_mobility": extracted_mobility,
            "image_path": image_path,
        })

        ocr_id += 1

    # Save JSON
    with open(output_json_path, mode="w", encoding="utf-8") as f:
        json.dump(ocr_entries, f, indent=2)

    print(f"Generated OCR reports JSON at: {output_json_path}")
    print(f"Generated placeholder images at: {images_dir}")


if __name__ == "__main__":
    generate_ocr_reports()
