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
def detect_temporal_anomalies(
    patients: pd.DataFrame,
    injuries: pd.DataFrame,
    sessions: pd.DataFrame,
    clinical_reports: pd.DataFrame = None
) -> pd.DataFrame:
    """
    Detects temporal anomalies between clinical datasets.

    Parameters
    ----------
    patients : pd.DataFrame
    injuries : pd.DataFrame
    sessions : pd.DataFrame
    clinical_reports : pd.DataFrame, optional

    Returns
    -------
    pd.DataFrame
        A DataFrame containing all detected temporal anomalies.
    """

    anomalies = []

    # ------------------------------------------------------------------
    # 1. Injury dates inconsistent with patient timeline
    # ------------------------------------------------------------------
    if "injury_date" in injuries.columns and "admission_date" in patients.columns:
        merged = injuries.merge(patients, on="patient_id", how="left")

        invalid_injury_dates = merged[
            (merged["injury_date"] < merged["admission_date"])
        ]

        for idx, row in invalid_injury_dates.iterrows():
            _add_anomaly(
                anomalies,
                record_id=row["injury_id"],
                field="injury_date",
                value=row["injury_date"],
                anomaly_type="inverted_dates",
                description="Injury date occurs before patient admission date.",
                severity="high"
            )

    # ------------------------------------------------------------------
    # 2. Sessions occurring before injury date or after discharge
    # ------------------------------------------------------------------
    if "session_date" in sessions.columns:
        merged = sessions.merge(injuries, on="injury_id", how="left")

        # Before injury
        invalid_before_injury = merged[
            (merged["session_date"] < merged["injury_date"])
        ]

        for idx, row in invalid_before_injury.iterrows():
            _add_anomaly(
                anomalies,
                record_id=row["session_id"],
                field="session_date",
                value=row["session_date"],
                anomaly_type="inverted_dates",
                description="Session occurs before injury date.",
                severity="high"
            )

        # After discharge (if available)
        if "discharge_date" in injuries.columns:
            invalid_after_discharge = merged[
                (merged["session_date"] > merged["discharge_date"])
            ]

            for idx, row in invalid_after_discharge.iterrows():
                _add_anomaly(
                    anomalies,
                    record_id=row["session_id"],
                    field="session_date",
                    value=row["session_date"],
                    anomaly_type="out_of_range",
                    description="Session occurs after discharge date.",
                    severity="medium"
                )

    # ------------------------------------------------------------------
    # 3. Sessions out of chronological order
    # ------------------------------------------------------------------
    if "session_date" in sessions.columns:
        sorted_sessions = sessions.sort_values(["patient_id", "session_date"])

        duplicated_timestamps = sorted_sessions[
            sorted_sessions.duplicated(subset=["patient_id", "session_date"], keep=False)
        ]

        for idx, row in duplicated_timestamps.iterrows():
            _add_anomaly(
                anomalies,
                record_id=row["session_id"],
                field="session_date",
                value=row["session_date"],
                anomaly_type="duplicate_timestamp",
                description="Multiple sessions share the same timestamp for the same patient.",
                severity="low"
            )

    # ------------------------------------------------------------------
    # 4. Impossible clinical progression (pain/mobility jumps)
    # ------------------------------------------------------------------
    if "session_date" in sessions.columns:
        sessions_sorted = sessions.sort_values(["patient_id", "session_date"])

        sessions_sorted["pain_diff"] = sessions_sorted.groupby("patient_id")["pain_level"].diff()
        sessions_sorted["mobility_diff"] = sessions_sorted.groupby("patient_id")["mobility_score"].diff()

        # Pain jumps > 5 points in one day
        impossible_pain = sessions_sorted[
            (sessions_sorted["pain_diff"].abs() > 5)
        ]

        for idx, row in impossible_pain.iterrows():
            _add_anomaly(
                anomalies,
                record_id=row["session_id"],
                field="pain_level",
                value=row["pain_level"],
                anomaly_type="impossible_progression",
                description="Pain level changes more than 5 points between consecutive sessions.",
                severity="medium"
            )

        # Mobility jumps > 30 points in one day
        impossible_mobility = sessions_sorted[
            (sessions_sorted["mobility_diff"].abs() > 30)
        ]

        for idx, row in impossible_mobility.iterrows():
            _add_anomaly(
                anomalies,
                record_id=row["session_id"],
                field="mobility_score",
                value=row["mobility_score"],
                anomaly_type="impossible_progression",
                description="Mobility score changes more than 30 points between consecutive sessions.",
                severity="medium"
            )

    # ------------------------------------------------------------------
    # 5. Clinical reports with inconsistent dates
    # ------------------------------------------------------------------
    if clinical_reports is not None and "report_date" in clinical_reports.columns:
        merged = clinical_reports.merge(sessions, on="session_id", how="left")

        invalid_reports = merged[
            (merged["report_date"] < merged["session_date"])
        ]

        for idx, row in invalid_reports.iterrows():
            _add_anomaly(
                anomalies,
                record_id=row.get("report_id", idx),
                field="report_date",
                value=row["report_date"],
                anomaly_type="inverted_dates",
                description="Clinical report date occurs before the session date.",
                severity="high"
            )

    # ------------------------------------------------------------------
    # Return anomalies as DataFrame
    # ------------------------------------------------------------------
    return pd.DataFrame(anomalies)
