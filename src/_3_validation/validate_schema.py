import pandas as pd

class SchemaValidator:
    """
    Schema validation module for the DQIE pipeline.
    Ensures that each dataset follows the expected structure:
    - required columns
    - no unexpected columns
    - correct data types
    """

    def __init__(self):
        self.errors = []

    def _add_error(self, message):
        self.errors.append(message)

    # ---------------------------------------------------------
    # 1. Validate required columns
    # ---------------------------------------------------------
    def validate_required_columns(self, df, expected_cols, df_name):
        missing = [col for col in expected_cols if col not in df.columns]
        if missing:
            self._add_error(
                f"{df_name}: Missing required columns: {missing}"
            )

    # ---------------------------------------------------------
    # 2. Validate unexpected columns
    # ---------------------------------------------------------
    def validate_unexpected_columns(self, df, expected_cols, df_name):
        unexpected = [col for col in df.columns if col not in expected_cols]
        if unexpected:
            self._add_error(
                f"{df_name}: Unexpected columns found: {unexpected}"
            )

    # ---------------------------------------------------------
    # 3. Validate column types
    # ---------------------------------------------------------
    def validate_types(self, df, expected_types, df_name):
        for col, expected_type in expected_types.items():
            if col not in df.columns:
                continue
            if not pd.api.types.is_dtype_equal(df[col].dtype, expected_type):
                self._add_error(
                    f"{df_name}: Column '{col}' has wrong dtype "
                    f"(expected {expected_type}, got {df[col].dtype})"
                )

    # ---------------------------------------------------------
    # Run all validations
    # ---------------------------------------------------------
    def validate(self, df, df_name, expected_cols, expected_types=None):

        self.validate_required_columns(df, expected_cols, df_name)
        self.validate_unexpected_columns(df, expected_cols, df_name)

        if expected_types:
            self.validate_types(df, expected_types, df_name)

        return self.errors


# ---------------------------------------------------------
# Example usage
# ---------------------------------------------------------
if __name__ == "__main__":
    from src._2_ingestion.load_csv import CSVIngestion

    ingestion = CSVIngestion()
    validator = SchemaValidator()

    patients_df = ingestion.load("patients.csv")

    expected_cols = [
        "patient_id", "name", "age", "injury_type",
        "injury_date", "discharge_date"
    ]

    expected_types = {
        "patient_id": "int64",
        "age": "int64",
        "injury_type": "object"
    }

    errors = validator.validate(
        patients_df,
        df_name="patients.csv",
        expected_cols=expected_cols,
        expected_types=expected_types
    )

    print("\nSchema Validation Errors:")
    print(errors)
