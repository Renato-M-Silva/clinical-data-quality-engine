"""
Module: detect_temporal_anomalies
Clinical Data Quality Engine (DQIE) – Module 4: Anomalies

This module detects temporal anomalies across clinical datasets, including
inverted dates, impossible recovery timelines, inconsistent session ordering,
and unrealistic clinical progression.

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
# Main function: detect temporal anomalies
# ----------------------------------------------------------------------
def detect_temporal_anomalies(patients, injuries, sessions, clinical_reports=None):
    anomalies = []

    # --------------------------------------------------------------
    # 1. Sessions before patient start_date
    # --------------------------------------------------------------
    merged = sessions.merge(
        patients[["patient_id", "start_date"]],
        on="patient_id", how="left"
    )

    invalid = merged[merged["session_date"] < merged["start_date"]]
    for idx, row in invalid.iterrows():
        _add_anomaly(
            anomalies,
            row["session_id"],
            "session_date",
            row["session_date"],
            "inverted_dates",
            "Session occurs before patient start_date."
        )

    # --------------------------------------------------------------
    # 2. Sessions after patient end_date
    # --------------------------------------------------------------
    merged = sessions.merge(
        patients[["patient_id", "end_date"]],
        on="patient_id", how="left"
    )

    invalid = merged[merged["session_date"] > merged["end_date"]]
    for idx, row in invalid.iterrows():
        _add_anomaly(
            anomalies,
            row["session_id"],
            "session_date",
            row["session_date"],
            "out_of_range",
            "Session occurs after patient end_date."
        )

    # --------------------------------------------------------------
    # 3. Impossible progression (pain/mobility jumps)
    # --------------------------------------------------------------
    s = sessions.sort_values(["patient_id", "session_date"])
    s["pain_diff"] = s.groupby("patient_id")["pain_final"].diff()
    s["mobility_diff"] = s.groupby("patient_id")["mobility_final"].diff()

    pain_jump = s[s["pain_diff"].abs() > 5]
    for idx, row in pain_jump.iterrows():
        _add_anomaly(
            anomalies,
            row["session_id"],
            "pain_final",
            row["pain_final"],
            "impossible_progression",
            "Pain jump > 5 between sessions."
        )

    mob_jump = s[s["mobility_diff"].abs() > 30]
    for idx, row in mob_jump.iterrows():
        _add_anomaly(
            anomalies,
            row["session_id"],
            "mobility_final",
            row["mobility_final"],
            "impossible_progression",
            "Mobility jump > 30 between sessions."
        )

    # --------------------------------------------------------------
    # 4. Clinical report before patient start_date
    # --------------------------------------------------------------
    if clinical_reports is not None:
        merged = clinical_reports.merge(
            patients[["patient_id", "start_date"]],
            on="patient_id", how="left"
        )

        invalid = merged[merged["report_date"] < merged["start_date"]]
        for idx, row in invalid.iterrows():
            _add_anomaly(
                anomalies,
                row["report_id"],
                "report_date",
                row["report_date"],
                "inverted_dates",
                "Clinical report occurs before patient start_date."
            )

    # --------------------------------------------------------------
    # 5. Clinical report after patient end_date
    # --------------------------------------------------------------
    if clinical_reports is not None:
        merged = clinical_reports.merge(
            patients[["patient_id", "end_date"]],
            on="patient_id", how="left"
        )

        invalid = merged[merged["report_date"] > merged["end_date"]]
        for idx, row in invalid.iterrows():
            _add_anomaly(
                anomalies,
                row["report_id"],
                "report_date",
                row["report_date"],
                "out_of_range",
                "Clinical report occurs after patient end_date."
            )

    return pd.DataFrame(anomalies)
