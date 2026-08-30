import os
import random
import csv
from datetime import datetime, timedelta

OUTPUT_PATH = "data/_1_bronze/csv/patients.csv"

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

ANOMALY_RATE = 0.08  # 8% dos pacientes terão anomalias

def generate_random_date(start_year=2012, end_year=2024):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)

def generate_patients(n_patients=1000, output_path=OUTPUT_PATH):
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

        existing_ids = set()

        for patient_id in range(1, n_patients + 1):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            age = random.randint(18, 85)
            sex = random.choice(["Male", "Female"])

            injury_type, diagnosis_code, diagnosis_category, typical_recovery_days = random.choice(INJURY_TYPES)

            start_date = generate_random_date()
            recovery_days = int(typical_recovery_days * random.uniform(0.7, 1.3))
            end_date = start_date + timedelta(days=recovery_days)

            # -------------------------------
            # ANOMALIAS REALISTAS (8%)
            # -------------------------------
            if random.random() < ANOMALY_RATE:
                anomaly = random.choice([
                    "negative_age",
                    "future_start_date",
                    "end_before_start",
                    "invalid_sex",
                    "missing_first_name",
                    "duplicate_patient_id",
                    "extreme_age"
                ])

                if anomaly == "negative_age":
                    age = -abs(age)

                elif anomaly == "future_start_date":
                    start_date = datetime.now() + timedelta(days=random.randint(30, 400))

                elif anomaly == "end_before_start":
                    end_date = start_date - timedelta(days=random.randint(1, 30))

                elif anomaly == "invalid_sex":
                    sex = random.choice(["Unknown", "X", ""])

                elif anomaly == "missing_first_name":
                    first_name = ""

                elif anomaly == "duplicate_patient_id" and len(existing_ids) > 10:
                    patient_id = random.choice(list(existing_ids))

                elif anomaly == "extreme_age":
                    age = random.choice([150, 200, -5])

            existing_ids.add(patient_id)

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

    print(f"Generated {n_patients} patients with mixed anomalies at: {output_path}")

if __name__ == "__main__":
    generate_patients()
