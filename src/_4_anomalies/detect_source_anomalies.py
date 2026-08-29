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
def detect_source_anomalies(
    csv_data: pd.DataFrame,
    sql_data: pd.DataFrame,
    ocr_text: pd.DataFrame,
    ocr_images: pd.DataFrame = None,
    clinical_json: pd.DataFrame = None
) -> pd.DataFrame:
    """
    Detects anomalies between multiple data sources (CSV, SQL, OCR, JSON, images).

    Parameters
    ----------
    csv_data : pd.DataFrame
    sql_data : pd.DataFrame
    ocr_text : pd.DataFrame
    ocr_images : pd.DataFrame, optional
    clinical_json : pd.DataFrame, optional

    Returns
    -------
    pd.DataFrame
        A DataFrame containing all detected source anomalies.
    """

    anomalies = []

    # ------------------------------------------------------------------
    # 1. Missing mandatory fields in any source
    # ------------------------------------------------------------------
    mandatory_fields = ["patient_id", "session_id", "injury_id"]

    for field in mandatory_fields:
        for source_name, df in [
            ("CSV", csv_data),
            ("SQL", sql_data),
            ("OCR Text", ocr_text),
            ("OCR Images", ocr_images),
            ("Clinical JSON", clinical_json)
        ]:
            if df is not None and field in df.columns:
                missing_rows = df[df[field].isna()]
                for idx, row in missing_rows.iterrows():
                    _add_anomaly(
                        anomalies,
                        record_id=row.get("session_id", idx),
                        field=field,
                        value=None,
                        anomaly_type="missing_value",
                        description=f"Mandatory field '{field}' missing in {source_name} source.",
                        severity="high"
                    )

    # ------------------------------------------------------------------
    # 2. CSV vs SQL inconsistencies
    # ------------------------------------------------------------------
    common_cols = [col for col in csv_data.columns if col in sql_data.columns]

    merged = csv_data.merge(sql_data, on=["session_id"], suffixes=("_csv", "_sql"), how="outer")

    for col in common_cols:
        csv_col = f"{col}_csv"
        sql_col = f"{col}_sql"

        mismatches = merged[
            (merged[csv_col].notna()) &
            (merged[sql_col].notna()) &
            (merged[csv_col] != merged[sql_col])
        ]

        for idx, row in mismatches.iterrows():
            _add_anomaly(
                anomalies,
                record_id=row.get("session_id", idx),
                field=col,
                value=f"{row[csv_col]} vs {row[sql_col]}",
                anomaly_type="source_mismatch",
                description=f"CSV and SQL values differ for field '{col}'.",
                severity="medium"
            )

    # ------------------------------------------------------------------
    # 3. OCR text referencing missing sessions or patients
    # ------------------------------------------------------------------
    if "session_id" in ocr_text.columns:
        missing_sessions = ocr_text[~ocr_text["session_id"].isin(csv_data["session_id"])]
        for idx, row in missing_sessions.iterrows():
            _add_anomaly(
                anomalies,
                record_id=row.get("ocr_id", idx),
                field="session_id",
                value=row["session_id"],
                anomaly_type="missing_reference",
                description="OCR text references a session not present in CSV.",
                severity="high"
            )

    if "patient_id" in ocr_text.columns:
        missing_patients = ocr_text[~ocr_text["patient_id"].isin(csv_data["patient_id"])]
        for idx, row in missing_patients.iterrows():
            _add_anomaly(
                anomalies,
                record_id=row.get("ocr_id", idx),
                field="patient_id",
                value=row["patient_id"],
                anomaly_type="missing_reference",
                description="OCR text references a patient not present in CSV.",
                severity="high"
            )

    # ------------------------------------------------------------------
    # 4. OCR images without OCR text (and vice-versa)
    # ------------------------------------------------------------------
    if ocr_images is not None:
        if "ocr_id" in ocr_images.columns and "ocr_id" in ocr_text.columns:
            missing_text = ocr_images[~ocr_images["ocr_id"].isin(ocr_text["ocr_id"])]
            for idx, row in missing_text.iterrows():
                _add_anomaly(
                    anomalies,
                    record_id=row["ocr_id"],
                    field="ocr_id",
                    value=row["ocr_id"],
                    anomaly_type="missing_text",
                    description="OCR image has no corresponding OCR text.",
                    severity="medium"
                )

            missing_image = ocr_text[~ocr_text["ocr_id"].isin(ocr_images["ocr_id"])]
            for idx, row in missing_image.iterrows():
                _add_anomaly(
                    anomalies,
                    record_id=row["ocr_id"],
                    field="ocr_id",
                    value=row["ocr_id"],
                    anomaly_type="missing_image",
                    description="OCR text has no corresponding OCR image.",
                    severity="medium"
                )

    # ------------------------------------------------------------------
    # 5. Clinical JSON inconsistencies
    # ------------------------------------------------------------------
    if clinical_json is not None:
        if "session_id" in clinical_json.columns:
            missing_sessions_json = clinical_json[
                ~clinical_json["session_id"].isin(csv_data["session_id"])
            ]
            for idx, row in missing_sessions_json.iterrows():
                _add_anomaly(
                    anomalies,
                    record_id=row.get("report_id", idx),
                    field="session_id",
                    value=row["session_id"],
                    anomaly_type="missing_reference",
                    description="Clinical JSON references a session not present in CSV.",
                    severity="high"
                )

        # Compare JSON vs CSV values
        json_common_cols = [col for col in clinical_json.columns if col in csv_data.columns]

        merged_json = clinical_json.merge(csv_data, on="session_id", suffixes=("_json", "_csv"), how="inner")

        for col in json_common_cols:
            json_col = f"{col}_json"
            csv_col = f"{col}_csv"

            mismatches = merged_json[
                (merged_json[json_col].notna()) &
                (merged_json[csv_col].notna()) &
                (merged_json[json_col] != merged_json[csv_col])
            ]

            for idx, row in mismatches.iterrows():
                _add_anomaly(
                    anomalies,
                    record_id=row.get("session_id", idx),
                    field=col,
                    value=f"{row[json_col]} vs {row[csv_col]}",
                    anomaly_type="source_mismatch",
                    description=f"Clinical JSON and CSV values differ for field '{col}'.",
                    severity="medium"
                )

    # ------------------------------------------------------------------
    # Return anomalies as DataFrame
    # ------------------------------------------------------------------
    return pd.DataFrame(anomalies)
