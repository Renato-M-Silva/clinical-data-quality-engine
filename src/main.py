"""
Clinical Data Quality Engine (DQIE)
Main Pipeline Orchestrator

This script runs the full Bronze → Silver → Gold pipeline:
1. Ingestion & Validation (Notebooks 01–02)
2. Anomaly Detection (Notebook 03)
3. Reconciliation (Notebook 04)
4. DQI Scoring (Notebook 05)
5. Dashboard Export (Notebook 06)

Usage:
    python main.py --run-all
    python main.py --stage anomalies
    python main.py --stage reconciliation
    python main.py --stage scoring
    python main.py --stage dashboard
"""

import argparse
import os
import json
import pandas as pd

# === MODULE IMPORTS ===========================================================
from src._4_anomalies.anomaly_engine import run_anomaly_pipeline
from src._5_reconciliation.reconciliation_engine import run_reconciliation_pipeline
from src._6_scoring.scoring_engine import run_scoring_pipeline


# === PATHS ====================================================================
SILVER_DIR = "data/_2_silver/"
GOLD_ANOM_DIR = "data/_3_gold/anomalies/"
GOLD_REC_DIR = "data/_3_gold/reconciliation/"
GOLD_SCORE_DIR = "data/_3_gold/scoring/"
GOLD_DASH_DIR = "data/_3_gold/dashboard/"


# === HELPERS ==================================================================
def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


# === STAGE 1: ANOMALY DETECTION ===============================================
def stage_anomalies():
    print("\n=== MODULE 3 — ANOMALY DETECTION ===")

    df_patients = pd.read_parquet(f"{SILVER_DIR}/patients.parquet")
    df_injuries = pd.read_parquet(f"{SILVER_DIR}/injuries.parquet")
    df_sessions = pd.read_parquet(f"{SILVER_DIR}/sessions.parquet")
    df_clinical = pd.read_parquet(f"{SILVER_DIR}/clinical_reports.parquet")
    df_ocr_json = pd.read_parquet(f"{SILVER_DIR}/ocr_extracted.parquet")
    df_ocr_images = pd.read_parquet(f"{SILVER_DIR}/ocr_images.parquet")

    anomalies = run_anomaly_pipeline(
        patients=df_patients,
        injuries=df_injuries,
        sessions=df_sessions,
        clinical=df_clinical,
        ocr_json=df_ocr_json,
        ocr_images=df_ocr_images
    )

    ensure_dir(GOLD_ANOM_DIR)

    for key, df in anomalies.items():
        df.to_parquet(f"{GOLD_ANOM_DIR}/{key}.parquet", index=False)

    print("Anomaly detection completed and saved to Gold Layer.")


# === STAGE 2: RECONCILIATION ==================================================
def stage_reconciliation():
    print("\n=== MODULE 5 — RECONCILIATION ===")

    df_patients = pd.read_parquet(f"{SILVER_DIR}/patients.parquet")
    df_injuries = pd.read_parquet(f"{SILVER_DIR}/injuries.parquet")
    df_sessions = pd.read_parquet(f"{SILVER_DIR}/sessions.parquet")
    df_clinical = pd.read_parquet(f"{SILVER_DIR}/clinical_reports.parquet")
    df_ocr_json = pd.read_parquet(f"{SILVER_DIR}/ocr_extracted.parquet")
    df_ocr_images = pd.read_parquet(f"{SILVER_DIR}/ocr_images.parquet")

    reconciliation = run_reconciliation_pipeline(
        patients=df_patients,
        injuries=df_injuries,
        sessions=df_sessions,
        csv_data=df_sessions,
        sql_data=df_sessions,
        ocr_text=df_ocr_json,
        clinical_json=df_clinical,
        ocr_images=df_ocr_images
    )

    ensure_dir(GOLD_REC_DIR)

    # Fix dict columns for Parquet
    entities = reconciliation["entities_reconciliation"].copy()
    entities = entities.astype("string")

    reconciliation["anomalies_summary"].to_parquet(
        f"{GOLD_REC_DIR}/anomalies_summary.parquet", index=False
    )
    entities.to_parquet(
        f"{GOLD_REC_DIR}/entities_reconciliation.parquet", index=False
    )

    print("Reconciliation completed and saved to Gold Layer.")


# === STAGE 3: SCORING =========================================================
def stage_scoring():
    print("\n=== MODULE 6 — DQI SCORING ===")

    anomalies_summary = pd.read_parquet(f"{GOLD_REC_DIR}/anomalies_summary.parquet")

    scoring_output = run_scoring_pipeline(anomalies_summary)

    entity_scores = scoring_output["entity_scores"]
    dataset_score = scoring_output["dataset_score"]

    ensure_dir(GOLD_SCORE_DIR)

    entity_scores.to_parquet(f"{GOLD_SCORE_DIR}/entity_scores.parquet", index=False)

    with open(f"{GOLD_SCORE_DIR}/dataset_score.json", "w") as f:
        json.dump(dataset_score, f, indent=4)

    print("Scoring completed and saved to Gold Layer.")


# === STAGE 4: DASHBOARD EXPORT ================================================
def stage_dashboard():
    print("\n=== MODULE 7 — DASHBOARD EXPORT ===")

    entity_scores = pd.read_parquet(f"{GOLD_SCORE_DIR}/entity_scores.parquet")

    with open(f"{GOLD_SCORE_DIR}/dataset_score.json", "r") as f:
        dataset_score = json.load(f)

    dataset_score_df = pd.DataFrame([{
        "global_score": dataset_score["global_score"],
        "global_label": dataset_score["global_label"],
        "anomaly_density": dataset_score["anomaly_density"],
        "multi_source_entities": dataset_score["sources_reliability"]["multi_source_entities"],
        "percentage_multi_source": dataset_score["sources_reliability"]["percentage_multi_source"]
    }])

    severity_dist_df = pd.DataFrame(
        list(dataset_score.get("severity_distribution", {}).items()),
        columns=["severity_level", "count"]
    )

    score_by_type_df = pd.DataFrame(
        list(dataset_score.get("score_by_entity_type", {}).items()),
        columns=["entity_type", "avg_score"]
    )

    ensure_dir(GOLD_DASH_DIR)

    entity_scores.to_parquet(f"{GOLD_DASH_DIR}/entity_scores.parquet", index=False)
    dataset_score_df.to_parquet(f"{GOLD_DASH_DIR}/dataset_score.parquet", index=False)
    severity_dist_df.to_parquet(f"{GOLD_DASH_DIR}/severity_distribution.parquet", index=False)
    score_by_type_df.to_parquet(f"{GOLD_DASH_DIR}/score_by_entity_type.parquet", index=False)

    print("Dashboard export completed and saved to Gold Layer.")


# === MAIN =====================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=str, default="all",
                        help="Stage to run: anomalies, reconciliation, scoring, dashboard, all")
    args = parser.parse_args()

    if args.stage == "anomalies":
        stage_anomalies()
    elif args.stage == "reconciliation":
        stage_reconciliation()
    elif args.stage == "scoring":
        stage_scoring()
    elif args.stage == "dashboard":
        stage_dashboard()
    else:
        stage_anomalies()
        stage_reconciliation()
        stage_scoring()
        stage_dashboard()

    print("\n=== DQIE PIPELINE COMPLETED ===")
