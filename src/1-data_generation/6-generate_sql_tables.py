import os
import csv

# Input CSVs from Bronze Layer
PATIENTS_CSV = "data/1-bronze/csv/patients.csv"
SESSIONS_CSV = "data/1-bronze/csv/sessions.csv"

# Output directory
OUTPUT_DIR = "data/1-bronze/sql"


def generate_sql_tables(output_dir=OUTPUT_DIR):
    """Generate SQL tables (CREATE + INSERT) for patients and sessions."""

    os.makedirs(output_dir, exist_ok=True)

    patients_sql_path = os.path.join(output_dir, "patients.sql")
    sessions_sql_path = os.path.join(output_dir, "sessions.sql")

    # ---------------------------
    # PATIENTS TABLE
    # ---------------------------
    with open(PATIENTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        patient_rows = list(reader)

    with open(patients_sql_path, mode="w", encoding="utf-8") as f_sql:
        f_sql.write("-- Synthetic Patients Table\n")
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
        f_sql.write("  end_date DATE\n")
        f_sql.write(");\n\n")

        for r in patient_rows:
            f_sql.write(
                "INSERT INTO patients (patient_id, first_name, last_name, age, sex, injury_type, "
                "diagnosis_code, diagnosis_category, start_date, end_date) VALUES "
                f"({r['patient_id']}, '{r['first_name']}', '{r['last_name']}', {r['age']}, "
                f"'{r['sex']}', '{r['injury_type']}', '{r['diagnosis_code']}', "
                f"'{r['diagnosis_category']}', '{r['start_date']}', '{r['end_date']}');\n"
            )

    # ---------------------------
    # SESSIONS TABLE
    # ---------------------------
    with open(SESSIONS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        session_rows = list(reader)

    with open(sessions_sql_path, mode="w", encoding="utf-8") as f_sql:
        f_sql.write("-- Synthetic Sessions Table\n")
        f_sql.write("CREATE TABLE sessions (\n")
        f_sql.write("  session_id INT PRIMARY KEY,\n")
        f_sql.write("  patient_id INT,\n")
        f_sql.write("  session_date DATE,\n")
        f_sql.write("  session_number INT,\n")
        f_sql.write("  injury_type VARCHAR(100),\n")
        f_sql.write("  pain_initial INT,\n")
        f_sql.write("  pain_final INT,\n")
        f_sql.write("  mobility_initial INT,\n")
        f_sql.write("  mobility_final INT,\n")
        f_sql.write("  therapist_id INT,\n")
        f_sql.write("  therapist_notes VARCHAR(255),\n")
        f_sql.write("  recovery_days INT\n")
        f_sql.write(");\n\n")

        for r in session_rows:
            f_sql.write(
                "INSERT INTO sessions (session_id, patient_id, session_date, session_number, injury_type, "
                "pain_initial, pain_final, mobility_initial, mobility_final, therapist_id, therapist_notes, "
                "recovery_days) VALUES "
                f"({r['session_id']}, {r['patient_id']}, '{r['session_date']}', {r['session_number']}, "
                f"'{r['injury_type']}', {r['pain_initial']}, {r['pain_final']}, "
                f"{r['mobility_initial']}, {r['mobility_final']}, {r['therapist_id']}, "
                f"'{r['therapist_notes']}', {r['recovery_days']});\n"
            )

    print(f"Generated SQL tables at: {output_dir}")


if __name__ == "__main__":
    generate_sql_tables()
