import os
import json
import csv
from datetime import datetime, timedelta
import random

# Input from Bronze Layer
PATIENTS_PATH = "data/1-bronze/csv/patients.csv"

# Output JSON
OUTPUT_PATH = "data/1-bronze/ocr/clinical_reports.json"


def load_patients(path=PATIENTS_PATH):
    """Load patients from CSV and parse dates."""
    patients = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["start_date"] = datetime.strptime(row["start_date"], "%Y-%m-%d")
            patients.append(row)
    return patients


def generate_clinical_reports(output_path=OUTPUT_PATH):
    """Generate synthetic clinical evaluation reports for physiotherapy."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    patients = load_patients()
    reports = []

    report_id = 1

    for p in patients:
        patient_id = int(p["patient_id"])
        injury_type = p["injury_type"]
        start_date = p["start_date"]

        # Report date: evaluation happens early in treatment
        report_date = start_date + timedelta(days=random.randint(0, 7))

        # Clinical scores
        pain_score = random.randint(4, 8)
        mobility_score = random.randint(20, 60)

        # Free-text diagnosis
        diagnosis_text = (
            f"Patient presents with {injury_type}. "
            f"Clinical findings include pain score {pain_score}/10 and reduced mobility."
        )

        # Therapist notes
        notes = (
            f"Initial physiotherapy evaluation for {injury_type}. "
            f"Patient reports pain during movement and functional limitations. "
            f"Mobility estimated at {mobility_score}% of normal range."
        )

        reports.append({
            "report_id": report_id,
            "patient_id": patient_id,
            "report_date": report_date.strftime("%Y-%m-%d"),
            "diagnosis_text": diagnosis_text,
            "pain_score": pain_score,
            "mobility_score": mobility_score,
            "notes": notes,
        })

        report_id += 1

    # Save JSON
    with open(output_path, mode="w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2)

    print(f"Generated clinical reports at: {output_path}")


if __name__ == "__main__":
    generate_clinical_reports()
