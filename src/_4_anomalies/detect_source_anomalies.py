"""
Module: detect_source_anomalies
Clinical Data Quality Engine (DQIE) – Module 4: Anomalies

This module detects source-level anomalies across clinical datasets, including
inconsistencies between CSV, SQL, OCR, JSON clinical reports, and image-based
OCR extractions.

Output:
    A DataFrame containing all detected anomalies with:
        - record_id
        - field
        - value
        - anomaly_type
        - description
        - severity
"""

import pandas as pd


# ----------------------------------------------------------------------
# Helper: register anomaly
# ----------------------------------------------------------------------
def _add_anomaly(anomalies, record_id, field, value, anomaly_type, description, severity="medium"):
    anomalies.append({
        "record_id": record_id,
        "field": field,
        "value": value,
        "anomaly_type": anomaly_type,
        "description": description,
        "severity": severity
    })


# ----------------------------------------------------------------------
# Main function: detect source anomalies
# ----------------------------------------------------------------------
def detect_source_anomalies(csv_data, sql_data, ocr_text, ocr_images=None, clinical_json=None):
    anomalies = []

    # --------------------------------------------------------------
    # 1. Mandatory fields across sources
    # --------------------------------------------------------------
    mandatory = ["patient_id", "session_id", "injury_type"]

    for field in mandatory:
        for name, df in [
            ("CSV", csv_data),
            ("SQL", sql_data),
            ("OCR Text", ocr_text),
            ("OCR Images", ocr_images),
            ("Clinical JSON", clinical_json)
        ]:
            if df is not None and field in df.columns:
                missing = df[df[field].isna()]
                for idx, row in missing.iterrows():
                    _add_anomaly(
                        anomalies,
                        row.get("session_id", idx),
                        field,
                        None,
                        "missing_value",
                        f"Field '{field}' missing in {name}."
                    )

    # --------------------------------------------------------------
    # 2. OCR referencing missing patients
    # --------------------------------------------------------------
    missing = ocr_text[~ocr_text["patient_id"].isin(csv_data["patient_id"])]
    for idx, row in missing.iterrows():
        _add_anomaly(
            anomalies,
            row["ocr_id"],
            "patient_id",
            row["patient_id"],
            "missing_reference",
            "OCR references non-existent patient."
        )

    # --------------------------------------------------------------
    # 3. OCR images without OCR text
    # --------------------------------------------------------------
    if ocr_images is not None:
        if "ocr_id" in ocr_images.columns and "ocr_id" in ocr_text.columns:
            missing_text = ocr_images[~ocr_images["ocr_id"].isin(ocr_text["ocr_id"])]
            for idx, row in missing_text.iterrows():
                _add_anomaly(
                    anomalies,
                    row["ocr_id"],
                    "ocr_id",
                    row["ocr_id"],
                    "missing_text",
                    "OCR image has no corresponding OCR text."
                )

            missing_image = ocr_text[~ocr_text["ocr_id"].isin(ocr_images["ocr_id"])]
            for idx, row in missing_image.iterrows():
                _add_anomaly(
                    anomalies,
                    row["ocr_id"],
                    "ocr_id",
                    row["ocr_id"],
                    "missing_image",
                    "OCR text has no corresponding OCR image."
                )

    return pd.DataFrame(anomalies)
