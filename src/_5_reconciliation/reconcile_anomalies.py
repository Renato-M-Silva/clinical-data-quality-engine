"""
Module: reconcile_anomalies
Clinical Data Quality Engine (DQIE) – Module 5: Reconciliation

This module consolidates anomalies detected across all anomaly detectors
(value, relational, temporal, and source anomalies). It groups anomalies by
entity, computes severity scores, identifies repeated patterns, and produces
a unified anomaly reconciliation summary.

Output:
    A DataFrame containing consolidated anomaly reconciliation:
        - entity_type
        - entity_id
        - anomalies_count
        - severity_score
        - severity_level
        - anomaly_types
        - fields_affected
        - notes
"""

import pandas as pd


# ----------------------------------------------------------------------
# Helper: severity mapping
# ----------------------------------------------------------------------
SEVERITY_MAP = {
    "low": 1,
    "medium": 2,
    "high": 3
}


# ----------------------------------------------------------------------
# Main function: reconcile anomalies
# ----------------------------------------------------------------------
def reconcile_anomalies(
    value_anomalies: pd.DataFrame,
    relational_anomalies: pd.DataFrame,
    temporal_anomalies: pd.DataFrame,
    source_anomalies: pd.DataFrame
) -> pd.DataFrame:
    """
    Consolidates anomalies from all detectors into a unified reconciliation summary.

    All anomaly detectors must provide:
        - entity_type
        - entity_id
        - record_id
        - field
        - value
        - anomaly_type
        - description
        - severity

    This module no longer infers entity_type from record_id.
    Instead, it relies entirely on the detectors' explicit entity_type/entity_id.
    """

    # --------------------------------------------------------------
    # 1. Combine all anomalies into a single DataFrame
    # --------------------------------------------------------------
    all_anomalies = pd.concat([
        value_anomalies.assign(source="value"),
        relational_anomalies.assign(source="relational"),
        temporal_anomalies.assign(source="temporal"),
        source_anomalies.assign(source="source")
    ], ignore_index=True)

    # --------------------------------------------------------------
    # 2. Validate required columns
    # --------------------------------------------------------------
    required_cols = {"entity_type", "entity_id", "record_id", "field", "anomaly_type", "severity"}
    missing = required_cols - set(all_anomalies.columns)

    if missing:
        raise ValueError(
            f"Missing required anomaly columns: {missing}. "
            "All detectors must output entity_type and entity_id explicitly."
        )

    # --------------------------------------------------------------
    # 3. Group anomalies by entity
    # --------------------------------------------------------------
    grouped = all_anomalies.groupby(["entity_type", "entity_id"])

    rows = []

    for (entity_type, entity_id), group in grouped:

        anomaly_types = sorted(group["anomaly_type"].unique())
        fields_affected = sorted(group["field"].unique())
        severity_values = group["severity"].map(SEVERITY_MAP)
        severity_score = severity_values.sum()

        # Determine severity level
        if severity_score >= 10:
            severity_level = "high-risk"
            notes = "Entity shows multiple severe anomalies across sources."
        elif severity_score >= 5:
            severity_level = "medium-risk"
            notes = "Entity shows moderate anomalies requiring attention."
        else:
            severity_level = "low-risk"
            notes = "Entity shows minor anomalies."

        rows.append({
            "entity_type": entity_type,
            "entity_id": entity_id,
            "anomalies_count": len(group),
            "severity_score": severity_score,
            "severity_level": severity_level,
            "anomaly_types": anomaly_types,
            "fields_affected": fields_affected,
            "sources_involved": sorted(group["source"].unique()),
            "notes": notes
        })

    return pd.DataFrame(rows)

