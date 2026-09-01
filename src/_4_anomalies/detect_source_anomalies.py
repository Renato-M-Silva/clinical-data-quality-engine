"""
Module: detect_source_anomalies
Clinical Data Quality Engine (DQIE) – Module 4: Anomalies

This module detects source-level anomalies across clinical datasets, including
inconsistencies between CSV, SQL, OCR, JSON clinical reports, and image-based
OCR extractions.

Output:
    A DataFrame containing all detected anomalies with:
        - record_id
        - entity_type
        - entity_id
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
def _add_anomaly(
    anomalies,
    record_id,
    entity_type,
    entity_id,
    field,
    value,
    anomaly_type,
    description,
    severity="medium"
):
    """
    Registers a source anomaly entry.

    Parameters
    ----------
    record_id : identifier of the record where the anomaly occurred
    entity_type : clinical entity type (session, patient, injury, report, ocr_report, ocr_image)
    entity_id : identifier of the affected entity
    field : field where the anomaly was detected
    value : problematic value
    anomaly_type : category of anomaly
    description : human-readable explanation
    severity : low / medium / high
    """
    anomalies.append({
        "record_id": record_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
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
    """
    Detects inconsistencies across multiple data sources.

    Entity type assignment follows the origin dataframe:
        - csv_data / sql_data / ocr_text referencing sessions → entity_type = "session"
        - csv_data / sql_data referencing patients → entity_type = "patient"
        - csv_data / sql_data referencing injuries → entity_type = "injury"
        - clinical_json → entity_type = "report"
        - ocr_text → entity_type = "ocr_report"
        - ocr_images → entity_type = "ocr_image"
    """

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

                    # Determine entity_type based on dataframe origin
                    if name in ["CSV", "SQL"]:
                        # CSV/SQL may contain sessions, patients, injuries
                        if "session_id" in row and pd.notna(row["session_id"]):
                            entity_type = "session"
                            entity_id = row["session_id"]
                        elif "patient_id" in row and pd.notna(row["patient_id"]):
                            entity_type = "patient"
                            entity_id = row["patient_id"]
                        elif "injury_type" in row and pd.notna(row["injury_type"]):
                            entity_type = "injury"
                            entity_id = row["injury_type"]
                        else:
                            entity_type = "unknown"
                            entity_id = idx

                    elif name == "OCR Text":
                        entity_type = "ocr_report"
                        entity_id = row.get("ocr_id", idx)

                    elif name == "OCR Images":
                        entity_type = "ocr_image"
                        entity_id = row.get("ocr_id", idx)

                    elif name == "Clinical JSON":
                        entity_type = "report"
                        entity_id = row.get("report_id", idx)

                    else:
                        entity_type = "unknown"
                        entity_id = idx

                    _add_anomaly(
                        anomalies,
                        record_id=entity_id,
                        entity_type=entity_type,
                        entity_id=entity_id,
                        field=field,
                        value=None,
                        anomaly_type="missing_value",
                        description=f"Field '{field}' missing in {name}."
                    )

    # --------------------------------------------------------------
    # 2. OCR referencing missing patients
    # --------------------------------------------------------------
    missing = ocr_text[~ocr_text["patient_id"].isin(csv_data["patient_id"])]
    for idx, row in missing.iterrows():
        _add_anomaly(
            anomalies,
            record_id=row["ocr_id"],
            entity_type="ocr_report",
            entity_id=row["ocr_id"],
            field="patient_id",
            value=row["patient_id"],
            anomaly_type="missing_reference",
            description="OCR references non-existent patient."
        )

    # --------------------------------------------------------------
    # 3. OCR images without OCR text
    # --------------------------------------------------------------
    if ocr_images is not None:
        if "ocr_id" in ocr_images.columns and "ocr_id" in ocr_text.columns:

            # OCR image missing text
            missing_text = ocr_images[~ocr_images["ocr_id"].isin(ocr_text["ocr_id"])]
            for idx, row in missing_text.iterrows():
                _add_anomaly(
                    anomalies,
                    record_id=row["ocr_id"],
                    entity_type="ocr_image",
                    entity_id=row["ocr_id"],
                    field="ocr_id",
                    value=row["ocr_id"],
                    anomaly_type="missing_text",
                    description="OCR image has no corresponding OCR text."
                )

            # OCR text missing image
            missing_image = ocr_text[~ocr_text["ocr_id"].isin(ocr_images["ocr_id"])]
            for idx, row in missing_image.iterrows():
                _add_anomaly(
                    anomalies,
                    record_id=row["ocr_id"],
                    entity_type="ocr_report",
                    entity_id=row["ocr_id"],
                    field="ocr_id",
                    value=row["ocr_id"],
                    anomaly_type="missing_image",
                    description="OCR text has no corresponding OCR image."
                )

    return pd.DataFrame(anomalies)
