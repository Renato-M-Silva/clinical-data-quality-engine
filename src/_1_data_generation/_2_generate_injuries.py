import os
import csv
import random
from datetime import datetime, timedelta

PATIENTS_PATH = "data/_1_bronze/csv/patients.csv"
OUTPUT_PATH = "data/_1_bronze/csv/injuries.csv"

ANOMALY_RATE = 0.10  # 10% das lesões terão anomalias
REINJURY_RATE = 0.10  # 10% reincidência
NEW_INJURY_RATE = 0.30  # 30% nova lesão

INJURIES = [
    ("Rotator Cuff Tear", "M75.1", "Musculoskeletal", 60),
    ("ACL Injury", "S83.5", "Musculoskeletal", 120),
    ("Lumbar Disc Herniation", "M51.2", "Musculoskeletal", 90),
    ("Cervical Radiculopathy", "M54.1", "Musculoskeletal", 75),
    ("Ankle Sprain", "S93.4", "Musculoskeletal", 45),
    ("Knee Osteoarthritis", "M17.0", "Musculoskeletal", 120),
]

def load_patients():
    patients = []
    with open(PATIENTS_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["start_date"] = datetime.strptime(row["start_date"], "%Y-%m-%d")
            patients.append(row)
    return patients

def generate_injuries(output_path=OUTPUT_PATH):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    patients = load_patients()
    injuries_out = []
    injury_id = 1

    for p in patients:
        patient_id = int(p["patient_id"])
        base_injury_type = p["injury_type"]
        base_start = p["start_date"]

        # Base injury (always)
        injury_type, diag_code, diag_cat, typical_days = random.choice(INJURIES)

        injuries_out.append({
            "injury_id": injury_id,
            "patient_id": patient_id,
            "injury_type": injury_type,
            "diagnosis_code": diag_code,
            "diagnosis_category": diag_cat,
            "injury_date": base_start.strftime("%Y-%m-%d"),
            "typical_recovery_days": typical_days,
        })
        injury_id += 1

        # Reinjury (10%)
        if random.random() < REINJURY_RATE:
            reinjury_date = base_start + timedelta(days=random.randint(60, 400))
            injuries_out.append({
                "injury_id": injury_id,
                "patient_id": patient_id,
                "injury_type": injury_type,  # same injury
                "diagnosis_code": diag_code,
                "diagnosis_category": diag_cat,
                "injury_date": reinjury_date.strftime("%Y-%m-%d"),
                "typical_recovery_days": typical_days,
            })
            injury_id += 1

        # New injury (30%)
        if random.random() < NEW_INJURY_RATE:
            new_injury_type, new_code, new_cat, new_days = random.choice(INJURIES)
            new_date = base_start + timedelta(days=random.randint(120, 900))

            injuries_out.append({
                "injury_id": injury_id,
                "patient_id": patient_id,
                "injury_type": new_injury_type,
                "diagnosis_code": new_code,
                "diagnosis_category": new_cat,
                "injury_date": new_date.strftime("%Y-%m-%d"),
                "typical_recovery_days": new_days,
            })
            injury_id += 1

    # Write CSV
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "injury_id",
            "patient_id",
            "injury_type",
            "diagnosis_code",
            "diagnosis_category",
            "injury_date",
            "typical_recovery_days",
        ])

        for inj in injuries_out:
            writer.writerow([
                inj["injury_id"],
                inj["patient_id"],
                inj["injury_type"],
                inj["diagnosis_code"],
                inj["diagnosis_category"],
                inj["injury_date"],
                inj["typical_recovery_days"],
            ])

    print(f"Generated {len(injuries_out)} injuries at: {output_path}")

if __name__ == "__main__":
    generate_injuries()
