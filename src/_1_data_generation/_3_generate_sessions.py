import os
import csv
import random
from datetime import datetime, timedelta

PATIENTS_PATH = "data/_1_bronze/csv/patients.csv"
INJURIES_PATH = "data/_1_bronze/csv/injuries.csv"
OUTPUT_PATH = "data/_1_bronze/csv/sessions.csv"

def load_patients(path=PATIENTS_PATH):
    patients = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["start_date"] = datetime.strptime(row["start_date"], "%Y-%m-%d")
            row["end_date"] = datetime.strptime(row["end_date"], "%Y-%m-%d")
            patients.append(row)
    return patients

def load_injuries(path=INJURIES_PATH):
    injuries = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            injuries[row["injury_type"]] = {
                "typical_recovery_days": int(row["typical_recovery_days"]),
                "typical_sessions": int(row["typical_sessions"]),
                "typical_pain_initial": int(row["typical_pain_initial"]),
                "typical_mobility_initial": int(row["typical_mobility_initial"]),
            }
    return injuries

THERAPISTS = [101, 102, 103, 104, 105]

def generate_sessions(output_path=OUTPUT_PATH):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    patients = load_patients()
    injuries = load_injuries()

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "session_id",
            "patient_id",
            "session_date",
            "session_number",
            "injury_type",
            "pain_initial",
            "pain_final",
            "mobility_initial",
            "mobility_final",
            "therapist_id",
            "therapist_notes",
            "recovery_days",
        ])

        session_id = 1

        for p in patients:
            patient_id = int(p["patient_id"])
            injury_type = p["injury_type"]
            start_date = p["start_date"]
            end_date = p["end_date"]
            total_days = (end_date - start_date).days

            injury_info = injuries.get(injury_type, None)

            if injury_info:
                typical_sessions = injury_info["typical_sessions"]
                base_pain = injury_info["typical_pain_initial"]
                base_mobility = injury_info["typical_mobility_initial"]
            else:
                typical_sessions = random.randint(8, 24)
                base_pain = random.randint(4, 8)
                base_mobility = random.randint(20, 60)

            n_sessions = int(typical_sessions * random.uniform(0.7, 1.3))
            n_sessions = max(n_sessions, 4)

            for session_number in range(1, n_sessions + 1):
                frac = session_number / n_sessions
                session_date = start_date + timedelta(days=int(total_days * frac))

                pain_initial = max(0, min(10, int(base_pain * (1 - 0.5 * frac) + random.uniform(-1, 1))))
                pain_final = max(0, min(10, pain_initial - random.randint(0, 2)))

                mobility_initial = max(0, min(100, int(base_mobility * (1 + 1.0 * frac) + random.uniform(-5, 5))))
                mobility_final = max(mobility_initial, min(100, mobility_initial + random.randint(0, 10)))

                therapist_id = random.choice(THERAPISTS)
                therapist_notes = f"Session {session_number} for {injury_type}"

                recovery_days = (session_date - start_date).days

                writer.writerow([
                    session_id,
                    patient_id,
                    session_date.strftime("%Y-%m-%d"),
                    session_number,
                    injury_type,
                    pain_initial,
                    pain_final,
                    mobility_initial,
                    mobility_final,
                    therapist_id,
                    therapist_notes,
                    recovery_days,
                ])

                session_id += 1

    print(f"Generated sessions dataset at: {output_path}")


if __name__ == "__main__":
    generate_sessions()
