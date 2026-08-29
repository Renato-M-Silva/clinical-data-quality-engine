import os
import json
import pandas as pd

class OCRIngestion:
    """
    OCR ingestion module for the DQIE pipeline.
    Loads JSON OCR files from the Bronze Layer and returns Pandas DataFrames.
    Handles:
    - clinical_reports.json
    - ocr_extracted.json
    """

    def __init__(self, base_path="data/_1_bronze/ocr"):
        self.base_path = base_path

    def _full_path(self, filename):
        """Build full path for a JSON file inside the Bronze Layer."""
        return os.path.join(self.base_path, filename)

    def load(self, filename):
        """
        Load a JSON OCR file into a DataFrame.
        Includes:
        - file existence validation
        - JSON parsing
        - conversion to DataFrame
        """
        full_path = self._full_path(filename)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"OCR JSON not found: {full_path}")

        with open(full_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        df = pd.DataFrame(data)

        print(f"Loaded OCR JSON: {filename}  |  Shape: {df.shape}")
        return df


if __name__ == "__main__":
    ingestion = OCRIngestion()

    clinical_df = ingestion.load("clinical_reports.json")
    ocr_df = ingestion.load("ocr_extracted.json")

    print("\nPreview:")
    print(clinical_df.head())
