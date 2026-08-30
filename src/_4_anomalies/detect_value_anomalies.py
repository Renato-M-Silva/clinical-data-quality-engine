"""
Module: detect_value_anomalies
Clinical Data Quality Engine (DQIE) – Module 4: Anomalies

This module performs value-level anomaly detection across clinical datasets.
It identifies physiologically impossible values, out-of-range metrics,
missing mandatory fields, invalid data types, and other inconsistencies.

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
import numpy as np


# ----------------------------------------------------------------------
# Helper: register anomaly
# ----------------------------------------------------------------------
def _add_anomaly(anomalies, record_id, field, value, anomaly_type, description, severity="medium"):
    anomalies.append({
        "record_id": record_id,
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
                _add_anomaly(anomalies, row.get("session_id", idx), field, None,
                            "missing_value", f"Mandatory field '{field}' is missing.")

    # Pain range
    for col in ["pain_initial", "pain_final"]:
        if col in df.columns:
            invalid = df[(df[col] < 0) | (df[col] > 10)]
            for idx, row in invalid.iterrows():
                _add_anomaly(anomalies, row["session_id"], col, row[col],
                            "out_of_range", "Pain must be between 0 and 10.")

    # Mobility range
    for col in ["mobility_initial", "mobility_final"]:
        if col in df.columns:
            invalid = df[(df[col] < 0) | (df[col] > 100)]
            for idx, row in invalid.iterrows():
                _add_anomaly(anomalies, row["session_id"], col, row[col],
                            "out_of_range", "Mobility must be between 0 and 100.")

    # Recovery days
    if "recovery_days" in df.columns:
        invalid = df[df["recovery_days"] < 0]
        for idx, row in invalid.iterrows():
            _add_anomaly(anomalies, row["session_id"], "recovery_days", row["recovery_days"],
                        "invalid_value", "Recovery days cannot be negative.")

    return pd.DataFrame(anomalies)
