# Clinical Data Quality Engine
Clinical Data Quality &amp; Integrity Engine (DQIE) — automated validation, reconciliation and scoring of healthcare datasets.

clinical-data-quality-engine/
│
├── dashboard/
│
├── data/
│   ├── _1__bronze/
│   │   ├── csv/
│   │   ├── images/ocr_reports
│   │   ├── ocr/
│   │   └── sql/
│   ├── _2__silver/
│   └── _3_gold/
│
├── docs/
│
├── notebooks/
│
├── src/
│   ├── _1_data_generation/
│   │   ├── __init__.py
│   │   ├── _1_generate_patients.py
│   │   ├── _2_generate_injuries.py
│   │   ├── _3_generate_sessions.py
│   │   ├── _4_generate_clinical_reports.py
│   │   ├── _5_generate_occr_reports.py
│   │   └── _6_generate_sql_tables.py
│   │
│   ├── _2_ingestion/
│   │   ├── __init__.py
│   │   ├── load_csv.py
│   │   ├── load_ocr_images.py
│   │   ├── load_ocr.py
│   │   └── load_sql.py
│   │ 
│   ├── _3_validation/
│   │   ├── __init__.py
│   │   ├── validate_business_rules.py
│   │   ├── validate_csv.py
│   │   ├── validate_ocr.py
│   │   ├── validate_relations.py
│   │   ├── validate_schema.py
│   │   ├── validate_sql.py
│   │
│   ├── _4_anomalies/
│   │   ├── __init__.py
│   │
│   ├── _5_reconciliation/
│   │   ├── __init__.py
│   │
│   ├── _6_scoring/
│   │   ├── __init__.py
│   │
│   └── main.py
│
├── tools/...
|
├── .gitignore
├── LICENSE
└── README.md

