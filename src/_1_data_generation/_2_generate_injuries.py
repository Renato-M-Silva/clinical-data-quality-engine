import os
import csv

# Output path inside Bronze Layer
OUTPUT_PATH = "data/_1_bronze/csv/injuries.csv"

# Synthetic physiotherapy injury profiles
INJURIES = [
    {
        "injury_type": "Rotator Cuff Tear",
        "typical_recovery_days": 60,
        "typical_sessions": 18,
        "typical_pain_initial": 7,
        "typical_mobility_initial": 40,
    },
    {
        "injury_type": "ACL Injury",
        "typical_recovery_days": 120,
        "typical_sessions": 24,
        "typical_pain_initial": 8,
        "typical_mobility_initial": 30,
    },
    {
        "injury_type": "Lumbar Disc Herniation",
        "typical_recovery_days": 90,
        "typical_sessions": 20,
        "typical_pain_initial": 7,
        "typical_mobility_initial": 35,
    },
    {
        "injury_type": "Cervical Radiculopathy",
        "typical_recovery_days": 75,
        "typical_sessions": 16,
        "typical_pain_initial": 6,
        "typical_mobility_initial": 45,
    },
    {
        "injury_type": "Ankle Sprain",
        "typical_recovery_days": 45,
        "typical_sessions": 10,
        "typical_pain_initial": 5,
        "typical_mobility_initial": 50,
    },
    {
        "injury_type": "Knee Osteoarthritis",
        "typical_recovery_days": 120,
        "typical_sessions": 20,
        "typical_pain_initial": 5,
        "typical_mobility_initial": 30,
    },
]

def generate_injuries(output_path=OUTPUT_PATH):
    """
    Generates a synthetic injuries dataset with realistic physiotherapy parameters.
    """

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write CSV
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            "injury_type",
            "typical_recovery_days",
            "typical_sessions",
            "typical_pain_initial",
            "typical_mobility_initial",
        ])

        # Rows
        for injury in INJURIES:
            writer.writerow([
                injury["injury_type"],
                injury["typical_recovery_days"],
                injury["typical_sessions"],
                injury["typical_pain_initial"],
                injury["typical_mobility_initial"],
            ])

    print(f"Generated injuries dataset at: {output_path}")


if __name__ == "__main__":
    generate_injuries()
