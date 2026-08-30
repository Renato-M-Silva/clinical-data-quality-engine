import pandas as pd

class BusinessRulesValidator:
    """
    Clinical business rules validator for the DQIE pipeline.
    Ensures that patient rehabilitation data follows realistic
    clinical constraints and biomechanical expectations.

    Validates:
    - pain progression
    - mobility progression
    - session ordering
    - recovery time consistency
    - injury-type-specific expectations
    """

    def __init__(self):
        self.errors = []

    def _add_error(self, message):
        self.errors.append(message)

    # ---------------------------------------------------------
    # 1. Pain must decrease or stay stable (not increase absurdly)
    # ---------------------------------------------------------
    def validate_pain_progression(self, df):
        invalid = df[df["pain_final"] > df["pain_initial"] + 2]
        if len(invalid) > 0:
            self._add_error(
                f"{len(invalid)} patients show unrealistic pain increase (>2 points)."
            )

    # ---------------------------------------------------------
    # 2. Mobility must increase or stay stable (not decrease absurdly)
    # ---------------------------------------------------------
    def validate_mobility_progression(self, df):
        invalid = df[df["mobility_final"] < df["mobility_initial"] - 10]
        if len(invalid) > 0:
            self._add_error(
                f"{len(invalid)} patients show unrealistic mobility loss (>10 points)."
            )

    # ---------------------------------------------------------
    # 3. Recovery days must be positive
    # ---------------------------------------------------------
    def validate_recovery_days(self, df):
        invalid = df[df["recovery_days"] < 0]
        if len(invalid) > 0:
            self._add_error(
                f"{len(invalid)} patients have negative recovery_days."
            )

    # ---------------------------------------------------------
    # 4. Sessions must be consistent with injury type
    # ---------------------------------------------------------
    def validate_sessions_by_injury(self, df_sessions):
        rules = {
            "muscle": (5, 20),
            "ligament": (8, 25),
            "joint": (10, 30)
        }

        session_counts = df_sessions.groupby("patient_id").size().reset_index(name="session_count")

        merged = session_counts.merge(
            df_sessions[["patient_id", "injury_type"]].drop_duplicates(),
            on="patient_id",
            how="left"
        )

        for injury, (min_s, max_s) in rules.items():
            subset = merged[merged["injury_type"] == injury]
            invalid = subset[(subset["session_count"] < min_s) | (subset["session_count"] > max_s)]

            if len(invalid) > 0:
                self._add_error(
                    f"{len(invalid)} patients with {injury} injuries have unrealistic session counts "
                    f"(expected {min_s}-{max_s})."
                )

    # ---------------------------------------------------------
    # 5. Pain and mobility must be within valid ranges
    # ---------------------------------------------------------
    def validate_score_ranges(self, df):
        invalid_pain = df[
            (df["pain_initial"] < 0) | (df["pain_initial"] > 10) |
            (df["pain_final"] < 0) | (df["pain_final"] > 10)
        ]
        if len(invalid_pain) > 0:
            self._add_error(
                f"{len(invalid_pain)} rows have pain scores outside 0–10."
            )

        invalid_mob = df[
            (df["mobility_initial"] < 0) | (df["mobility_initial"] > 100) |
            (df["mobility_final"] < 0) | (df["mobility_final"] > 100)
        ]
        if len(invalid_mob) > 0:
            self._add_error(
                f"{len(invalid_mob)} rows have mobility scores outside 0–100."
            )




    # ---------------------------------------------------------
    # 6. Pain improvement and mobility gain must match raw scores
    # ---------------------------------------------------------
    def validate_kpi_consistency(self, df):
        # 1. Pain improvement must match raw scores
        invalid_pain = df[
            (df["pain_initial"] - df["pain_final"]) < 0
        ]
        if len(invalid_pain) > 0:
            self._add_error(
                f"{len(invalid_pain)} sessions show negative pain improvement (pain_final > pain_initial)."
            )

        # 2. Mobility gain must match raw scores
        invalid_mob = df[
            (df["mobility_final"] - df["mobility_initial"]) < 0
        ]
        if len(invalid_mob) > 0:
            self._add_error(
                f"{len(invalid_mob)} sessions show negative mobility gain (mobility_final < mobility_initial)."
            )


    # ---------------------------------------------------------
    # Run all validations
    # ---------------------------------------------------------
    def validate(self, df):
        self.validate_pain_progression(df)
        self.validate_mobility_progression(df)
        self.validate_recovery_days(df)
        self.validate_sessions_by_injury(df)
        self.validate_score_ranges(df)
        self.validate_kpi_consistency(df)

        return self.errors
    
# ---------------------------------------------------------
# Example usage
# ---------------------------------------------------------
if __name__ == "__main__":
    from src._2_ingestion.load_csv import CSVIngestion

    ingestion = CSVIngestion()
    df = ingestion.load("patients.csv")

    validator = BusinessRulesValidator()
    errors = validator.validate(df)

    print("\nBusiness Rules Errors:")
    print(errors)
