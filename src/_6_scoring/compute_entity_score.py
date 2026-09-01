"""
Module: compute_entity_score
Clinical Data Quality Engine (DQIE) – Module 6: DQI Scoring

This module computes a Data Quality Index (DQI) score for each clinical entity.
It incorporates:
    - anomaly count
    - severity score
    - severity level
    - number of sources involved
    - entity-type weighting (patients, sessions, injuries, reports)

The scoring model is designed to be flexible and extensible, allowing
different entity types to contribute differently to the overall DQI.

Output:
    A DataFrame with:
        - entity_type
        - entity_id
        - dqi_score (0–100)
        - dqi_label
        - anomalies_count
        - severity_score
        - severity_level
        - sources_involved
"""

import pandas as pd


# ----------------------------------------------------------------------
# Severity-level multiplicative penalty
# ----------------------------------------------------------------------
SEVERITY_LEVEL_PENALTY = {
    "low-risk": 0.10,      # -10%
    "medium-risk": 0.30,   # -30%
    "high-risk": 0.60      # -60%
}


# ----------------------------------------------------------------------
# Entity-type weighting
# ----------------------------------------------------------------------
ENTITY_TYPE_WEIGHT = {
    "patient": 1.00,          # full weight
    "session": 0.90,          # slightly lower impact
    "injury": 0.85,           # injuries often have fewer fields
    "clinical_report": 0.80,  # reports are secondary sources
    "ocr_report": 0.75,       # OCR text less reliable
    "ocr_image": 0.70         # OCR image least reliable
}


# ----------------------------------------------------------------------
# Column validation
# ----------------------------------------------------------------------
REQUIRED_COLUMNS = {
    "entity_type",
    "entity_id",
    "anomalies_count",
    "severity_score",
    "severity_level",
    "sources_involved"
}


def _validate_columns(df: pd.DataFrame):
    """
    Ensures anomalies_summary contains all required columns.
    Raises a clear error if something is missing.
    """
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"anomalies_summary is missing required columns: {missing}"
        )


# ----------------------------------------------------------------------
# Base score calculation
# ----------------------------------------------------------------------
def _compute_base_score(severity_score: int, anomalies_count: int) -> float:
    """
    Compute a base score from severity_score and anomalies_count.
    Starts from 100 and subtracts weighted penalties.
    """

    # Penalty per anomaly (small but cumulative)
    anomaly_penalty = min(anomalies_count * 2, 30)  # max 30 points

    # Penalty from severity_score (scaled)
    severity_penalty = min(severity_score * 3, 50)  # max 50 points

    base = 100 - anomaly_penalty - severity_penalty
    return max(0.0, base)


# ----------------------------------------------------------------------
# Apply severity-level penalty
# ----------------------------------------------------------------------
def _apply_severity_level_penalty(base_score: float, severity_level: str) -> float:
    """
    Apply multiplicative penalty based on severity_level.
    """
    penalty_factor = SEVERITY_LEVEL_PENALTY.get(severity_level, 0.0)
    adjusted = base_score * (1.0 - penalty_factor)
    return max(0.0, adjusted)


# ----------------------------------------------------------------------
# Apply entity-type weighting
# ----------------------------------------------------------------------
def _apply_entity_type_weight(score: float, entity_type: str) -> float:
    """
    Adjust score based on entity type importance.
    """
    weight = ENTITY_TYPE_WEIGHT.get(entity_type, 1.0)
    return max(0.0, score * weight)


# ----------------------------------------------------------------------
# Convert numeric score to qualitative label
# ----------------------------------------------------------------------
def _label_from_score(score: float) -> str:
    """
    Map numeric score to qualitative label.
    """
    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Good"
    if score >= 50:
        return "Moderate"
    if score >= 25:
        return "Poor"
    return "Critical"


# ----------------------------------------------------------------------
# Main function: compute entity scores
# ----------------------------------------------------------------------
def compute_entity_scores(anomalies_summary: pd.DataFrame) -> pd.DataFrame:
    """
    Compute DQI scores for each entity based on the consolidated anomalies summary.

    Steps:
        1. Validate input columns
        2. Compute base score
        3. Apply severity-level penalty
        4. Apply entity-type weighting
        5. Assign qualitative label
    """

    # Handle empty input
    if anomalies_summary is None or len(anomalies_summary) == 0:
        return pd.DataFrame({
            "entity_type": [],
            "entity_id": [],
            "dqi_score": [],
            "dqi_label": [],
            "anomalies_count": [],
            "severity_score": [],
            "severity_level": [],
            "sources_involved": []
        })

    # Validate columns
    _validate_columns(anomalies_summary)

    scores_rows = []

    for _, row in anomalies_summary.iterrows():

        entity_type = row["entity_type"]
        entity_id = row["entity_id"]
        anomalies_count = int(row["anomalies_count"])
        severity_score = int(row["severity_score"])
        severity_level = row["severity_level"]
        sources_involved = row.get("sources_involved", [])

        # Step 1: base score
        base_score = _compute_base_score(severity_score, anomalies_count)

        # Step 2: severity-level penalty
        severity_adjusted = _apply_severity_level_penalty(base_score, severity_level)

        # Step 3: entity-type weighting
        final_score = _apply_entity_type_weight(severity_adjusted, entity_type)

        # Step 4: qualitative label
        label = _label_from_score(final_score)

        scores_rows.append({
            "entity_type": entity_type,
            "entity_id": entity_id,
            "dqi_score": round(final_score, 2),
            "dqi_label": label,
            "anomalies_count": anomalies_count,
            "severity_score": severity_score,
            "severity_level": severity_level,
            "sources_involved": sources_involved
        })

    return pd.DataFrame(scores_rows)
