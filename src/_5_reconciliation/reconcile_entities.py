"""
Module: reconcile_entities
Clinical Data Quality Engine (DQIE) – Module 5: Reconciliation

This module reconciles entities across multiple data sources (CSV, SQL, OCR,
JSON clinical reports). It resolves conflicts, determines authoritative values,
and produces a unified reconciliation map for each clinical entity.

Output:
    A DataFrame containing reconciliation decisions:
        - entity_type (patient, injury, session)
        - entity_id
        - field
        - source_values (dict)
        - chosen_value
        - reconciliation_status
        - severity
        - notes
"""

import pandas as pd


# ----------------------------------------------------------------------
# Helper: choose authoritative value
# ----------------------------------------------------------------------
def _choose_value(values_dict):
    """
    Decide which source value should prevail.

    Priority order:
        1. SQL (most structured)
        2. CSV (primary ingestion)
        3. JSON (clinical reports)
        4. OCR text
        5. OCR image metadata

    If all values differ → mark as unresolved.
    """

    priority = ["sql", "csv", "json", "ocr_text", "ocr_image"]

    for source in priority:
        if source in values_dict and pd.notna(values_dict[source]):
            return values_dict[source]

    return None  # unresolved


# ----------------------------------------------------------------------
# Main reconciliation function
# ----------------------------------------------------------------------
def reconcile_entities(
    csv_data: pd.DataFrame,
    sql_data: pd.DataFrame,
    ocr_text: pd.DataFrame,
    clinical_json: pd.DataFrame = None,
    ocr_images: pd.DataFrame = None
) -> pd.DataFrame:
    """
    Reconciles entities across multiple sources.

    Parameters
    ----------
    csv_data : pd.DataFrame
    sql_data : pd.DataFrame
    ocr_text : pd.DataFrame
    clinical_json : pd.DataFrame, optional
    ocr_images : pd.DataFrame, optional

    Returns
    -------
    pd.DataFrame
        Reconciliation map for all entities.
    """

    reconciliation_rows = []

    # ------------------------------------------------------------------
    # Identify all unique sessions across sources
    # ------------------------------------------------------------------
    all_session_ids = set(csv_data["session_id"]) \
        | set(sql_data["session_id"]) \
        | set(ocr_text["session_id"])

    if clinical_json is not None and "session_id" in clinical_json.columns:
        all_session_ids |= set(clinical_json["session_id"])

    if ocr_images is not None and "session_id" in ocr_images.columns:
        all_session_ids |= set(ocr_images["session_id"])

    # ------------------------------------------------------------------
    # Reconcile each session
    # ------------------------------------------------------------------
    for session_id in sorted(all_session_ids):

        # Collect values from each source
        values = {}

        # CSV
        if session_id in csv_data["session_id"].values:
            row = csv_data[csv_data["session_id"] == session_id].iloc[0]
            values["csv"] = row.to_dict()

        # SQL
        if session_id in sql_data["session_id"].values:
            row = sql_data[sql_data["session_id"] == session_id].iloc[0]
            values["sql"] = row.to_dict()

        # OCR text
        if session_id in ocr_text["session_id"].values:
            row = ocr_text[ocr_text["session_id"] == session_id].iloc[0]
            values["ocr_text"] = row.to_dict()

        # Clinical JSON
        if clinical_json is not None and session_id in clinical_json["session_id"].values:
            row = clinical_json[clinical_json["session_id"] == session_id].iloc[0]
            values["json"] = row.to_dict()

        # OCR images
        if ocr_images is not None and session_id in ocr_images["session_id"].values:
            row = ocr_images[ocr_images["session_id"] == session_id].iloc[0]
            values["ocr_image"] = row.to_dict()

        # ------------------------------------------------------------------
        # Reconcile each field
        # ------------------------------------------------------------------
        all_fields = set()
        for source_dict in values.values():
            all_fields |= set(source_dict.keys())

        for field in sorted(all_fields):

            source_values = {
                src: src_dict.get(field)
                for src, src_dict in values.items()
            }

            chosen_value = _choose_value(source_values)

            # Determine reconciliation status
            unique_values = {v for v in source_values.values() if pd.notna(v)}

            if len(unique_values) <= 1:
                status = "consistent"
                severity = "low"
                notes = "All sources agree."
            elif chosen_value is None:
                status = "unresolved"
                severity = "high"
                notes = "Conflicting values across sources; no authoritative source."
            else:
                status = "resolved"
                severity = "medium"
                notes = f"Conflict resolved using authoritative source."

            reconciliation_rows.append({
                "entity_type": "session",
                "entity_id": session_id,
                "field": field,
                "source_values": source_values,
                "chosen_value": chosen_value,
                "reconciliation_status": status,
                "severity": severity,
                "notes": notes
            })

    # ------------------------------------------------------------------
    # Return reconciliation map
    # ------------------------------------------------------------------
    return pd.DataFrame(reconciliation_rows)
