import pandas as pd

class OCRValidator:
    """
    OCR validation module for the DQIE pipeline.
    Validates both JSON-based OCR (synthetic) and real OCR extracted
    from images using EasyOCR.
    
    Checks include:
    - required fields
    - empty text
    - minimum text length
    - presence of clinical keywords
    - excessive OCR noise
    - structural consistency
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
    # 2. Validate empty or missing text
    # ---------------------------------------------------------
    def validate_empty_text(self, df, text_col, df_name):
        empty_rows = df[df[text_col].isnull() | (df[text_col].str.strip() == "")]
        if len(empty_rows) > 0:
            self._add_error(
                f"{df_name}: Empty OCR text found in {len(empty_rows)} rows"
            )

    # ---------------------------------------------------------
    # 3. Validate minimum text length
    # ---------------------------------------------------------
    def validate_min_length(self, df, text_col, min_len, df_name):
        short_rows = df[df[text_col].str.len() < min_len]
        if len(short_rows) > 0:
            self._add_error(
                f"{df_name}: OCR text shorter than {min_len} chars in "
                f"{len(short_rows)} rows"
            )

    # ---------------------------------------------------------
    # 4. Validate presence of clinical keywords
    # ---------------------------------------------------------
    def validate_keywords(self, df, text_col, keywords, df_name):
        missing_keywords = []
        for idx, row in df.iterrows():
            text = row[text_col].lower()
            if not any(k.lower() in text for k in keywords):
                missing_keywords.append(idx)

        if missing_keywords:
            self._add_error(
                f"{df_name}: Missing clinical keywords in rows: {missing_keywords}"
            )

    # ---------------------------------------------------------
    # 5. Validate OCR noise (real OCR only)
    # ---------------------------------------------------------
    def validate_noise(self, df, text_col, noise_chars, max_ratio, df_name):
        noisy_rows = []
        for idx, row in df.iterrows():
            text = row[text_col]
            if not isinstance(text, str):
                continue

            noise_count = sum(text.count(c) for c in noise_chars)
            ratio = noise_count / max(len(text), 1)

            if ratio > max_ratio:
                noisy_rows.append(idx)

        if noisy_rows:
            self._add_error(
                f"{df_name}: Excessive OCR noise in rows: {noisy_rows}"
            )

    # ---------------------------------------------------------
    # Run all validations
    # ---------------------------------------------------------
    def validate(self, df, df_name, text_col="extracted_text",
                required_cols=None, min_len=None,
                keywords=None, noise_chars=None, max_noise_ratio=None):

        if required_cols:
            self.validate_required_columns(df, required_cols, df_name)

        self.validate_empty_text(df, text_col, df_name)

        if min_len:
            self.validate_min_length(df, text_col, min_len, df_name)

        if keywords:
            self.validate_keywords(df, text_col, keywords, df_name)

        if noise_chars and max_noise_ratio:
            self.validate_noise(df, text_col, noise_chars, max_noise_ratio, df_name)

        return self.errors


# ---------------------------------------------------------
# Example usage
# ---------------------------------------------------------
if __name__ == "__main__":
    from src._2_ingestion.load_ocr import OCRIngestion
    from src._2_ingestion.load_ocr_images import OCRImageIngestion

    validator = OCRValidator()

    # JSON OCR (synthetic)
    json_df = OCRIngestion().load("ocr_extracted.json")
    json_errors = validator.validate(
        json_df,
        df_name="ocr_extracted.json",
        required_cols=["report_id", "patient_id", "extracted_text"],
        min_len=20,
        keywords=["pain", "mobility", "session", "treatment"]
    )

    print("\nJSON OCR Validation Errors:")
    print(json_errors)

    # Real OCR (EasyOCR)
    real_df = OCRImageIngestion().load()
    real_errors = validator.validate(
        real_df,
        df_name="ocr_images",
        required_cols=["image_file", "image_path", "extracted_text"],
        min_len=10,
        noise_chars=["#", "@", "%", "&", "*"],
        max_noise_ratio=0.15
    )

    print("\nReal OCR Validation Errors:")
    print(real_errors)
