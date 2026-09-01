"""
Module: reconciliation_engine
Clinical Data Quality Engine (DQIE) – Module 5: Reconciliation

This module orchestrates the full reconciliation workflow:
    1. Runs all anomaly detectors (Module 4)
    2. Consolidates anomalies (reconcile_anomalies)
    3. Reconciles entity-level conflicts (reconcile_entities)
    4. Produces a unified Reconciliation Report for Module 6 (DQI Scoring)

Output:
    A dictionary containing:
        - value_anomalies
        - relational_anomalies
        - temporal_anomalies
        - source_anomalies
        - anomalies_summary
        - entities_reconciliation
"""

import pandas as pd

# Module 4 imports
from src._4_anomalies.detect_value_anomalies import detect_value_anomalies
from src._4_anomalies.detect_relational_anomalies import detect_relational_anomalies
from src._4_anomalies.detect_temporal_anomalies import detect_temporal_anomalies
from src._4_anomalies.detect_source_anomalies import detect_source_anomalies

# Module 5 imports
from src._5_reconciliation.reconcile_anomalies import reconcile_anomalies
from src._5_reconciliation.reconcile_entities import reconcile_entities


# ----------------------------------------------------------------------
# Main orchestration function
# ----------------------------------------------------------------------
def run_reconciliation_pipeline(
    patients: pd.DataFrame,
    injuries: pd.DataFrame,
    sessions: pd.DataFrame,
    csv_data: pd.DataFrame,
    sql_data: pd.DataFrame,
    ocr_text: pd.DataFrame,
    clinical_json: pd.DataFrame = None,
    ocr_images: pd.DataFrame = None
) -> dict:
    """
    Executes the full reconciliation workflow.

    Steps:
        1. Run anomaly detectors (Module 4)
        2. Consolidate anomalies (Module 5)
        3. Reconcile entity-level conflicts (Module 5)
        4. Produce unified reconciliation report
    """

    print("=== DQIE Reconciliation Engine ===")
    print("Step 1: Running anomaly detectors...")

    # --------------------------------------------------------------
    # 1. Run anomaly detectors (Module 4)
    # --------------------------------------------------------------

    # Value anomalies (sessions only)
    value_anomalies = detect_value_anomalies(sessions)

    # Relational anomalies (patients, injuries, sessions, reports)
    relational_anomalies = detect_relational_anomalies(
        patients=patients,
        injuries=injuries,
        sessions=sessions,
        clinical_reports=clinical_json,
        ocr_reports=ocr_text
    )

    # Temporal anomalies (sessions, patients, reports)
    temporal_anomalies = detect_temporal_anomalies(
        patients=patients,
        injuries=injuries,
        sessions=sessions,
        clinical_reports=clinical_json
    )

    # Source anomalies (CSV, SQL, OCR, JSON)
    source_anomalies = detect_source_anomalies(
        csv_data=csv_data,
        sql_data=sql_data,
        ocr_text=ocr_text,
        ocr_images=ocr_images,
        clinical_json=clinical_json
    )

    print(f"  - Value anomalies: {len(value_anomalies)}")
    print(f"  - Relational anomalies: {len(relational_anomalies)}")
    print(f"  - Temporal anomalies: {len(temporal_anomalies)}")
    print(f"  - Source anomalies: {len(source_anomalies)}")

    print("Step 2: Consolidating anomalies...")

    # --------------------------------------------------------------
    # 2. Consolidate anomalies (Module 5)
    # --------------------------------------------------------------

    anomalies_summary = reconcile_anomalies(
        value_anomalies=value_anomalies,
        relational_anomalies=relational_anomalies,
        temporal_anomalies=temporal_anomalies,
        source_anomalies=source_anomalies
    )

    print(f"  - Entities with anomalies: {len(anomalies_summary)}")

    print("Step 3: Reconciling entity-level conflicts...")

    # --------------------------------------------------------------
    # 3. Reconcile entities (Module 5)
    # --------------------------------------------------------------

    entities_reconciliation = reconcile_entities(
        csv_data=csv_data,
        sql_data=sql_data,
        ocr_text=ocr_text,
        clinical_json=clinical_json,
        ocr_images=ocr_images
    )

    print(f"  - Reconciled fields: {len(entities_reconciliation)}")

    print("Step 4: Building final reconciliation report...")

    # --------------------------------------------------------------
    # 4. Build final report
    # --------------------------------------------------------------

    report = {
        "value_anomalies": value_anomalies,
        "relational_anomalies": relational_anomalies,
        "temporal_anomalies": temporal_anomalies,
        "source_anomalies": source_anomalies,
        "anomalies_summary": anomalies_summary,
        "entities_reconciliation": entities_reconciliation
    }

    print("=== Reconciliation Engine Completed ===")

    return report
