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
    """
    Detects value-level anomalies in clinical datasets.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataset (patients, injuries, sessions, or clinical reports).

    Returns
    -------
    pd.DataFrame
        A DataFrame containing all detected anomalies.
    """

    anomalies = []

    # ------------------------------------------------------------------
    # 1. Missing mandatory fields
    # ------------------------------------------------------------------
    mandatory_fields = [
        "patient_id", "injury_id", "session_id",
        "pain_level", "mobility_score", "recovery_days"
    ]

    for field in mandatory_fields:
        if field in df.columns:
            missing_rows = df[df[field].isna()]
            for idx, row in missing_rows.iterrows():
                _add_anomaly(
                    anomalies,
                    record_id=row.get("patient_id", idx),
                    field=field,
                    value=None,
                    anomaly_type="missing_value",
                    description=f"Mandatory field '{field}' is missing.",
                    severity="high"
                )

    # ------------------------------------------------------------------
    # 2. Physiological ranges
    # ------------------------------------------------------------------
    if "pain_level" in df.columns:
        invalid_pain = df[(df["pain_level"] < 0) | (df["pain_level"] > 10)]
        for idx, row in invalid_pain.iterrows():
            _add_anomaly(
                anomalies,
                record_id=row.get("patient_id", idx),
                field="pain_level",
                value=row["pain_level"],
                anomaly_type="out_of_range",
                description="Pain level must be between 0 and 10.",
                severity="high"
            )

    if "mobility_score" in df.columns:
        invalid_mobility = df[(df["mobility_score"] < 0) | (df["mobility_score"] > 100)]
        for idx, row in invalid_mobility.iterrows():
            _add_anomaly(
                anomalies,
                record_id=row.get("patient_id", idx),
                field="mobility_score",
                value=row["mobility_score"],
                anomaly_type="out_of_range",
                description="Mobility score must be between 0 and 100.",
                severity="medium"
            )

    if "recovery_days" in df.columns:
        invalid_recovery = df[df["recovery_days"] < 0]
        for idx, row in invalid_recovery.iterrows():
            _add_anomaly(
                anomalies,
                record_id=row.get("patient_id", idx),
                field="recovery_days",
                value=row["recovery_days"],
                anomaly_type="invalid_value",
                description="Recovery days cannot be negative.",
                severity="high"
            )

    # ------------------------------------------------------------------
    # 3. Invalid data types
    # ------------------------------------------------------------------
    for col in df.columns:
        if df[col].dtype == object:
            # detect numeric fields stored as strings
            numeric_like = df[col].astype(str).str.replace(".", "", regex=False).str.isnumeric()
            if numeric_like.any():
                for idx, row in df[numeric_like].iterrows():
                    _add_anomaly(
                        anomalies,
                        record_id=row.get("patient_id", idx),
                        field=col,
                        value=row[col],
                        anomaly_type="invalid_type",
                        description=f"Field '{col}' contains numeric values stored as strings.",
                        severity="low"
                    )

    # ------------------------------------------------------------------
    # 4. Impossible values (generic)
    # ------------------------------------------------------------------
    impossible_values = ["N/A", "NULL", "undefined", "missing", "???"]

    for col in df.columns:
        invalid_rows = df[df[col].astype(str).str.lower().isin([v.lower() for v in impossible_values])]
        for idx, row in invalid_rows.iterrows():
            _add_anomaly(
                anomalies,
                record_id=row.get("patient_id", idx),
                field=col,
                value=row[col],
                anomaly_type="invalid_value",
                description=f"Field '{col}' contains an impossible placeholder value.",
                severity="medium"
            )

    # ------------------------------------------------------------------
    # Return anomalies as DataFrame
    # ------------------------------------------------------------------
    return pd.DataFrame(anomalies)
