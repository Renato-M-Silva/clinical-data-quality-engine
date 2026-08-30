"""
Anomaly Engine — Module 4
Runs all anomaly detectors and returns a unified dictionary.

Used by:
- Notebook 03 (Anomaly Detection)
- main.py (full pipeline execution)
"""

import pandas as pd

from src._4_anomalies.detect_value_anomalies import detect_value_anomalies
from src._4_anomalies.detect_temporal_anomalies import detect_temporal_anomalies
from src._4_anomalies.detect_relational_anomalies import detect_relational_anomalies
from src._4_anomalies.detect_source_anomalies import detect_source_anomalies


def run_anomaly_pipeline(
    patients: pd.DataFrame,
    injuries: pd.DataFrame,
    sessions: pd.DataFrame,
    clinical: pd.DataFrame,
    ocr_json: pd.DataFrame,
    ocr_images: pd.DataFrame
):
    print("=== Running Anomaly Detection Pipeline ===")

    value_anomalies = detect_value_anomalies(sessions)
    print(f"Value anomalies: {len(value_anomalies)}")

    temporal_anomalies = detect_temporal_anomalies(
        patients=patients,
        injuries=injuries,
        sessions=sessions,
        clinical_reports=clinical
    )
    print(f"Temporal anomalies: {len(temporal_anomalies)}")

    relational_anomalies = detect_relational_anomalies(
        patients=patients,
        injuries=injuries,
        sessions=sessions,
        clinical_reports=clinical,
        ocr_reports=ocr_json,
        sql_tables=None
    )
    print(f"Relational anomalies: {len(relational_anomalies)}")

    source_anomalies = detect_source_anomalies(
        csv_data=sessions,
        sql_data=sessions,
        ocr_text=ocr_json,
        ocr_images=ocr_images,
        clinical_json=clinical
    )
    print(f"Source anomalies: {len(source_anomalies)}")

    print("=== Anomaly Detection Completed ===")

    return {
        "value_anomalies": value_anomalies,
        "temporal_anomalies": temporal_anomalies,
        "relational_anomalies": relational_anomalies,
        "source_anomalies": source_anomalies
    }
