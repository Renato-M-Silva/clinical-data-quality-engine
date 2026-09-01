# Clinical Data Quality & Integrity Engine (DQIE)

**Automated validation, reconciliation, and scoring of healthcare datasets**

A comprehensive Python-based engine designed to identify data quality issues, reconcile multi-source clinical information, and generate quantified quality scores for healthcare datasets. Built for healthcare professionals, data engineers, and analysts working with clinical datasets across multiple formats (CSV, SQL, OCR).

---

## 🎯 Overview

The **Clinical Data Quality & Integrity Engine** automates the end-to-end workflow for healthcare data quality assurance:

- **Data Ingestion**: Load and normalize data from multiple sources (CSV, databases, OCR extractions)
- **Schema & Business Rules Validation**: Enforce structural and domain-specific constraints
- **Anomaly Detection**: Identify outliers, inconsistencies, and violations across datasets
- **Multi-Source Reconciliation**: Cross-reference entities across CSV, SQL, and OCR sources to resolve conflicts
- **DQI Scoring**: Generate quantified quality scores at both entity and dataset levels
- **Dashboard Export**: Prepare clean datasets for visualization and reporting

### Key Features

✅ **Multi-Format Support**: CSV, SQL databases, OCR text extraction, and image processing  
✅ **Hierarchical Data Staging**: Bronze → Silver → Gold data lake architecture  
✅ **Realistic Anomaly Injection**: Generate test datasets with 7+ types of quality issues  
✅ **Modular Pipeline**: Run full pipeline or individual stages independently  
✅ **Comprehensive Validation**: Schema, business rules, relationships, and OCR-specific checks  
✅ **Jupyter Notebook Integration**: Interactive exploration and notebook-based execution  

---

## 🏗️ Architecture

### Stack
- **Language**: Python 74.5% | Jupyter Notebook 25.5%
- **Framework**: Pandas, SQLAlchemy
- **Computer Vision**: EasyOCR, OpenCV, PyTorch, scikit-image, Pillow
- **Data Processing**: NumPy, Shapely, NetworkX, SciPy

### Project Structure

```
clinical-data-quality-engine/
│
├── src/
│   ├── _1_data_generation/          # Synthetic dataset creation with realistic anomalies
│   │   ├── _1_generate_patients.py
│   │   ├── _2_generate_injuries.py
│   │   ├── _3_generate_sessions.py
│   │   ├── _4_generate_clinical_reports.py
│   │   ├── _5_generate_ocr_reports.py
│   │   └── _6_generate_sql_tables.py
│   │
│   ├── _2_ingestion/                # Data loading and normalization
│   │   ├── load_csv.py              # CSV ingestion with NA handling
│   │   ├── load_ocr.py              # OCR text extraction
│   │   ├── load_ocr_images.py       # OCR image processing
│   │   └── load_sql.py              # SQL database queries
│   │
│   ├── _3_validation/               # Multi-layer validation framework
│   │   ├── validate_schema.py       # Column structure & dtype checks
│   │   ├── validate_business_rules.py
│   │   ├── validate_relations.py    # Foreign key & referential integrity
│   │   ├── validate_csv.py
│   │   ├── validate_ocr.py
│   │   └── validate_sql.py
│   │
│   ├── _4_anomalies/                # Anomaly detection engine
│   │   └── anomaly_engine.py        # Pattern-based outlier detection
│   │
│   ├── _5_reconciliation/           # Multi-source entity matching
│   │   └── reconciliation_engine.py
│   │
│   ├── _6_scoring/                  # Data Quality Index calculation
│   │   └── scoring_engine.py        # Entity & dataset-level scoring
│   │
│   └── main.py                      # Pipeline orchestrator
│
├── data/
│   ├── _1_bronze/                   # Raw data layer
│   │   ├── csv/
│   │   ├── sql/
│   │   ├── ocr/
│   │   └── images/ocr_reports
│   │
│   ├── _2_silver/                   # Cleaned & normalized layer
│   │   └── *.parquet files
│   │
│   └── _3_gold/                     # Business-ready layer
│       ├── anomalies/
│       ├── reconciliation/
│       ├── scoring/
│       └── dashboard/
│
├── notebooks/                        # Jupyter analysis & execution notebooks
│   ├── 01_ingestion_validation.ipynb
│   ├── 02_schema_validation.ipynb
│   ├── 03_anomaly_detection.ipynb
│   ├── 04_reconciliation.ipynb
│   ├── 05_dqi_scoring.ipynb
│   └── 06_dashboard_export.ipynb
│
├── dashboard/                        # Dashboard configuration & templates
│
├── requirements.txt
├── LICENSE (MIT)
└── README.md
```

### Data Flow

```
Bronze Layer (Raw)
    ↓ [Ingestion]
Silver Layer (Cleaned)
    ↓ [Validation + Anomaly Detection]
Gold Layer (Business-Ready)
    ├── /anomalies      (detected issues)
    ├── /reconciliation (cross-source matches)
    ├── /scoring        (DQI results)
    └── /dashboard      (visualization-ready)
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip or conda

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Renato-M-Silva/clinical-data-quality-engine.git
   cd clinical-data-quality-engine
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate sample data** (optional)
   ```bash
   python src/_1_data_generation/_1_generate_patients.py
   python src/_1_data_generation/_2_generate_injuries.py
   python src/_1_data_generation/_3_generate_sessions.py
   # ... run remaining generators
   ```

### Run the Full Pipeline

```bash
# Run all stages (Bronze → Silver → Gold)
python src/main.py --stage all

# Or run individual stages
python src/main.py --stage anomalies
python src/main.py --stage reconciliation
python src/main.py --stage scoring
python src/main.py --stage dashboard
```

### Interactive Exploration

Open and run notebooks in order:

```bash
jupyter notebook notebooks/01_ingestion_validation.ipynb
jupyter notebook notebooks/02_schema_validation.ipynb
jupyter notebook notebooks/03_anomaly_detection.ipynb
# ... and so on
```

---

## 📊 Module Details

### 1. Data Generation (`_1_data_generation/`)
Creates realistic synthetic clinical datasets with injected anomalies:
- **Patients**: Personal info, injury types, recovery dates
- **Injuries**: Medical codes (ICD), diagnosis categories, severity
- **Sessions**: Treatment sessions, physiotherapy records
- **Clinical Reports**: Structured medical notes and observations
- **OCR Reports**: Text extracted from document scans
- **SQL Tables**: Relational schema with referential integrity

**Anomaly Types** (8% injection rate):
- Negative ages
- Future start dates
- Logical inconsistencies (end before start)
- Invalid categorical values
- Missing required fields
- Duplicate IDs

### 2. Ingestion (`_2_ingestion/`)
Loads multi-format data with consistent handling:
- **CSV**: UTF-8 encoding, NA parsing, dtype inference
- **SQL**: Query-based extraction with SQLAlchemy
- **OCR**: Text extraction from images via EasyOCR
- **Images**: Direct image loading for OCR processing

### 3. Validation (`_3_validation/`)
Multi-layer validation framework:
- **Schema**: Required columns, unexpected columns, dtype verification
- **Business Rules**: Domain-specific constraints (age ranges, date logic)
- **Relations**: Foreign key checks, referential integrity
- **Format-Specific**: CSV, SQL, OCR, image validations

### 4. Anomaly Detection (`_4_anomalies/`)
Identifies outliers and inconsistencies:
- Statistical outliers (age, dates, durations)
- Logical violations (end < start, negative values)
- Referential integrity issues
- Cross-dataset inconsistencies

### 5. Reconciliation (`_5_reconciliation/`)
Matches and resolves entities across sources:
- Patient ID cross-references
- Duplicate detection and merging
- Conflict resolution strategies
- Multi-source reliability scoring

### 6. Scoring (`_6_scoring/`)
Generates quantified data quality metrics:
- **Entity-Level**: Quality score per patient/record (0-100)
- **Dataset-Level**: Overall DQI with anomaly density
- **Severity Distribution**: Breakdown of anomaly types and counts
- **Source Reliability**: Confidence in each data source

---

## 📈 Outputs

After running the full pipeline, explore results in `data/_3_gold/`:

### Anomalies
```
data/_3_gold/anomalies/
├── patients_anomalies.parquet
├── injuries_anomalies.parquet
├── sessions_anomalies.parquet
└── cross_source_anomalies.parquet
```

### Reconciliation
```
data/_3_gold/reconciliation/
├── entities_reconciliation.parquet  (matched records)
└── anomalies_summary.parquet        (aggregated issues)
```

### Scoring
```
data/_3_gold/scoring/
├── entity_scores.parquet            (per-record DQI)
└── dataset_score.json               (global metrics)
```

### Dashboard
```
data/_3_gold/dashboard/
├── entity_scores.parquet
├── dataset_score.parquet
├── severity_distribution.parquet
└── score_by_entity_type.parquet
```

---

## 🛠️ Configuration

Environment variables (optional):

```bash
# .env file or environment
OCR_MODEL=easyocr          # OCR model type
DATABASE_URL=...           # SQL connection string
DATA_PATH=data/            # Root data directory
ANOMALY_THRESHOLD=0.05     # Anomaly detection sensitivity
```

---

## 📚 Dependencies

Core packages:

```
pandas==3.0.5              # Data manipulation
numpy==2.4.6               # Numerical computing
SQLAlchemy==2.0.52         # Database ORM
PyYAML==6.0.3              # Configuration

# Computer Vision & OCR
easyocr==1.7.2
opencv-python-headless==5.0.0.93
torch==2.13.0
torchvision==0.28.0
scikit-image==0.26.0
pillow==12.3.0

# Utilities
scikit-image==0.26.0
shapely==2.1.2
networkx==3.6.1
python-dotenv==1.2.3
```

See `requirements.txt` for full dependency list.

---

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:

- Additional anomaly detection algorithms
- Real dataset adapters (EHR systems)
- Dashboard UI implementation
- Performance optimizations for large datasets
- Automated testing & CI/CD

Please submit issues and pull requests.

---

## 📄 License

MIT License — See [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Renato M. Silva**  
📧 Contact: [GitHub Profile](https://github.com/Renato-M-Silva)

---

## 🗂️ Quick Reference

| Task | Command |
|------|---------|
| Generate synthetic data | `python src/_1_data_generation/_*.py` |
| Run full pipeline | `python src/main.py --stage all` |
| Run anomaly detection only | `python src/main.py --stage anomalies` |
| Explore data interactively | `jupyter notebook notebooks/` |
| Install dependencies | `pip install -r requirements.txt` |

---

**Last Updated**: September 2026  
**Status**: Active Development

---

*Built for healthcare data engineers, quality analysts, and clinical informaticists.*
