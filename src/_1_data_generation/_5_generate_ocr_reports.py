import os
import json
import csv
from datetime import datetime, timedelta
import random

# Input from Bronze Layer
INJURIES_PATH = "data/_1_bronze/csv/injuries.csv"

# Outputs
OUTPUT_JSON_PATH = "data/_1_bronze/ocr/ocr_extracted.json"
IMAGES_DIR = "data/_1_bronze/images/ocr_reports"

ANOMALY_RATE = 0.10  # 10% of OCR entries will contain anomalies


def load_injuries(path=INJURIES_PATH):
    """Load injuries from CSV and parse dates."""
    injuries = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["injury_date"] = datetime.strptime(row["injury_date"], "%Y-%m-%d")
            row["typical_recovery_days"] = int(row["typical_recovery_days"])
            injuries.append(row)
    return injuries


def generate_ocr_reports(output_json_path=OUTPUT_JSON_PATH, images_dir=IMAGES_DIR):
    """Generate synthetic OCR reports for every injury."""
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    injuries = load_injuries()
    ocr_entries = []
    ocr_id = 1

    for inj in injuries:
        patient_id = int(inj["patient_id"])
        injury_id = int(inj["injury_id"])
        injury_type = inj["injury_type"]
        injury_date = inj["injury_date"]

        # OCR report date (usually after clinical report)
        report_date = injury_date + timedelta(days=random.randint(5, 25))

        # Extracted clinical values (OCR noise simulated)
        extracted_pain = random.randint(2, 7)
        extracted_mobility = random.randint(30, 80)

        # Base OCR text
        extracted_text = (
            f"Physiotherapy Follow-Up Report\n"
            f"Patient ID: {patient_id}\n"
            f"Injury: {injury_type}\n"
            f"Pain Score: {extracted_pain}/10\n"
            f"Mobility: approx {extracted_mobility}%\n"
            f"Notes: patient shows gradual improvement.\n"
        )

        # Image filename only — real image generated in script 7
        image_filename = f"ocr_report_{ocr_id}.png"
        image_path = f"data/_1_bronze/images/ocr_reports/{image_filename}"

        # ------------------------------------------------------
        # ANOMALIES (10%)
        # ------------------------------------------------------
        if random.random() < ANOMALY_RATE:
            anomaly = random.choice([
                "ocr_text_corrupted",
                "ocr_missing_fields",
                "ocr_wrong_patient",
                "ocr_future_date",
                "ocr_before_injury",
                "pain_out_of_range",
                "mobility_out_of_range",
                "ocr_inconsistent_values",
                "ocr_empty_text",
                "ocr_invalid_format"
            ])

            if anomaly == "ocr_text_corrupted":
                extracted_text = "### OCR FAILURE ### unreadable text ??? ###"

            elif anomaly == "ocr_missing_fields":
                extracted_text = (
                    f"Physio Report\n"
                    f"Pain Score: {extracted_pain}/10\n"
                    f"Mobility: {extracted_mobility}%\n"
                )  # missing patient ID and injury

            elif anomaly == "ocr_wrong_patient":
                patient_id = random.randint(1, 50)

            elif anomaly == "ocr_future_date":
                report_date = datetime.now() + timedelta(days=random.randint(30, 400))

            elif anomaly == "ocr_before_injury":
                report_date = injury_date - timedelta(days=random.randint(1, 20))

            elif anomaly == "pain_out_of_range":
                extracted_pain = random.randint(11, 20)

            elif anomaly == "mobility_out_of_range":
                extracted_mobility = random.randint(101, 200)

            elif anomaly == "ocr_inconsistent_values":
                extracted_text = (
                    f"Physiotherapy Follow-Up Report\n"
                    f"Patient ID: {patient_id}\n"
                    f"Injury: {injury_type}\n"
                    f"Pain Score: {extracted_pain}/10\n"
                    f"Mobility: approx {extracted_mobility}%\n"
                    f"Notes: patient reports worsening symptoms.\n"
                )

            elif anomaly == "ocr_empty_text":
                extracted_text = ""

            elif anomaly == "ocr_invalid_format":
                extracted_text = "{invalid_json: true, missing_quotes: yes}"

        # JSON entry
        ocr_entries.append({
            "ocr_id": ocr_id,
            "injury_id": injury_id,
            "patient_id": patient_id,
            "report_date": report_date.strftime("%Y-%m-%d"),
            "injury_type": injury_type,
            "extracted_text": extracted_text,
            "extracted_pain": extracted_pain,
            "extracted_mobility": extracted_mobility,
            "image_path": image_path,
        })

        ocr_id += 1

    # Save JSON
    with open(output_json_path, mode="w", encoding="utf-8") as f:
        json.dump(ocr_entries, f, indent=2)

    print(f"Generated {len(ocr_entries)} OCR reports (multiple injuries) at: {output_json_path}")
    print(f"Image metadata prepared at: {images_dir} (real images generated separately)")


if __name__ == "__main__":
    generate_ocr_reports()
