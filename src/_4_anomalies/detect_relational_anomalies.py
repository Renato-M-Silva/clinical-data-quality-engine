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
    ocr_reports: pd.DataFrame = None,
    sql_tables: pd.DataFrame = None
) -> pd.DataFrame:
    """
    Detects relational anomalies between clinical datasets.

    Parameters
    ----------
    patients : pd.DataFrame
    injuries : pd.DataFrame
    sessions : pd.DataFrame
    clinical_reports : pd.DataFrame, optional
    ocr_reports : pd.DataFrame, optional
    sql_tables : pd.DataFrame, optional

    Returns
    -------
    pd.DataFrame
        A DataFrame containing all detected relational anomalies.
    """

    anomalies = []

    # ------------------------------------------------------------------
    # 1. Sessions referencing non-existent patients
    # ------------------------------------------------------------------
    if "patient_id" in sessions.columns:
        missing_patients = sessions[~sessions["patient_id"].isin(patients["patient_id"])]
        for idx, row in missing_patients.iterrows():
            _add_anomaly(
                anomalies,
                record_id=row["session_id"],
                field="patient_id",
                value=row["patient_id"],
                anomaly_type="missing_reference",
                description="Session references a non-existent patient.",
                severity="high"
            )

    # ------------------------------------------------------------------
    # 2. Sessions referencing non-existent injuries
    # ------------------------------------------------------------------
    if "injury_id" in sessions.columns:
        missing_injuries = sessions[~sessions["injury_id"].isin(injuries["injury_id"])]
        for idx, row in missing_injuries.iterrows():
            _add_anomaly(
                anomalies,
                record_id=row["session_id"],
                field="injury_id",
                value=row["injury_id"],
                anomaly_type="missing_reference",
                description="Session references a non-existent injury.",
                severity="high"
            )

    # ------------------------------------------------------------------
    # 3. Injuries referencing non-existent patients
    # ------------------------------------------------------------------
    if "patient_id" in injuries.columns:
        missing_patients_in_injuries = injuries[~injuries["patient_id"].isin(patients["patient_id"])]
        for idx, row in missing_patients_in_injuries.iterrows():
            _add_anomaly(
                anomalies,
                record_id=row["injury_id"],
                field="patient_id",
                value=row["patient_id"],
                anomaly_type="missing_reference",
                description="Injury references a non-existent patient.",
                severity="high"
            )

    # ------------------------------------------------------------------
    # 4. Duplicate primary keys
    # ------------------------------------------------------------------
    def detect_duplicates(df, key, label):
        duplicates = df[df[key].duplicated(keep=False)]
        for idx, row in duplicates.iterrows():
            _add_anomaly(
                anomalies,
                record_id=row[key],
                field=key,
                value=row[key],
                anomaly_type="duplicate_key",
                description=f"Duplicate {label} ID detected.",
                severity="medium"
            )

    detect_duplicates(patients, "patient_id", "patient")
    detect_duplicates(injuries, "injury_id", "injury")
    detect_duplicates(sessions, "session_id", "session")

    # ------------------------------------------------------------------
    # 5. Clinical reports referencing missing sessions
    # ------------------------------------------------------------------
    if clinical_reports is not None and "session_id" in clinical_reports.columns:
        missing_sessions = clinical_reports[~clinical_reports["session_id"].isin(sessions["session_id"])]
        for idx, row in missing_sessions.iterrows():
            _add_anomaly(
                anomalies,
                record_id=row.get("report_id", idx),
                field="session_id",
                value=row["session_id"],
                anomaly_type="missing_reference",
                description="Clinical report references a non-existent session.",
                severity="high"
            )

    # ------------------------------------------------------------------
    # 6. OCR reports referencing missing patients or sessions
    # ------------------------------------------------------------------
    if ocr_reports is not None:
        if "patient_id" in ocr_reports.columns:
            missing_ocr_patients = ocr_reports[~ocr_reports["patient_id"].isin(patients["patient_id"])]
            for idx, row in missing_ocr_patients.iterrows():
                _add_anomaly(
                    anomalies,
                    record_id=row.get("ocr_id", idx),
                    field="patient_id",
                    value=row["patient_id"],
                    anomaly_type="missing_reference",
                    description="OCR report references a non-existent patient.",
                    severity="medium"
                )

        if "session_id" in ocr_reports.columns:
            missing_ocr_sessions = ocr_reports[~ocr_reports["session_id"].isin(sessions["session_id"])]
            for idx, row in missing_ocr_sessions.iterrows():
                _add_anomaly(
                    anomalies,
                    record_id=row.get("ocr_id", idx),
                    field="session_id",
                    value=row["session_id"],
                    anomaly_type="missing_reference",
                    description="OCR report references a non-existent session.",
                    severity="medium"
                )

    # ------------------------------------------------------------------
    # 7. SQL tables referencing missing patients/sessions
    # ------------------------------------------------------------------
    if sql_tables is not None:
        if "patient_id" in sql_tables.columns:
            missing_sql_patients = sql_tables[~sql_tables["patient_id"].isin(patients["patient_id"])]
            for idx, row in missing_sql_patients.iterrows():
                _add_anomaly(
                    anomalies,
                    record_id=row.get("sql_id", idx),
                    field="patient_id",
                    value=row["patient_id"],
                    anomaly_type="missing_reference",
                    description="SQL table references a non-existent patient.",
                    severity="medium"
                )

        if "session_id" in sql_tables.columns:
            missing_sql_sessions = sql_tables[~sql_tables["session_id"].isin(sessions["session_id"])]
            for idx, row in missing_sql_sessions.iterrows():
                _add_anomaly(
                    anomalies,
                    record_id=row.get("sql_id", idx),
                    field="session_id",
                    value=row["session_id"],
                    anomaly_type="missing_reference",
                    description="SQL table references a non-existent session.",
                    severity="medium"
                )

    # ------------------------------------------------------------------
    # Return anomalies as DataFrame
    # ------------------------------------------------------------------
    return pd.DataFrame(anomalies)
