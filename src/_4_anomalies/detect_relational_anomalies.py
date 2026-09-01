"""
Module: detect_relational_anomalies
Clinical Data Quality Engine (DQIE) – Module 4: Anomalies

This module detects relational anomalies across clinical datasets, including
missing foreign-key relationships, duplicated keys, orphan records, and
inconsistencies between patients, injuries, sessions, and clinical reports.

Output:
    A DataFrame containing all detected anomalies with:
        - record_id
        - entity_type
        - entity_id
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
def _add_anomaly(
    anomalies,
    record_id,
    entity_type,
    entity_id,
    field,
    value,
    anomaly_type,
    description,
    severity="high"
):
    """
    Registers a relational anomaly entry.

    Parameters
    ----------
    record_id : identifier of the record where the anomaly occurred
    entity_type : clinical entity type (session, patient, injury, report, ocr_report)
    entity_id : identifier of the affected entity
    field : field where the anomaly was detected
    value : problematic value
    anomaly_type : category of anomaly
    description : human-readable explanation
    severity : low / medium / high
    """
    anomalies.append({
        "record_id": record_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
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
            record_id=row["session_id"],
            entity_type="session",
            entity_id=row["session_id"],
            field="patient_id",
            value=row["patient_id"],
            anomaly_type="missing_reference",
            description="Session references non-existent patient."
        )

    # --------------------------------------------------------------
    # 2. Sessions referencing missing injury_type
    # --------------------------------------------------------------
    missing = sessions[~sessions["injury_type"].isin(injuries["injury_type"])]
    for idx, row in missing.iterrows():
        _add_anomaly(
            anomalies,
            record_id=row["session_id"],
            entity_type="session",
            entity_id=row["session_id"],
            field="injury_type",
            value=row["injury_type"],
            anomaly_type="missing_reference",
            description="Session references non-existent injury_type."
        )

    # --------------------------------------------------------------
    # 3. Clinical reports referencing missing patients
    # --------------------------------------------------------------
    if clinical_reports is not None:
        missing = clinical_reports[~clinical_reports["patient_id"].isin(patients["patient_id"])]
        for idx, row in missing.iterrows():
            _add_anomaly(
                anomalies,
                record_id=row["report_id"],
                entity_type="report",
                entity_id=row["report_id"],
                field="patient_id",
                value=row["patient_id"],
                anomaly_type="missing_reference",
                description="Clinical report references non-existent patient."
            )

    # --------------------------------------------------------------
    # 4. OCR reports referencing missing patients
    # --------------------------------------------------------------
    if ocr_reports is not None:
        missing = ocr_reports[~ocr_reports["patient_id"].isin(patients["patient_id"])]
        for idx, row in missing.iterrows():
            _add_anomaly(
                anomalies,
                record_id=row["ocr_id"],
                entity_type="ocr_report",
                entity_id=row["ocr_id"],
                field="patient_id",
                value=row["patient_id"],
                anomaly_type="missing_reference",
                description="OCR report references non-existent patient."
            )

    # --------------------------------------------------------------
    # 5. Duplicate primary keys
    # --------------------------------------------------------------
    for df, key, label, entity_type in [
        (patients, "patient_id", "patient", "patient"),
        (injuries, "injury_type", "injury_type", "injury"),
        (sessions, "session_id", "session", "session"),
        (clinical_reports, "report_id", "clinical_report", "report"),
        (ocr_reports, "ocr_id", "ocr_report", "ocr_report")
    ]:
        if df is not None and key in df.columns:
            dup = df[df[key].duplicated(keep=False)]
            for idx, row in dup.iterrows():
                _add_anomaly(
                    anomalies,
                    record_id=row[key],
                    entity_type=entity_type,
                    entity_id=row[key],
                    field=key,
                    value=row[key],
                    anomaly_type="duplicate_key",
                    description=f"Duplicate {label} ID detected.",
                    severity="medium"
                )

    return pd.DataFrame(anomalies)
