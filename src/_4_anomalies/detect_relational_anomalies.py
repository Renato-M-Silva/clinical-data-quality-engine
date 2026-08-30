"""
Module: detect_relational_anomalies
Clinical Data Quality Engine (DQIE) – Module 4: Anomalies

This module detects relational anomalies across clinical datasets, including
missing foreign-key relationships, duplicated keys, orphan records, and
inconsistencies between patients, injuries, sessions, and clinical reports.

Output:
    A DataFrame containing all detected anomalies with:
        - record_id
        - field
        - value
        - anomaly_type
        - description
        - severity
"""

import pandas as pd

# ----------------------------------------------------------------------
# Helper: register anomaly
# ----------------------------------------------------------------------
def _add_anomaly(anomalies, record_id, field, value, anomaly_type, description, severity="high"):
    anomalies.append({
        "record_id": record_id,
        "field": field,
        "value": value,
        "anomaly_type": anomaly_type,
        "description": description,
        "severity": severity
    })


# ----------------------------------------------------------------------
# Main function: detect relational anomalies
# ----------------------------------------------------------------------
def detect_relational_anomalies(
    patients: pd.DataFrame,
    injuries: pd.DataFrame,
    sessions: pd.DataFrame,
    clinical_reports: pd.DataFrame = None,
    ocr_reports: pd.DataFrame = None
) -> pd.DataFrame:

    anomalies = []

    # --------------------------------------------------------------
    # 1. Sessions referencing missing patients
    # --------------------------------------------------------------
    missing = sessions[~sessions["patient_id"].isin(patients["patient_id"])]
    for idx, row in missing.iterrows():
        _add_anomaly(
            anomalies,
            row["session_id"],
            "patient_id",
            row["patient_id"],
            "missing_reference",
            "Session references non-existent patient."
        )

    # --------------------------------------------------------------
    # 2. Sessions referencing missing injury_type
    # --------------------------------------------------------------
    missing = sessions[~sessions["injury_type"].isin(injuries["injury_type"])]
    for idx, row in missing.iterrows():
        _add_anomaly(
            anomalies,
            row["session_id"],
            "injury_type",
            row["injury_type"],
            "missing_reference",
            "Session references non-existent injury_type."
        )

    # --------------------------------------------------------------
    # 3. Clinical reports referencing missing patients
    # --------------------------------------------------------------
    if clinical_reports is not None:
        missing = clinical_reports[~clinical_reports["patient_id"].isin(patients["patient_id"])]
        for idx, row in missing.iterrows():
            _add_anomaly(
                anomalies,
                row["report_id"],
                "patient_id",
                row["patient_id"],
                "missing_reference",
                "Clinical report references non-existent patient."
            )

    # --------------------------------------------------------------
    # 4. OCR reports referencing missing patients
    # --------------------------------------------------------------
    if ocr_reports is not None:
        missing = ocr_reports[~ocr_reports["patient_id"].isin(patients["patient_id"])]
        for idx, row in missing.iterrows():
            _add_anomaly(
                anomalies,
                row["ocr_id"],
                "patient_id",
                row["patient_id"],
                "missing_reference",
                "OCR report references non-existent patient."
            )

    # --------------------------------------------------------------
    # 5. Duplicate primary keys
    # --------------------------------------------------------------
    for df, key, label in [
        (patients, "patient_id", "patient"),
        (injuries, "injury_type", "injury_type"),
        (sessions, "session_id", "session"),
        (clinical_reports, "report_id", "clinical_report"),
        (ocr_reports, "ocr_id", "ocr_report")
    ]:
        if df is not None and key in df.columns:
            dup = df[df[key].duplicated(keep=False)]
            for idx, row in dup.iterrows():
                _add_anomaly(
                    anomalies,
                    row[key],
                    key,
                    row[key],
                    "duplicate_key",
                    f"Duplicate {label} ID detected.",
                    severity="medium"
                )

    return pd.DataFrame(anomalies)
