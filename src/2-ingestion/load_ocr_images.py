import os
import pandas as pd
import easyocr

class OCRImageIngestion:
    """
    Real OCR ingestion module using EasyOCR.
    Reads PNG images from the Bronze Layer and extracts text.
    Returns a DataFrame with:
    - image_path
    - extracted_text
    """

    def __init__(self, images_path="data/1-bronze/images/ocr_reports"):
        self.images_path = images_path
        self.reader = easyocr.Reader(["en"], gpu=False)

    def load_images(self):
        """List all PNG images in the OCR directory."""
        files = [
            f for f in os.listdir(self.images_path)
            if f.lower().endswith(".png")
        ]
        return files

    def extract_text(self, filename):
        """Run OCR on a single image."""
        full_path = os.path.join(self.images_path, filename)
        result = self.reader.readtext(full_path, detail=0)
        return "\n".join(result)

    def load(self):
        """Extract OCR text from all images and return a DataFrame."""
        images = self.load_images()

        rows = []
        for img in images:
            text = self.extract_text(img)
            rows.append({
                "image_file": img,
                "image_path": os.path.join(self.images_path, img),
                "extracted_text": text
            })

        df = pd.DataFrame(rows)
        print(f"Loaded OCR images: {len(df)}")
        return df


if __name__ == "__main__":
    ingestion = OCRImageIngestion()
    df = ingestion.load()
    print(df.head())
