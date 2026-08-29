import os
import json
from PIL import Image, ImageDraw, ImageFont

OCR_JSON_PATH = "data/_1_bronze/ocr/ocr_extracted.json"
IMAGES_DIR = "data/_1_bronze/images/ocr_reports"

def generate_real_ocr_images(json_path=OCR_JSON_PATH, images_dir=IMAGES_DIR):
    """Generate real PNG images with clinical OCR text."""

    # Load OCR JSON
    with open(json_path, "r", encoding="utf-8") as f:
        ocr_entries = json.load(f)

    os.makedirs(images_dir, exist_ok=True)

    for entry in ocr_entries:
        text = entry["extracted_text"]
        filename = f"ocr_report_{entry['ocr_id']}.png"
        path = os.path.join(images_dir, filename)

        # Create white background image
        img = Image.new("RGB", (900, 700), "white")
        draw = ImageDraw.Draw(img)

        # Draw text (simple, clean, OCR-friendly)
        draw.text((40, 40), text, fill="black")

        img.save(path)

    print(f"Generated {len(ocr_entries)} real OCR images at: {images_dir}")


if __name__ == "__main__":
    generate_real_ocr_images()
