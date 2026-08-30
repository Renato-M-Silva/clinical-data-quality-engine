import os
import sys

# Import all generators
from _1_generate_patients import generate_patients
from _2_generate_injuries import generate_injuries
from _3_generate_sessions import generate_sessions
from _4_generate_clinical_reports import generate_clinical_reports
from _5_generate_ocr_reports import generate_ocr_reports
from _6_generate_sql_tables import generate_sql_tables
from _7_generate_real_ocr_images import generate_real_ocr_images


def check_file(path):
    """Utility: ensure a file exists before continuing."""
    if not os.path.exists(path):
        print(f"ERROR: Required file not found: {path}")
        sys.exit(1)


def main():
    print("\n==============================================")
    print("   Clinical Data Quality Engine - Full Build")
    print("==============================================\n")

    # ------------------------------------------------------------
    # 1. Generate Patients
    # ------------------------------------------------------------
    print("STEP 1 — Generating patients...")
    generate_patients()
    check_file("data/_1_bronze/csv/patients.csv")

    # ------------------------------------------------------------
    # 2. Generate Injuries (multi-injury model)
    # ------------------------------------------------------------
    print("STEP 2 — Generating injuries...")
    generate_injuries()
    check_file("data/_1_bronze/csv/injuries.csv")

    # ------------------------------------------------------------
    # 3. Generate Sessions (per injury)
    # ------------------------------------------------------------
    print("STEP 3 — Generating sessions...")
    generate_sessions()
    check_file("data/_1_bronze/csv/sessions.csv")

    # ------------------------------------------------------------
    # 4. Generate Clinical Reports (per injury)
    # ------------------------------------------------------------
    print("STEP 4 — Generating clinical reports...")
    generate_clinical_reports()
    check_file("data/_1_bronze/ocr/clinical_reports.json")

    # ------------------------------------------------------------
    # 5. Generate OCR Reports (per injury)
    # ------------------------------------------------------------
    print("STEP 5 — Generating OCR extracted reports...")
    generate_ocr_reports()
    check_file("data/_1_bronze/ocr/ocr_extracted.json")

    # ------------------------------------------------------------
    # 6. Generate SQL Tables (patients + injuries + sessions)
    # ------------------------------------------------------------
    print("STEP 6 — Generating SQL tables...")
    generate_sql_tables()
    check_file("data/_1_bronze/sql/patients.sql")
    check_file("data/_1_bronze/sql/injuries.sql")
    check_file("data/_1_bronze/sql/sessions.sql")

    # ------------------------------------------------------------
    # 7. Generate Real OCR Images (with artifacts)
    # ------------------------------------------------------------
    print("STEP 7 — Generating OCR images...")
    generate_real_ocr_images()
    print("OCR images generated successfully.")

    print("\n==============================================")
    print("   FULL DATA GENERATION COMPLETED SUCCESSFULLY")
    print("==============================================\n")


if __name__ == "__main__":
    main()
