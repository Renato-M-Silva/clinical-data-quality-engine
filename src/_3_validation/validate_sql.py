import pandas as pd

class SQLValidator:
    """
    SQL validation module for the DQIE pipeline.
    Performs schema validation, type checking, null detection,
    primary key integrity, and record count checks on SQL tables
    loaded into DataFrames.
    """

    def __init__(self):
        self.errors = []

    def _add_error(self, message):
        self.errors.append(message)

    # ---------------------------------------------------------
    # 1. Validate required columns
    # ---------------------------------------------------------
    def validate_required_columns(self, df, required_cols, table_name):
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            self._add_error(
                f"{table_name}: Missing required columns: {missing}"
            )

    # ---------------------------------------------------------
    # 2. Validate column types
    # ---------------------------------------------------------
    def validate_types(self, df, expected_types, table_name):
        for col, expected_type in expected_types.items():
            if col not in df.columns:
                continue
            if not pd.api.types.is_dtype_equal(df[col].dtype, expected_type):
                self._add_error(
                    f"{table_name}: Column '{col}' has wrong dtype "
                    f"(expected {expected_type}, got {df[col].dtype})"
                )

    # ---------------------------------------------------------
    # 3. Validate missing values
    # ---------------------------------------------------------
    def validate_missing(self, df, table_name):
        null_counts = df.isnull().sum()
        problematic = null_counts[null_counts > 0]
        if len(problematic) > 0:
            self._add_error(
                f"{table_name}: Missing values found in columns: "
                f"{problematic.to_dict()}"
            )

    # ---------------------------------------------------------
    # 4. Validate primary key uniqueness
    # ---------------------------------------------------------
    def validate_primary_key(self, df, key_cols, table_name):
        if df.duplicated(subset=key_cols).any():
            self._add_error(
                f"{table_name}: Duplicate primary key rows found "
                f"based on keys {key_cols}"
            )

    # ---------------------------------------------------------
    # 5. Validate record count
    # ---------------------------------------------------------
    def validate_record_count(self, df, min_rows, table_name):
        if len(df) < min_rows:
            self._add_error(
                f"{table_name}: Too few rows (expected at least {min_rows}, got {len(df)})"
            )

    # ---------------------------------------------------------
    # Run all validations
    # ---------------------------------------------------------
    def validate(self, df, table_name,
                required_cols=None, expected_types=None,
                key_cols=None, min_rows=None):

        if required_cols:
            self.validate_required_columns(df, required_cols, table_name)

        if expected_types:
            self.validate_types(df, expected_types, table_name)

        self.validate_missing(df, table_name)

        if key_cols:
            self.validate_primary_key(df, key_cols, table_name)

        if min_rows:
            self.validate_record_count(df, min_rows, table_name)

        return self.errors


# ---------------------------------------------------------
# Example usage
# ---------------------------------------------------------
if __name__ == "__main__":
    from src._2_ingestion.load_sql import SQLIngestion

    ingestion = SQLIngestion()
    validator = SQLValidator()

    patients_df = ingestion.load("patients.sql")

    errors = validator.validate(
        patients_df,
        table_name="patients",
        required_cols=["patient_id", "name", "age", "injury_type"],
        expected_types={"patient_id": "int64", "age": "int64"},
        key_cols=["patient_id"],
        min_rows=10
    )

    print("\nValidation Errors:")
    print(errors)
