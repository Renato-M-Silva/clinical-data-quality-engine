import os
import json
import csv
from datetime import datetime, timedelta
import random

# Input from Bronze Layer
INJURIES_PATH = "data/_1_bronze/csv/injuries.csv"

# Output JSON
OUTPUT_PATH = "data/_1_bronze/ocr/clinical_reports.json"

ANOMALY_RATE = 0.10  # 10% of reports will contain anomalies


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


def generate_clinical_reports(output_path=OUTPUT_PATH):
    """Generate one clinical evaluation report per injury."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    injuries = load_injuries()
    reports = []

    report_id = 1

    for inj in injuries:
        patient_id = int(inj["patient_id"])
        injury_id = int(inj["injury_id"])
        injury_type = inj["injury_type"]
        injury_date = inj["injury_date"]

        # Clinical evaluation usually happens early after injury
        report_date = injury_date + timedelta(days=random.randint(0, 10))

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

        # ------------------------------------------------------
        # ANOMALIES (10%)
        # ------------------------------------------------------
        if random.random() < ANOMALY_RATE:
            anomaly = random.choice([
                "future_report_date",
                "report_before_injury",
                "pain_out_of_range",
                "mobility_out_of_range",
                "missing_injury_type",
                "nonsense_text",
                "contradictory_text",
                "duplicate_patient_id",
                "empty_notes",
                "empty_diagnosis"
            ])

            if anomaly == "future_report_date":
                report_date = datetime.now() + timedelta(days=random.randint(30, 400))

            elif anomaly == "report_before_injury":
                report_date = injury_date - timedelta(days=random.randint(1, 20))

            elif anomaly == "pain_out_of_range":
                pain_score = random.randint(11, 20)

            elif anomaly == "mobility_out_of_range":
                mobility_score = random.randint(101, 200)

            elif anomaly == "missing_injury_type":
                injury_type = ""

            elif anomaly == "nonsense_text":
                diagnosis_text = "### OCR FAILURE ### unreadable clinical text ???"
                notes = "### TEXT CORRUPTED ###"

            elif anomaly == "contradictory_text":
                diagnosis_text = (
                    f"Patient presents with {injury_type}. "
                    f"Pain score reported as {pain_score}/10 but patient denies any pain."
                )

            elif anomaly == "duplicate_patient_id":
                patient_id = random.randint(1, 50)

            elif anomaly == "empty_notes":
                notes = ""

            elif anomaly == "empty_diagnosis":
                diagnosis_text = ""

        reports.append({
            "report_id": report_id,
            "injury_id": injury_id,
            "patient_id": patient_id,
            "report_date": report_date.strftime("%Y-%m-%d"),
            "injury_type": injury_type,
            "diagnosis_text": diagnosis_text,
            "pain_score": pain_score,
            "mobility_score": mobility_score,
            "notes": notes,
        })

        report_id += 1

    # Save JSON
    with open(output_path, mode="w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2)

    print(f"Generated {len(reports)} clinical reports (multiple injuries) at: {output_path}")


if __name__ == "__main__":
    generate_clinical_reports()
