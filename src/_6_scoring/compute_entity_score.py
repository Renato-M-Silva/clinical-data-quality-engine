"""
Module: compute_entity_score
Clinical Data Quality Engine (DQIE) – Module 6: DQI Scoring

This module computes a Data Quality Index (DQI) score for each clinical entity
(patient, injury, session) based on:
    - anomalies_count
    - severity_score
    - severity_level
    - sources_involved

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
# Helper: map severity_level to penalty
# ----------------------------------------------------------------------
SEVERITY_LEVEL_PENALTY = {
    "low-risk": 0.10,      # -10%
    "medium-risk": 0.30,   # -30%
    "high-risk": 0.60      # -60%
}


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


def _apply_severity_level_penalty(base_score: float, severity_level: str) -> float:
    """
    Apply a multiplicative penalty based on severity_level.
    """

    penalty_factor = SEVERITY_LEVEL_PENALTY.get(severity_level, 0.0)
    adjusted = base_score * (1.0 - penalty_factor)
    return max(0.0, adjusted)


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

    Parameters
    ----------
    anomalies_summary : pd.DataFrame
        Output from reconcile_anomalies, with columns:
            - entity_type
            - entity_id
            - anomalies_count
            - severity_score
            - severity_level
            - sources_involved

    Returns
    -------
    pd.DataFrame
        Entity-level DQI scores.
    """

    scores_rows = []

    for _, row in anomalies_summary.iterrows():
        entity_type = row["entity_type"]
        entity_id = row["entity_id"]
        anomalies_count = int(row["anomalies_count"])
        severity_score = int(row["severity_score"])
        severity_level = row["severity_level"]
        sources_involved = row.get("sources_involved", [])

        base_score = _compute_base_score(severity_score, anomalies_count)
        final_score = _apply_severity_level_penalty(base_score, severity_level)
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
