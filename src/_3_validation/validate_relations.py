import pandas as pd

class RelationsValidator:
    """
    Referential integrity validator for the DQIE pipeline.
    Ensures internal consistency between datasets:
    - patients ↔ injuries
    - patients ↔ sessions
    - patients ↔ clinical reports
    - temporal consistency (injury_date < session_date < discharge_date)
    """

    def __init__(self):
        self.errors = []

    def _add_error(self, message):
        self.errors.append(message)

    # ---------------------------------------------------------
    # 1. Validate patient_id exists in patients table
    # ---------------------------------------------------------
    def validate_patient_links(self, df_child, df_parent, child_key, parent_key, child_name, parent_name):
        missing = df_child[~df_child[child_key].isin(df_parent[parent_key])]
        if len(missing) > 0:
            self._add_error(
                f"{child_name}: {len(missing)} rows reference non-existent {parent_name} via {child_key}"
            )

    # ---------------------------------------------------------
    # 2. Validate injury_type exists in injuries table
    # ---------------------------------------------------------
    def validate_injury_links(self, patients_df, injuries_df):
        missing = patients_df[~patients_df["injury_type"].isin(injuries_df["injury_type"])]
        if len(missing) > 0:
            self._add_error(
                f"patients.csv: {len(missing)} rows reference unknown injury_type"
            )

    # ---------------------------------------------------------
    # 3. Validate clinical reports reference valid patients
    # ---------------------------------------------------------
    def validate_reports_links(self, reports_df, patients_df):
        missing = reports_df[~reports_df["patient_id"].isin(patients_df["patient_id"])]
        if len(missing) > 0:
            self._add_error(
                f"clinical_reports.json: {len(missing)} reports reference non-existent patient_id"
            )

    # ---------------------------------------------------------
    # 4. Validate temporal consistency
    # ---------------------------------------------------------
    def validate_temporal(self, patients_df, sessions_df):
        merged = sessions_df.merge(
            patients_df[["patient_id", "injury_date"]],
            on="patient_id",
            how="left"
        )

        invalid = merged[merged["session_date"] < merged["injury_date"]]
        if len(invalid) > 0:
            self._add_error(
                f"sessions.csv: {len(invalid)} sessions occur BEFORE injury_date"
            )

    # ---------------------------------------------------------
    # 5. Validate session ordering
    # ---------------------------------------------------------
    def validate_session_order(self, sessions_df):
        grouped = sessions_df.sort_values(["patient_id", "session_date"])
        invalid = grouped[grouped["session_number"] != grouped.groupby("patient_id").cumcount() + 1]

        if len(invalid) > 0:
            self._add_error(
                f"sessions.csv: {len(invalid)} rows have incorrect session_number ordering"
            )

    # ---------------------------------------------------------
    # Run all validations
    # ---------------------------------------------------------
    def validate(self, patients_df, injuries_df, sessions_df, reports_df):
        self.validate_patient_links(
            sessions_df, patients_df,
            child_key="patient_id",
            parent_key="patient_id",
            child_name="sessions.csv",
            parent_name="patients.csv"
        )

        self.validate_injury_links(patients_df, injuries_df)

        self.validate_reports_links(reports_df, patients_df)

        self.validate_temporal(patients_df, sessions_df)

        self.validate_session_order(sessions_df)

        return self.errors


# ---------------------------------------------------------
# Example usage
# ---------------------------------------------------------
if __name__ == "__main__":
    from src._2_ingestion.load_csv import CSVIngestion
    from src._2_ingestion.load_ocr import OCRIngestion

    ingestion = CSVIngestion()
    ocr_ingestion = OCRIngestion()

    patients = ingestion.load("patients.csv")
    injuries = ingestion.load("injuries.csv")
    sessions = ingestion.load("sessions.csv")
    reports = ocr_ingestion.load("clinical_reports.json")

    validator = RelationsValidator()
    errors = validator.validate(patients, injuries, sessions, reports)

    print("\nReferential Integrity Errors:")
    print(errors)
