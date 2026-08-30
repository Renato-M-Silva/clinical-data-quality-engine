import os
import csv
import random
from datetime import datetime, timedelta

# Input CSVs from Bronze Layer
PATIENTS_CSV = "data/_1_bronze/csv/patients.csv"
INJURIES_CSV = "data/_1_bronze/csv/injuries.csv"
SESSIONS_CSV = "data/_1_bronze/csv/sessions.csv"

# Output directory
OUTPUT_DIR = "data/_1_bronze/sql"

ANOMALY_RATE = 0.10  # 10% of SQL rows will contain anomalies


def generate_sql_tables(output_dir=OUTPUT_DIR):
    """Generate SQL tables (CREATE + INSERT) for patients, injuries, and sessions with anomalies."""

    os.makedirs(output_dir, exist_ok=True)

    patients_sql_path = os.path.join(output_dir, "patients.sql")
    injuries_sql_path = os.path.join(output_dir, "injuries.sql")
    sessions_sql_path = os.path.join(output_dir, "sessions.sql")

    # ---------------------------
    # LOAD PATIENTS CSV
    # ---------------------------
    with open(PATIENTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        patient_rows = list(reader)

    # ---------------------------
    # PATIENTS TABLE (SQL)
    # ---------------------------
    with open(patients_sql_path, mode="w", encoding="utf-8") as f_sql:
        f_sql.write("-- Synthetic Patients Table (with anomalies)\n")
        f_sql.write("CREATE TABLE patients (\n")
        f_sql.write("  patient_id INT PRIMARY KEY,\n")
        f_sql.write("  first_name VARCHAR(50),\n")
        f_sql.write("  last_name VARCHAR(50),\n")
        f_sql.write("  age INT,\n")
        f_sql.write("  sex VARCHAR(10),\n")
        f_sql.write("  injury_type VARCHAR(100),\n")
        f_sql.write("  diagnosis_code VARCHAR(20),\n")
        f_sql.write("  diagnosis_category VARCHAR(50),\n")
        f_sql.write("  start_date DATE,\n")
        f_sql.write("  end_date DATE\n");
        f_sql.write(");\n\n")

        for r in patient_rows:

            # Copy original values
            patient_id = r["patient_id"]
            first_name = r["first_name"]
            last_name = r["last_name"]
            age = r["age"]
            sex = r["sex"]
            injury_type = r["injury_type"]
            diagnosis_code = r["diagnosis_code"]
            diagnosis_category = r["diagnosis_category"]
            start_date = r["start_date"]
            end_date = r["end_date"]

            # ---------------------------------------------
            # ANOMALIES (10%)
            # ---------------------------------------------
            if random.random() < ANOMALY_RATE:
                anomaly = random.choice([
                    "age_mismatch",
                    "wrong_sex",
                    "injury_typo",
                    "date_shift",
                    "missing_last_name",
                    "duplicate_patient_id",
                    "invalid_diagnosis_code",
                    "end_before_start"
                ])

                if anomaly == "age_mismatch":
                    age = str(int(age) + random.randint(-5, 15))

                elif anomaly == "wrong_sex":
                    sex = random.choice(["Unknown", "X", ""])

                elif anomaly == "injury_typo":
                    injury_type = injury_type.replace(" ", "")

                elif anomaly == "date_shift":
                    dt = datetime.strptime(start_date, "%Y-%m-%d")
                    dt = dt + timedelta(days=random.randint(-20, 20))
                    start_date = dt.strftime("%Y-%m-%d")

                elif anomaly == "missing_last_name":
                    last_name = ""

                elif anomaly == "duplicate_patient_id":
                    patient_id = random.randint(1, 50)

                elif anomaly == "invalid_diagnosis_code":
                    diagnosis_code = "XXX"

                elif anomaly == "end_before_start":
                    end_date = "1900-01-01"

            # Write SQL INSERT
            f_sql.write(
                "INSERT INTO patients (patient_id, first_name, last_name, age, sex, injury_type, "
                "diagnosis_code, diagnosis_category, start_date, end_date) VALUES "
                f"({patient_id}, '{first_name}', '{last_name}', {age}, "
                f"'{sex}', '{injury_type}', '{diagnosis_code}', "
                f"'{diagnosis_category}', '{start_date}', '{end_date}');\n"
            )

    # ---------------------------
    # LOAD INJURIES CSV
    # ---------------------------
    with open(INJURIES_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        injury_rows = list(reader)

    # ---------------------------
    # INJURIES TABLE (SQL)
    # ---------------------------
    with open(injuries_sql_path, mode="w", encoding="utf-8") as f_sql:
        f_sql.write("-- Synthetic Injuries Table (with anomalies)\n")
        f_sql.write("CREATE TABLE injuries (\n")
        f_sql.write("  injury_id INT PRIMARY KEY,\n")
        f_sql.write("  patient_id INT,\n")
        f_sql.write("  injury_type VARCHAR(100),\n")
        f_sql.write("  diagnosis_code VARCHAR(20),\n")
        f_sql.write("  diagnosis_category VARCHAR(50),\n")
        f_sql.write("  injury_date DATE,\n")
        f_sql.write("  typical_recovery_days INT\n");
        f_sql.write(");\n\n")

        for r in injury_rows:

            injury_id = r["injury_id"]
            patient_id = r["patient_id"]
            injury_type = r["injury_type"]
            diagnosis_code = r["diagnosis_code"]
            diagnosis_category = r["diagnosis_category"]
            injury_date = r["injury_date"]
            typical_days = r["typical_recovery_days"]

            # ---------------------------------------------
            # ANOMALIES (10%)
            # ---------------------------------------------
            if random.random() < ANOMALY_RATE:
                anomaly = random.choice([
                    "invalid_recovery_days",
                    "invalid_sessions",
                    "pain_out_of_range",
                    "mobility_out_of_range",
                    "future_injury_date",
                    "missing_patient",
                    "duplicate_injury_id",
                    "unknown_injury_type"
                ])

                if anomaly == "invalid_recovery_days":
                    typical_days = random.choice([-10, 0, 5000])

                elif anomaly == "future_injury_date":
                    injury_date = (datetime.now() + timedelta(days=random.randint(30, 400))).strftime("%Y-%m-%d")

                elif anomaly == "missing_patient":
                    patient_id = None

                elif anomaly == "duplicate_injury_id":
                    injury_id = random.randint(1, 50)

                elif anomaly == "unknown_injury_type":
                    injury_type = "UNKNOWN_INJURY"

            f_sql.write(
                "INSERT INTO injuries (injury_id, patient_id, injury_type, diagnosis_code, "
                "diagnosis_category, injury_date, typical_recovery_days) VALUES "
                f"({injury_id}, {patient_id}, '{injury_type}', '{diagnosis_code}', "
                f"'{diagnosis_category}', '{injury_date}', {typical_days});\n"
            )

    # ---------------------------
    # LOAD SESSIONS CSV
    # ---------------------------
    with open(SESSIONS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        session_rows = list(reader)

    # ---------------------------
    # SESSIONS TABLE (SQL)
    # ---------------------------
    with open(sessions_sql_path, mode="w", encoding="utf-8") as f_sql:
        f_sql.write("-- Synthetic Sessions Table (with anomalies)\n")
        f_sql.write("CREATE TABLE sessions (\n")
        f_sql.write("  session_id INT PRIMARY KEY,\n")
        f_sql.write("  patient_id INT,\n")
        f_sql.write("  injury_id INT,\n")
        f_sql.write("  injury_type VARCHAR(100),\n")
        f_sql.write("  session_date DATE,\n")
        f_sql.write("  session_number INT,\n")
        f_sql.write("  pain_initial INT,\n")
        f_sql.write("  pain_final INT,\n")
        f_sql.write("  mobility_initial INT,\n")
        f_sql.write("  mobility_final INT,\n")
        f_sql.write("  therapist_id INT,\n")
        f_sql.write("  therapist_notes VARCHAR(255),\n")
        f_sql.write("  recovery_days INT\n");
        f_sql.write(");\n\n")

        for r in session_rows:

            session_id = r["session_id"]
            patient_id = r["patient_id"]
            injury_id = r["injury_id"]
            injury_type = r["injury_type"]
            session_date = r["session_date"]
            session_number = r["session_number"]
            pain_initial = r["pain_initial"]
            pain_final = r["pain_final"]
            mobility_initial = r["mobility_initial"]
            mobility_final = r["mobility_final"]
            therapist_id = r["therapist_id"]
            therapist_notes = r["therapist_notes"]
            recovery_days = r["recovery_days"]

            # ---------------------------------------------
            # ANOMALIES (10%)
            # ---------------------------------------------
            if random.random() < ANOMALY_RATE:
                anomaly = random.choice([
                    "pain_mismatch",
                    "mobility_mismatch",
                    "wrong_therapist",
                    "invalid_session_number",
                    "missing_injury_type",
                    "date_shift",
                    "duplicate_session_id",
                    "negative_recovery_days"
                ])

                if anomaly == "pain_mismatch":
                    pain_initial = str(int(pain_initial) + random.randint(-3, 5))

                elif anomaly == "mobility_mismatch":
                    mobility_final = str(int(mobility_final) + random.randint(-10, 20))

                elif anomaly == "wrong_therapist":
                    therapist_id = random.randint(999, 1200)

                elif anomaly == "invalid_session_number":
                    session_number = random.choice([-1, 0, 999])

                elif anomaly == "missing_injury_type":
                    injury_type = ""

                elif anomaly == "date_shift":
                    dt = datetime.strptime(session_date, "%Y-%m-%d")
                    dt = dt + timedelta(days=random.randint(-15, 15))
                    session_date = dt.strftime("%Y-%m-%d")

                elif anomaly == "duplicate_session_id":
                    session_id = random.randint(1, 100)

                elif anomaly == "negative_recovery_days":
                    recovery_days = -abs(int(recovery_days))

            f_sql.write(
                "INSERT INTO sessions (session_id, patient_id, injury_id, injury_type, session_date, "
                "session_number, pain_initial, pain_final, mobility_initial, mobility_final, therapist_id, "
                "therapist_notes, recovery_days) VALUES "
                f"({session_id}, {patient_id}, {injury_id}, '{injury_type}', '{session_date}', "
                f"{session_number}, {pain_initial}, {pain_final}, {mobility_initial}, {mobility_final}, "
                f"{therapist_id}, '{therapist_notes}', {recovery_days});\n"
            )

    print(f"Generated SQL tables with multiple injuries and anomalies at: {output_dir}")


if __name__ == "__main__":
    generate_sql_tables()
