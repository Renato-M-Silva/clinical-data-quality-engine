import os
import csv
import random
from datetime import datetime, timedelta

PATIENTS_PATH = "data/_1_bronze/csv/patients.csv"
INJURIES_PATH = "data/_1_bronze/csv/injuries.csv"
OUTPUT_PATH = "data/_1_bronze/csv/sessions.csv"

ANOMALY_RATE = 0.10  # 10% of sessions will contain anomalies
THERAPISTS = [101, 102, 103, 104, 105]


def load_patients(path=PATIENTS_PATH):
    """Load patients into a dictionary keyed by patient_id."""
    patients = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            patients[int(row["patient_id"])] = row
    return patients


def load_injuries(path=INJURIES_PATH):
    """Load injuries from CSV."""
    injuries = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["injury_date"] = datetime.strptime(row["injury_date"], "%Y-%m-%d")
            row["typical_recovery_days"] = int(row["typical_recovery_days"])
            injuries.append(row)
    return injuries


def generate_sessions(output_path=OUTPUT_PATH):
    """Generate physiotherapy sessions for every injury."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    patients = load_patients()
    injuries = load_injuries()

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "session_id",
            "patient_id",
            "injury_id",
            "injury_type",
            "session_date",
            "session_number",
            "pain_initial",
            "pain_final",
            "mobility_initial",
            "mobility_final",
            "therapist_id",
            "therapist_notes",
            "recovery_days",
        ])

        session_id = 1

        for inj in injuries:
            patient_id = int(inj["patient_id"])
            injury_id = int(inj["injury_id"])
            injury_type = inj["injury_type"]
            start_date = inj["injury_date"]
            typical_days = inj["typical_recovery_days"]

            # Number of sessions for this injury
            typical_sessions = random.randint(10, 24)
            n_sessions = int(typical_sessions * random.uniform(0.7, 1.3))
            n_sessions = max(n_sessions, 4)

            # Clinical baseline
            base_pain = random.randint(5, 8)
            base_mobility = random.randint(20, 50)

            for session_number in range(1, n_sessions + 1):
                frac = session_number / n_sessions

                # Session date progression
                session_date = start_date + timedelta(days=int(typical_days * frac))

                # Clinical progression
                pain_initial = max(0, min(10, int(base_pain * (1 - 0.5 * frac) + random.uniform(-1, 1))))
                pain_final = max(0, min(10, pain_initial - random.randint(0, 2)))

                mobility_initial = max(0, min(100, int(base_mobility * (1 + 1.0 * frac) + random.uniform(-5, 5))))
                mobility_final = max(mobility_initial, min(100, mobility_initial + random.randint(0, 10)))

                therapist_id = random.choice(THERAPISTS)
                therapist_notes = f"Session {session_number} for {injury_type}"

                recovery_days = (session_date - start_date).days

                # ------------------------------------------------------
                # ANOMALIES (10%)
                # ------------------------------------------------------
                if random.random() < ANOMALY_RATE:
                    anomaly = random.choice([
                        "session_before_injury",
                        "pain_out_of_range",
                        "mobility_out_of_range",
                        "negative_recovery_days",
                        "future_session_date",
                        "wrong_therapist",
                        "pain_increases",
                        "mobility_decreases",
                        "missing_injury_type",
                        "invalid_session_number"
                    ])

                    if anomaly == "session_before_injury":
                        session_date = start_date - timedelta(days=random.randint(1, 20))

                    elif anomaly == "pain_out_of_range":
                        pain_initial = random.randint(11, 20)

                    elif anomaly == "mobility_out_of_range":
                        mobility_initial = random.randint(101, 200)

                    elif anomaly == "negative_recovery_days":
                        recovery_days = -abs(recovery_days)

                    elif anomaly == "future_session_date":
                        session_date = datetime.now() + timedelta(days=random.randint(30, 400))

                    elif anomaly == "wrong_therapist":
                        therapist_id = random.randint(999, 1200)

                    elif anomaly == "pain_increases":
                        pain_final = pain_initial + random.randint(1, 4)

                    elif anomaly == "mobility_decreases":
                        mobility_final = max(0, mobility_initial - random.randint(5, 20))

                    elif anomaly == "missing_injury_type":
                        injury_type = ""

                    elif anomaly == "invalid_session_number":
                        session_number = random.choice([-3, 0, 999])

                writer.writerow([
                    session_id,
                    patient_id,
                    injury_id,
                    injury_type,
                    session_date.strftime("%Y-%m-%d"),
                    session_number,
                    pain_initial,
                    pain_final,
                    mobility_initial,
                    mobility_final,
                    therapist_id,
                    therapist_notes,
                    recovery_days,
                ])

                session_id += 1

    print(f"Generated sessions dataset with multiple injuries at: {output_path}")


if __name__ == "__main__":
    generate_sessions()
