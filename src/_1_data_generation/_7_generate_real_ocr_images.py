import os
import json
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

OCR_JSON_PATH = "data/_1_bronze/ocr/ocr_extracted.json"
IMAGES_DIR = "data/_1_bronze/images/ocr_reports"

LIGHT_ANOMALY_RATE = 0.10   # 10% light anomalies
HEAVY_ARTIFACT_RATE = 0.20  # 20% heavy artifacts


def add_noise(draw, width, height):
    """Add random noise points to the image."""
    for _ in range(random.randint(80, 250)):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        draw.point((x, y), fill="black")


def add_horizontal_lines(draw, width, height):
    """Add faint horizontal lines simulating scanner artifacts."""
    for _ in range(random.randint(2, 6)):
        y = random.randint(0, height - 1)
        draw.line((0, y, width, y), fill="gray", width=1)


def add_coffee_stain(img):
    """Add a circular brownish stain."""
    stain = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(stain)
    x = random.randint(100, 700)
    y = random.randint(100, 500)
    radius = random.randint(80, 160)
    draw.ellipse(
        (x - radius, y - radius, x + radius, y + radius),
        fill=(150, 100, 50, random.randint(40, 90))
    )
    return Image.alpha_composite(img.convert("RGBA"), stain).convert("RGB")


def add_vignette(img):
    """Add dark vignette around edges."""
    width, height = img.size
    vignette = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(vignette)
    draw.ellipse(
        (-width * 0.3, -height * 0.3, width * 1.3, height * 1.3),
        fill=255
    )
    vignette = vignette.filter(ImageFilter.GaussianBlur(80))
    return ImageOps.colorize(vignette, black="black", white="white").convert("RGB")


def add_paper_bleed(img):
    """Simulate ink bleed-through from the back of the page."""
    bleed = img.filter(ImageFilter.GaussianBlur(radius=8))
    bleed = bleed.point(lambda p: p * 0.6)
    return Image.blend(img, bleed, alpha=0.4)


def add_jpeg_compression(img):
    """Simulate heavy JPEG compression artifacts."""
    temp_path = "temp_compressed.jpg"
    img.save(temp_path, "JPEG", quality=random.randint(10, 40))
    return Image.open(temp_path)


def add_diagonal_cut(img):
    """Add a diagonal white cut across the image."""
    draw = ImageDraw.Draw(img)
    width, height = img.size
    draw.line(
        (0, random.randint(0, height), width, random.randint(0, height)),
        fill="white",
        width=random.randint(20, 60)
    )
    return img


def generate_real_ocr_images(json_path=OCR_JSON_PATH, images_dir=IMAGES_DIR):
    """Generate real PNG images with clinical OCR text and visual anomalies."""

    with open(json_path, "r", encoding="utf-8") as f:
        ocr_entries = json.load(f)

    os.makedirs(images_dir, exist_ok=True)

    for entry in ocr_entries:
        text = entry["extracted_text"]
        filename = f"ocr_report_{entry['ocr_id']}.png"
        path = os.path.join(images_dir, filename)

        width, height = 900, 700
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)

        # Draw text normally
        draw.text((40, 40), text, fill="black")

        # ------------------------------------------------------
        # LIGHT ANOMALIES (10%)
        # ------------------------------------------------------
        if random.random() < LIGHT_ANOMALY_RATE:
            anomaly = random.choice([
                "noise",
                "blur",
                "cut_text",
                "rotate",
                "horizontal_lines",
                "low_contrast",
                "double_text",
                "partial_text"
            ])

            if anomaly == "noise":
                add_noise(draw, width, height)

            elif anomaly == "blur":
                img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(1.0, 3.5)))

            elif anomaly == "cut_text":
                draw.rectangle((40, 40, 500, 120), fill="white")

            elif anomaly == "rotate":
                img = img.rotate(random.uniform(-5, 5), expand=False)

            elif anomaly == "horizontal_lines":
                add_horizontal_lines(draw, width, height)

            elif anomaly == "low_contrast":
                img = img.point(lambda p: p * 0.7)

            elif anomaly == "double_text":
                draw.text((45, 45), text, fill="gray")

            elif anomaly == "partial_text":
                short_text = text[:random.randint(20, 60)]
                img = Image.new("RGB", (width, height), "white")
                draw = ImageDraw.Draw(img)
                draw.text((40, 40), short_text, fill="black")

        # ------------------------------------------------------
        # HEAVY ARTIFACTS (20%)
        # ------------------------------------------------------
        if random.random() < HEAVY_ARTIFACT_RATE:
            artifact = random.choice([
                "coffee_stain",
                "vignette",
                "paper_bleed",
                "jpeg_compression",
                "diagonal_cut"
            ])

            if artifact == "coffee_stain":
                img = add_coffee_stain(img)

            elif artifact == "vignette":
                img = add_vignette(img)

            elif artifact == "paper_bleed":
                img = add_paper_bleed(img)

            elif artifact == "jpeg_compression":
                img = add_jpeg_compression(img)

            elif artifact == "diagonal_cut":
                img = add_diagonal_cut(img)

        img.save(path)

    print(f"Generated {len(ocr_entries)} OCR images with mixed anomalies at: {images_dir}")


if __name__ == "__main__":
    generate_real_ocr_images()
