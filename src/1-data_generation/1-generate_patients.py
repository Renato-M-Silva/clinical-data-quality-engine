import os
import random
import csv
from datetime import datetime, timedelta

OUTPUT_PATH = "data/bronze/csv/patients.csv"

FIRST_NAMES = [
    "John", "Emily", "Michael", "Sarah", "David", "Laura",
    "Robert", "Anna", "James", "Sophia", "Daniel", "Olivia"
]

LAST_NAMES = [
    "Smith", "Johnson", "Brown", "Taylor", "Anderson",
    "Thomas", "Jackson", "White", "Harris", "Martin"
]

INJURY_TYPES = [
    ("Rotator Cuff Tear", "M75.1", "Musculoskeletal", 60),
    ("ACL Injury", "S83.5", "Musculoskeletal", 120),
    ("Lumbar Disc Herniation", "M51.2", "Musculoskeletal", 90),
    ("Cervical Radiculopathy", "M54.1", "Musculoskeletal", 75),
    ("Ankle Sprain", "S93.4", "Musculoskeletal", 45),
    ("Knee Osteoarthritis", "M17.0", "Musculoskeletal", 120),
]

def generate_random_date(start_year=2022, end_year=2024):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)

def generate_patients(n_patients=300, output_path=OUTPUT_PATH):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "patient_id",
            "first_name",
            "last_name",
            "age",
            "sex",
            "injury_type",
            "diagnosis_code",
            "diagnosis_category",
            "start_date",
            "end_date",
        ])

        for patient_id in range(1, n_patients + 1):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            age = random.randint(18, 85)

            sex = random.choice(["Male", "Female"])

            injury_type, diagnosis_code, diagnosis_category, typical_recovery_days = random.choice(INJURY_TYPES)

            start_date = generate_random_date()
            # recovery between 70% and 130% of typical
            recovery_days = int(typical_recovery_days * random.uniform(0.7, 1.3))
            end_date = start_date + timedelta(days=recovery_days)

            writer.writerow([
                patient_id,
                first_name,
                last_name,
                age,
                sex,
                injury_type,
                diagnosis_code,
                diagnosis_category,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
            ])

    print(f"Generated {n_patients} patients at: {output_path}")

if __name__ == "__main__":
    generate_patients()
