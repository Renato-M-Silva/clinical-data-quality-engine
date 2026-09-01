"""
Module: detect_temporal_anomalies
Clinical Data Quality Engine (DQIE) – Module 4: Anomalies

This module detects temporal anomalies across clinical datasets, including
inverted dates, impossible recovery timelines, inconsistent session ordering,
and unrealistic clinical progression.

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
    severity="high"
):
    """
    Registers a temporal anomaly entry.

    Parameters
    ----------
    record_id : identifier of the record where the anomaly occurred
    entity_type : clinical entity type (session, patient, injury, report)
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
# Main function: detect temporal anomalies
# ----------------------------------------------------------------------
def detect_temporal_anomalies(patients, injuries, sessions, clinical_reports=None):
    """
    Detects temporal anomalies across patients, injuries, sessions,
    and clinical reports.

    Entity type assignment follows the origin dataframe:
        - sessions          → entity_type = "session"
        - clinical_reports  → entity_type = "report"
        - patients          → entity_type = "patient"
        - injuries          → entity_type = "injury" (if needed)
    """

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
            record_id=row["session_id"],
            entity_type="session",
            entity_id=row["session_id"],
            field="session_date",
            value=row["session_date"],
            anomaly_type="inverted_dates",
            description="Session occurs before patient start_date."
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
            record_id=row["session_id"],
            entity_type="session",
            entity_id=row["session_id"],
            field="session_date",
            value=row["session_date"],
            anomaly_type="out_of_range",
            description="Session occurs after patient end_date."
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
            record_id=row["session_id"],
            entity_type="session",
            entity_id=row["session_id"],
            field="pain_final",
            value=row["pain_final"],
            anomaly_type="impossible_progression",
            description="Pain jump > 5 between sessions."
        )

    mob_jump = s[s["mobility_diff"].abs() > 30]
    for idx, row in mob_jump.iterrows():
        _add_anomaly(
            anomalies,
            record_id=row["session_id"],
            entity_type="session",
            entity_id=row["session_id"],
            field="mobility_final",
            value=row["mobility_final"],
            anomaly_type="impossible_progression",
            description="Mobility jump > 30 between sessions."
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
                record_id=row["report_id"],
                entity_type="report",
                entity_id=row["report_id"],
                field="report_date",
                value=row["report_date"],
                anomaly_type="inverted_dates",
                description="Clinical report occurs before patient start_date."
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
                record_id=row["report_id"],
                entity_type="report",
                entity_id=row["report_id"],
                field="report_date",
                value=row["report_date"],
                anomaly_type="out_of_range",
                description="Clinical report occurs after patient end_date."
            )

    return pd.DataFrame(anomalies)
