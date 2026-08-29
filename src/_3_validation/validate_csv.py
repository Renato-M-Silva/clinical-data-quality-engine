import pandas as pd

class CSVValidator:
    """
    CSV validation module for the DQIE pipeline.
    Performs structural, type, null, duplicate, and range validations
    on CSV datasets loaded in the Silver Layer.
    """

    def __init__(self):
        self.errors = []

    def _add_error(self, message):
        self.errors.append(message)

    # ---------------------------------------------------------
    # 1. Validate required columns
    # ---------------------------------------------------------
    def validate_required_columns(self, df, required_cols, df_name):
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            self._add_error(
                f"{df_name}: Missing required columns: {missing}"
            )

    # ---------------------------------------------------------
    # 2. Validate column types
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
    # 3. Validate missing values
    # ---------------------------------------------------------
    def validate_missing(self, df, df_name):
        null_counts = df.isnull().sum()
        problematic = null_counts[null_counts > 0]
        if len(problematic) > 0:
            self._add_error(
                f"{df_name}: Missing values found in columns: "
                f"{problematic.to_dict()}"
            )

    # ---------------------------------------------------------
    # 4. Validate duplicates
    # ---------------------------------------------------------
    def validate_duplicates(self, df, key_cols, df_name):
        if df.duplicated(subset=key_cols).any():
            self._add_error(
                f"{df_name}: Duplicate rows found based on keys {key_cols}"
            )

    # ---------------------------------------------------------
    # 5. Validate numeric ranges
    # ---------------------------------------------------------
    def validate_ranges(self, df, range_rules, df_name):
        for col, (min_val, max_val) in range_rules.items():
            if col not in df.columns:
                continue
            if df[col].min() < min_val or df[col].max() > max_val:
                self._add_error(
                    f"{df_name}: Column '{col}' out of range "
                    f"(expected {min_val}–{max_val}, got "
                    f"{df[col].min()}–{df[col].max()})"
                )

    # ---------------------------------------------------------
    # Run all validations
    # ---------------------------------------------------------
    def validate(self, df, df_name, required_cols=None,
                expected_types=None, key_cols=None, range_rules=None):

        if required_cols:
            self.validate_required_columns(df, required_cols, df_name)

        if expected_types:
            self.validate_types(df, expected_types, df_name)

        self.validate_missing(df, df_name)

        if key_cols:
            self.validate_duplicates(df, key_cols, df_name)

        if range_rules:
            self.validate_ranges(df, range_rules, df_name)

        return self.errors


# ---------------------------------------------------------
# Example usage
# ---------------------------------------------------------
if __name__ == "__main__":
    from src._2_ingestion.load_csv import CSVIngestion

    ingestion = CSVIngestion()
    validator = CSVValidator()

    patients = ingestion.load("patients.csv")

    errors = validator.validate(
        patients,
        df_name="patients.csv",
        required_cols=["patient_id", "name", "age", "injury_type"],
        expected_types={"patient_id": "int64", "age": "int64"},
        key_cols=["patient_id"],
        range_rules={"age": (0, 120)}
    )

    print("\nValidation Errors:")
    print(errors)
