"""
Module: compute_dataset_score
Clinical Data Quality Engine (DQIE) – Module 6: DQI Scoring

This module aggregates entity-level DQI scores into a dataset-level score.
It computes:
    - global DQI score (0–100)
    - average score per entity type
    - severity distribution
    - anomaly density
    - source reliability indicators

Output:
    A dictionary containing:
        - global_score
        - global_label
        - score_by_entity_type
        - severity_distribution
        - anomaly_density
        - sources_reliability
"""

import pandas as pd


# ----------------------------------------------------------------------
# Helper: label mapping
# ----------------------------------------------------------------------
def _label_from_score(score: float) -> str:
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
# Main function: compute dataset score
# ----------------------------------------------------------------------
def compute_dataset_score(entity_scores: pd.DataFrame) -> dict:
    """
    Compute dataset-level DQI score from entity-level scores.

    Parameters
    ----------
    entity_scores : pd.DataFrame
        Output from compute_entity_scores, with columns:
            - entity_type
            - entity_id
            - dqi_score
            - dqi_label
            - anomalies_count
            - severity_score
            - severity_level
            - sources_involved

    Returns
    -------
    dict
        Dataset-level DQI score report.
    """

    # ------------------------------------------------------------------
    # 1. Global score (mean of all entity scores)
    # ------------------------------------------------------------------
    global_score = round(entity_scores["dqi_score"].mean(), 2)
    global_label = _label_from_score(global_score)

    # ------------------------------------------------------------------
    # 2. Score by entity type
    # ------------------------------------------------------------------
    score_by_entity_type = (
        entity_scores.groupby("entity_type")["dqi_score"]
        .mean()
        .round(2)
        .to_dict()
    )

    # ------------------------------------------------------------------
    # 3. Severity distribution
    # ------------------------------------------------------------------
    severity_distribution = (
        entity_scores["severity_level"]
        .value_counts()
        .to_dict()
    )

    # ------------------------------------------------------------------
    # 4. Anomaly density (anomalies per entity)
    # ------------------------------------------------------------------
    anomaly_density = round(
        entity_scores["anomalies_count"].sum() / len(entity_scores),
        2
    )

    # ------------------------------------------------------------------
    # 5. Source reliability (how many entities involve multi-source conflicts)
    # ------------------------------------------------------------------
    multi_source_entities = entity_scores[
        entity_scores["sources_involved"].apply(lambda s: len(s) > 1)
    ]

    sources_reliability = {
        "multi_source_entities": len(multi_source_entities),
        "percentage_multi_source": round(
            len(multi_source_entities) / len(entity_scores) * 100, 2
        )
    }

    # ------------------------------------------------------------------
    # Build final dataset score report
    # ------------------------------------------------------------------
    report = {
        "global_score": global_score,
        "global_label": global_label,
        "score_by_entity_type": score_by_entity_type,
        "severity_distribution": severity_distribution,
        "anomaly_density": anomaly_density,
        "sources_reliability": sources_reliability
    }

    return report
