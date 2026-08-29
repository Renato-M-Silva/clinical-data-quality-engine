"""
Module: scoring_engine
Clinical Data Quality Engine (DQIE) – Module 6: DQI Scoring

This module orchestrates the full DQI scoring workflow:
    1. Uses reconciliation outputs from Module 5
    2. Computes entity-level DQI scores
    3. Aggregates into dataset-level DQI score
    4. Produces a structured DQI report for dashboards and monitoring

Output:
    A dictionary containing:
        - entity_scores (DataFrame)
        - dataset_score (dict)
"""

import pandas as pd

from src._6_scoring.compute_entity_score import compute_entity_scores
from src._6_scoring.compute_dataset_score import compute_dataset_score


def run_scoring_pipeline(anomalies_summary: pd.DataFrame) -> dict:
    """
    Run the full DQI scoring pipeline.

    Parameters
    ----------
    anomalies_summary : pd.DataFrame
        Output from reconcile_anomalies, with:
            - entity_type
            - entity_id
            - anomalies_count
            - severity_score
            - severity_level
            - sources_involved

    Returns
    -------
    dict
        DQI scoring report:
            - entity_scores
            - dataset_score
    """

    print("=== DQIE Scoring Engine ===")
    print("Step 1: Computing entity-level DQI scores...")

    entity_scores = compute_entity_scores(anomalies_summary)
    print(f"  - Entities scored: {len(entity_scores)}")

    print("Step 2: Computing dataset-level DQI score...")

    dataset_score = compute_dataset_score(entity_scores)
    print(f"  - Global DQI score: {dataset_score['global_score']} ({dataset_score['global_label']})")

    print("=== Scoring Engine Completed ===")

    return {
        "entity_scores": entity_scores,
        "dataset_score": dataset_score
    }
