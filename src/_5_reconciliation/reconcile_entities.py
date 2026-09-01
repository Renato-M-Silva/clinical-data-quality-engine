"""
Module: reconcile_entities
Clinical Data Quality Engine (DQIE) – Module 5: Reconciliation

This module performs entity-level reconciliation across multiple data sources:
CSV, SQL, OCR text, OCR images, and JSON clinical reports.

For each entity (patient, session, injury, clinical_report, ocr_report, ocr_image),
the module compares values across sources, detects conflicts, and selects a
"chosen_value" using a priority rule.

Output:
    A DataFrame containing:
        - entity_type
        - entity_id
        - field
        - source_values
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
    Selects the best value among multiple sources using a priority rule.

    Priority order:
        1. SQL (most structured)
        2. CSV (primary ingestion)
        3. JSON (clinical reports)
        4. OCR text
        5. OCR image

    Returns
    -------
    chosen_value : any or None
    """
    priority = ["sql", "csv", "json", "ocr_text", "ocr_image"]
    for source in priority:
        if source in values_dict and pd.notna(values_dict[source]):
            return values_dict[source]
    return None


# ----------------------------------------------------------------------
# Helper: collect IDs from a dataframe
# ----------------------------------------------------------------------
def _collect_ids(df, id_col):
    """
    Extracts all unique IDs from a dataframe column.

    Returns
    -------
    set
    """
    return set(df[id_col]) if df is not None and id_col in df.columns else set()


# ----------------------------------------------------------------------
# Main reconciliation function
# ----------------------------------------------------------------------
def reconcile_entities(
    csv_data,
    sql_data,
    ocr_text,
    clinical_json=None,
    ocr_images=None
):
    """
    Performs entity-level reconciliation across all available sources.

    Entities reconciled:
        - patient
        - session
        - injury
        - clinical_report
        - ocr_report
        - ocr_image
    """

    rows = []

    # ==============================================================
    # 1. PATIENTS
    # ==============================================================

    patient_ids = (
        _collect_ids(csv_data, "patient_id")
        | _collect_ids(sql_data, "patient_id")
        | _collect_ids(ocr_text, "patient_id")
        | _collect_ids(clinical_json, "patient_id")
        | _collect_ids(ocr_images, "patient_id")
    )

    for pid in sorted(patient_ids):
        values = {}

        # Collect patient rows from each source
        for name, df in [
            ("csv", csv_data),
            ("sql", sql_data),
            ("ocr_text", ocr_text),
            ("json", clinical_json),
            ("ocr_image", ocr_images),
        ]:
            if df is not None and "patient_id" in df.columns:
                match = df[df["patient_id"] == pid]
                if len(match) > 0:
                    values[name] = match.iloc[0].to_dict()

        # Reconcile all fields for this patient
        fields = set().union(*[v.keys() for v in values.values()])
        for field in fields:

            src_vals = {src: d.get(field) for src, d in values.items()}
            chosen = _choose_value(src_vals)
            uniq = {v for v in src_vals.values() if pd.notna(v)}

            if len(uniq) <= 1:
                status, sev, notes = "consistent", "low", "All sources agree."
            elif chosen is None:
                status, sev, notes = "unresolved", "high", "Conflicting values across sources."
            else:
                status, sev, notes = "resolved", "medium", "Conflict resolved using priority rule."

            rows.append({
                "entity_type": "patient",
                "entity_id": pid,
                "field": field,
                "source_values": src_vals,
                "chosen_value": chosen,
                "reconciliation_status": status,
                "severity": sev,
                "notes": notes
            })

    # ==============================================================
    # 2. SESSIONS
    # ==============================================================

    session_ids = (
        _collect_ids(csv_data, "session_id")
        | _collect_ids(sql_data, "session_id")
        | _collect_ids(ocr_text, "session_id")
        | _collect_ids(clinical_json, "session_id")
        | _collect_ids(ocr_images, "session_id")
    )

    for sid in sorted(session_ids):
        values = {}

        for name, df in [
            ("csv", csv_data),
            ("sql", sql_data),
            ("ocr_text", ocr_text),
            ("json", clinical_json),
            ("ocr_image", ocr_images),
        ]:
            if df is not None and "session_id" in df.columns:
                match = df[df["session_id"] == sid]
                if len(match) > 0:
                    values[name] = match.iloc[0].to_dict()

        fields = set().union(*[v.keys() for v in values.values()])
        for field in fields:

            src_vals = {src: d.get(field) for src, d in values.items()}
            chosen = _choose_value(src_vals)
            uniq = {v for v in src_vals.values() if pd.notna(v)}

            if len(uniq) <= 1:
                status, sev, notes = "consistent", "low", "All sources agree."
            elif chosen is None:
                status, sev, notes = "unresolved", "high", "Conflicting values across sources."
            else:
                status, sev, notes = "resolved", "medium", "Conflict resolved using priority rule."

            rows.append({
                "entity_type": "session",
                "entity_id": sid,
                "field": field,
                "source_values": src_vals,
                "chosen_value": chosen,
                "reconciliation_status": status,
                "severity": sev,
                "notes": notes
            })

    # ==============================================================
    # 3. INJURIES
    # ==============================================================

    injury_ids = (
        _collect_ids(csv_data, "injury_id")
        | _collect_ids(sql_data, "injury_id")
        | _collect_ids(ocr_text, "injury_id")
        | _collect_ids(clinical_json, "injury_id")
        | _collect_ids(ocr_images, "injury_id")
    )

    for iid in sorted(injury_ids):
        values = {}

        for name, df in [
            ("csv", csv_data),
            ("sql", sql_data),
            ("ocr_text", ocr_text),
            ("json", clinical_json),
            ("ocr_image", ocr_images),
        ]:
            if df is not None and "injury_id" in df.columns:
                match = df[df["injury_id"] == iid]
                if len(match) > 0:
                    values[name] = match.iloc[0].to_dict()

        fields = set().union(*[v.keys() for v in values.values()])
        for field in fields:

            src_vals = {src: d.get(field) for src, d in values.items()}
            chosen = _choose_value(src_vals)
            uniq = {v for v in src_vals.values() if pd.notna(v)}

            if len(uniq) <= 1:
                status, sev, notes = "consistent", "low", "All sources agree."
            elif chosen is None:
                status, sev, notes = "unresolved", "high", "Conflicting values across sources."
            else:
                status, sev, notes = "resolved", "medium", "Conflict resolved using priority rule."

            rows.append({
                "entity_type": "injury",
                "entity_id": iid,
                "field": field,
                "source_values": src_vals,
                "chosen_value": chosen,
                "reconciliation_status": status,
                "severity": sev,
                "notes": notes
            })

    # ==============================================================
    # 4. CLINICAL REPORTS
    # ==============================================================

    if clinical_json is not None and "report_id" in clinical_json.columns:
        report_ids = _collect_ids(clinical_json, "report_id")

        for rid in sorted(report_ids):
            values = {"json": clinical_json[clinical_json["report_id"] == rid].iloc[0].to_dict()}

            fields = set(values["json"].keys())
            for field in fields:
                src_vals = {"json": values["json"].get(field)}
                chosen = src_vals["json"]

                rows.append({
                    "entity_type": "clinical_report",
                    "entity_id": rid,
                    "field": field,
                    "source_values": src_vals,
                    "chosen_value": chosen,
                    "reconciliation_status": "consistent",
                    "severity": "low",
                    "notes": "Single-source entity."
                })

    # ==============================================================
    # 5. OCR REPORTS
    # ==============================================================

    if ocr_text is not None and "ocr_id" in ocr_text.columns:
        ocr_ids = _collect_ids(ocr_text, "ocr_id")

        for oid in sorted(ocr_ids):
            values = {"ocr_text": ocr_text[ocr_text["ocr_id"] == oid].iloc[0].to_dict()}

            fields = set(values["ocr_text"].keys())
            for field in fields:
                src_vals = {"ocr_text": values["ocr_text"].get(field)}
                chosen = src_vals["ocr_text"]

                rows.append({
                    "entity_type": "ocr_report",
                    "entity_id": oid,
                    "field": field,
                    "source_values": src_vals,
                    "chosen_value": chosen,
                    "reconciliation_status": "consistent",
                    "severity": "low",
                    "notes": "Single-source entity."
                })

    # ==============================================================
    # 6. OCR IMAGES
    # ==============================================================

    if ocr_images is not None and "ocr_id" in ocr_images.columns:
        ocr_img_ids = _collect_ids(ocr_images, "ocr_id")

        for oid in sorted(ocr_img_ids):
            values = {"ocr_image": ocr_images[ocr_images["ocr_id"] == oid].iloc[0].to_dict()}

            fields = set(values["ocr_image"].keys())
            for field in fields:
                src_vals = {"ocr_image": values["ocr_image"].get(field)}
                chosen = src_vals["ocr_image"]

                rows.append({
                    "entity_type": "ocr_image",
                    "entity_id": oid,
                    "field": field,
                    "source_values": src_vals,
                    "chosen_value": chosen,
                    "reconciliation_status": "consistent",
                    "severity": "low",
                    "notes": "Single-source entity."
                })

    # ==============================================================
    # Final output
    # ==============================================================

    return pd.DataFrame(rows)
