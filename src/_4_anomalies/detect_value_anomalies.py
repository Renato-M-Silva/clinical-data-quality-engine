"""
Module: detect_value_anomalies
Clinical Data Quality Engine (DQIE) – Module 4: Anomalies

This module performs value-level anomaly detection across clinical datasets.
It identifies physiologically impossible values, out-of-range metrics,
missing mandatory fields, invalid data types, and other inconsistencies.

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
import numpy as np


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
    severity="medium"
):
    """
    Registers a single anomaly entry into the anomaly list.

    Parameters
    ----------
    record_id : identifier of the record where the anomaly occurred
    entity_type : clinical entity type (session, patient, injury, report)
    entity_id : identifier of the affected entity
    field : field where the anomaly was detected
    value : the problematic value
    anomaly_type : category of anomaly (missing_value, out_of_range, etc.)
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
# Main function: detect value anomalies
# ----------------------------------------------------------------------
def detect_value_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detects value-level anomalies in the sessions dataset.

    Since this detector operates exclusively on the sessions dataframe,
    all anomalies detected here are associated with the clinical entity
    type "session", and entity_id corresponds to session_id.
    """

    anomalies = []

    # Mandatory fields
    mandatory_fields = [
        "patient_id", "session_id", "injury_type",
        "pain_initial", "pain_final",
        "mobility_initial", "mobility_final",
        "recovery_days"
    ]

    for field in mandatory_fields:
        if field in df.columns:
            missing = df[df[field].isna()]
            for idx, row in missing.iterrows():
                session_id = row.get("session_id", idx)
                _add_anomaly(
                    anomalies,
                    record_id=session_id,
                    entity_type="session",
                    entity_id=session_id,
                    field=field,
                    value=None,
                    anomaly_type="missing_value",
                    description=f"Mandatory field '{field}' is missing."
                )

    # Pain range
    for col in ["pain_initial", "pain_final"]:
        if col in df.columns:
            invalid = df[(df[col] < 0) | (df[col] > 10)]
            for idx, row in invalid.iterrows():
                session_id = row["session_id"]
                _add_anomaly(
                    anomalies,
                    record_id=session_id,
                    entity_type="session",
                    entity_id=session_id,
                    field=col,
                    value=row[col],
                    anomaly_type="out_of_range",
                    description="Pain must be between 0 and 10."
                )

    # Mobility range
    for col in ["mobility_initial", "mobility_final"]:
        if col in df.columns:
            invalid = df[(df[col] < 0) | (df[col] > 100)]
            for idx, row in invalid.iterrows():
                session_id = row["session_id"]
                _add_anomaly(
                    anomalies,
                    record_id=session_id,
                    entity_type="session",
                    entity_id=session_id,
                    field=col,
                    value=row[col],
                    anomaly_type="out_of_range",
                    description="Mobility must be between 0 and 100."
                )

    # Recovery days
    if "recovery_days" in df.columns:
        invalid = df[df["recovery_days"] < 0]
        for idx, row in invalid.iterrows():
            session_id = row["session_id"]
            _add_anomaly(
                anomalies,
                record_id=session_id,
                entity_type="session",
                entity_id=session_id,
                field="recovery_days",
                value=row["recovery_days"],
                anomaly_type="invalid_value",
                description="Recovery days cannot be negative."
            )

    return pd.DataFrame(anomalies)
