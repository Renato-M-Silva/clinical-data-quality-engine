"""
Module: compute_dataset_score
Clinical Data Quality Engine (DQIE) – Module 6: DQI Scoring

This module aggregates entity-level DQI scores into a dataset-level score.
It produces:
    - global DQI score (0–100)
    - average score per entity type
    - severity distribution
    - anomaly density
    - source reliability indicators
    - entity-type weighted score (optional)
    - entity-type contribution analysis

This premium version includes:
    - column validation
    - entity-type weighting
    - extended reliability metrics
    - improved comments and documentation
"""

import pandas as pd


# ----------------------------------------------------------------------
# Helper: label mapping
# ----------------------------------------------------------------------
def _label_from_score(score: float) -> str:
    """
    Convert numeric score into qualitative label.
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
# Required columns for dataset scoring
# ----------------------------------------------------------------------
REQUIRED_COLUMNS = {
    "entity_type",
    "entity_id",
    "dqi_score",
    "dqi_label",
    "anomalies_count",
    "severity_score",
    "severity_level",
    "sources_involved"
}


def _validate_columns(df: pd.DataFrame):
    """
    Ensures entity_scores contains all required columns.
    Raises a clear error if something is missing.
    """
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"entity_scores is missing required columns: {missing}"
        )


# ----------------------------------------------------------------------
# Entity-type weighting (optional)
# ----------------------------------------------------------------------
ENTITY_TYPE_WEIGHT = {
    "patient": 1.00,
    "session": 0.90,
    "injury": 0.85,
    "clinical_report": 0.80,
    "ocr_report": 0.75,
    "ocr_image": 0.70
}


def _apply_entity_type_weight(df: pd.DataFrame) -> pd.Series:
    """
    Apply entity-type weighting to DQI scores.
    """
    return df.apply(
        lambda row: row["dqi_score"] * ENTITY_TYPE_WEIGHT.get(row["entity_type"], 1.0),
        axis=1
    )


# ----------------------------------------------------------------------
# Main function: compute dataset score
# ----------------------------------------------------------------------
def compute_dataset_score(entity_scores: pd.DataFrame) -> dict:
    """
    Compute dataset-level DQI score from entity-level scores.

    Steps:
        1. Validate input columns
        2. Compute global score
        3. Compute score by entity type
        4. Compute severity distribution
        5. Compute anomaly density
        6. Compute source reliability
        7. Compute weighted global score (optional)
        8. Build final report
    """

    # --------------------------------------------------------------
    # Handle case: no entity scores (no anomalies in dataset)
    # --------------------------------------------------------------
    if entity_scores is None or len(entity_scores) == 0:
        return {
            "global_score": 100.0,
            "global_label": "Excellent",
            "score_by_entity_type": {},
            "severity_distribution": {},
            "anomaly_density": 0.0,
            "sources_reliability": {
                "multi_source_entities": 0,
                "percentage_multi_source": 0.0
            },
            "weighted_global_score": 100.0,
            "weighted_global_label": "Excellent",
            "entity_type_contribution": {}
        }

    # --------------------------------------------------------------
    # 1. Validate columns
    # --------------------------------------------------------------
    _validate_columns(entity_scores)

    # --------------------------------------------------------------
    # 2. Global score (mean of all entity scores)
    # --------------------------------------------------------------
    global_score = round(entity_scores["dqi_score"].mean(), 2)
    global_label = _label_from_score(global_score)

    # --------------------------------------------------------------
    # 3. Score by entity type
    # --------------------------------------------------------------
    score_by_entity_type = (
        entity_scores.groupby("entity_type")["dqi_score"]
        .mean()
        .round(2)
        .to_dict()
    )

    # --------------------------------------------------------------
    # 4. Severity distribution
    # --------------------------------------------------------------
    severity_distribution = (
        entity_scores["severity_level"]
        .value_counts()
        .to_dict()
    )

    # --------------------------------------------------------------
    # 5. Anomaly density (anomalies per entity)
    # --------------------------------------------------------------
    anomaly_density = round(
        entity_scores["anomalies_count"].sum() / len(entity_scores),
        2
    )

    # --------------------------------------------------------------
    # 6. Source reliability (multi-source conflicts)
    # --------------------------------------------------------------
    multi_source_entities = entity_scores[
        entity_scores["sources_involved"].apply(lambda s: len(s) > 1)
    ]

    sources_reliability = {
        "multi_source_entities": len(multi_source_entities),
        "percentage_multi_source": round(
            len(multi_source_entities) / len(entity_scores) * 100, 2
        )
    }

    # --------------------------------------------------------------
    # 7. Weighted global score (optional)
    # --------------------------------------------------------------
    weighted_scores = _apply_entity_type_weight(entity_scores)
    weighted_global_score = round(weighted_scores.mean(), 2)
    weighted_global_label = _label_from_score(weighted_global_score)

    # --------------------------------------------------------------
    # 8. Entity-type contribution analysis
    # --------------------------------------------------------------
    entity_type_contribution = (
        weighted_scores.groupby(entity_scores["entity_type"])
        .mean()
        .round(2)
        .to_dict()
    )

    # --------------------------------------------------------------
    # Build final dataset score report
    # --------------------------------------------------------------
    report = {
        "global_score": global_score,
        "global_label": global_label,
        "score_by_entity_type": score_by_entity_type,
        "severity_distribution": severity_distribution,
        "anomaly_density": anomaly_density,
        "sources_reliability": sources_reliability,
        "weighted_global_score": weighted_global_score,
        "weighted_global_label": weighted_global_label,
        "entity_type_contribution": entity_type_contribution
    }

    return report
