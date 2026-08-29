import os
import pandas as pd

class CSVIngestion:
    """
    Generic CSV ingestion module for the DQIE pipeline.
    Loads CSV files from the Bronze Layer into Pandas DataFrames
    with consistent options and basic integrity checks.
    """

    def __init__(self, base_path="data/1-bronze/csv"):
        self.base_path = base_path

    def _full_path(self, filename):
        """Build full path for a CSV inside the Bronze Layer."""
        return os.path.join(self.base_path, filename)

    def load(self, filename):
        """
        Load a CSV file into a DataFrame with standard DQIE settings.
        Includes:
        - UTF-8 encoding
        - automatic NA parsing
        - dtype inference
        - basic file existence validation
        """
        full_path = self._full_path(filename)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"CSV not found: {full_path}")

        df = pd.read_csv(
            full_path,
            encoding="utf-8",
            na_values=["", " ", "NA", "N/A", None]
        )

        print(f"Loaded CSV: {filename}  |  Shape: {df.shape}")
        return df


if __name__ == "__main__":
    ingestion = CSVIngestion()

    # Example usage
    patients = ingestion.load("patients.csv")
    injuries = ingestion.load("injuries.csv")
    sessions = ingestion.load("sessions.csv")

    print("\nPreview:")
    print(patients.head())
