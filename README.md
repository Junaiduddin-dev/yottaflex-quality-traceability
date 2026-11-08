# YottaFlex – Manufacturing Quality & Defect Traceability System

## 1. Project Overview

The YottaFlex Manufacturing Quality & Defect Traceability System is a Python-based synthetic manufacturing data and traceability project.

It models manufacturing operations and enables defects to be traced across:

- Products and Bills of Materials (BOMs)
- Suppliers and material lots
- Production orders and material consumption
- Machines and process execution
- Inspection plans and inspection results
- Defects and Corrective and Preventive Actions (CAPA)

The project also includes synthetic anomaly scenarios, ground-truth labels, business-rule validation, structured data exports, and reproducibility checks.

## 2. Project Objectives

- Build a relational manufacturing database.
- Generate realistic synthetic manufacturing data.
- Maintain traceability between defects, inspections, production orders, machines, material lots, and suppliers.
- Represent corrective actions and verification lifecycles.
- Detect data-quality and traceability anomalies.
- Export datasets in CSV, JSON, and SQL formats.
- Validate database integrity and business rules.
- Support reproducible dataset exports using SHA-256 checksums.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application and data generation |
| SQLite | Relational database |
| SQLAlchemy | ORM and database operations |
| Faker | Synthetic data generation |
| CSV | Tabular data export |
| JSON | Structured data export |
| SQL | Database dump |
| SHA-256 | File integrity and reproducibility checks |
| Git | Version control |

## 4. Project Structure

```text
yottaflex-quality-traceability/
│
├── app/
│
├── database/
│   ├── connection.py
│   ├── models.py
│   ├── init_db.py
│   ├── check_db.py
│   └── seed_sample.py
│
├── generator/
│   ├── config.py
│   ├── master_data.py
│   ├── production_data.py
│   ├── inspection_data.py
│   ├── capa_data.py
│   ├── anomaly_data.py
│   └── export_data.py
│
├── validation/
│   ├── traceability_check.py
│   ├── business_rules.py
│   ├── capa_validation.py
│   ├── capa_data_check.py
│   ├── anomaly_tests.py
│   ├── production_data_check.py
│   ├── check_quality_counts.py
│   ├── export_check.py
│   └── reproducibility_check.py
│
├── data/
│   ├── csv/
│   ├── json/
│   ├── sql/
│   └── ground_truth/
│
├── docs/
│   ├── data_dictionary.md
│   ├── erd.md
│   └── export_checksums.sha256
│
├── prompt_history/
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```

## 5. Database Design

The database contains 15 relational tables.

| Table | Description |
|---|---|
| products | Product master information |
| suppliers | Supplier master information |
| machines | Manufacturing machine information |
| boms | Product Bill of Materials |
| bom_lines | Individual BOM material requirements |
| material_lots | Supplier-linked material batches |
| production_orders | Manufacturing production orders |
| material_consumptions | Materials consumed by production orders |
| process_steps | Manufacturing process steps |
| order_machine_executions | Machine execution records |
| inspection_plans | Product inspection specifications |
| inspection_results | Inspection measurements and outcomes |
| defects | Manufacturing quality defects |
| corrective_actions | Corrective and preventive action records |
| audit_events | Entity event and change history |

Refer to `docs/data_dictionary.md` and `docs/erd.md` for detailed schema documentation.

## 6. Synthetic Dataset

The dataset was generated using the fixed project seed configured in `generator/config.py`.

**Dataset configuration**

| Entity | Target quantity |
|---|---:|
| Products | 200 |
| Suppliers | 50 |
| Machines | 30 |
| BOMs | 200 |
| BOM lines | 808 |
| Material lots | 2,000 |
| Production orders | 5,000 |
| Material consumption records | 21,203 |
| Process steps | 15,000 |
| Machine executions | 15,000 |
| Inspection plans | 600 |
| Inspection results | 20,000 |
| Defects | 3,979 |
| Corrective actions | 3,979 |
| Audit events | 0 |

The exported database contains **88,049 records** across 15 tables.

Dataset date range: 2025-01-01 to 2026-10-22.

## 7. Defect Traceability

The system supports tracing a defect through the following relationships:

```text
Product
   |
Production Order
   |
Inspection Result
   |
Defect
   |
Production Order / Process Execution
   |
Machine
   |
Material Consumption
   |
Material Lot
   |
Supplier
   |
Corrective Action
```

Traceability validation checks the relationships between defects, inspections, production orders, process execution, machines, material lots, and suppliers.

## 8. Anomaly Scenarios

Five synthetic anomaly cases are maintained separately from the operational database.

| Anomaly | Description |
|---|---|
| NONEXISTENT_MATERIAL_LOT | Defect references a material lot that does not exist |
| BOM_MATERIAL_NOT_CONSUMED | BOM-required material has no consumption record |
| CAPA_CLOSED_BEFORE_VERIFICATION | CAPA is closed before successful verification |
| DEFECT_QUANTITY_EXCEEDS_INSPECTED | Defect quantity exceeds the recorded failed quantity |
| BROKEN_TRACEABILITY_CHAIN | Defect and inspection reference different production orders |

Ground-truth files:

- `data/ground_truth/anomaly_cases.json`
- `data/ground_truth/anomaly_cases.csv`


five anomaly cases are labelled as ANOMALY in the ground-truth dataset.

## 9. Installation and Setup

### Prerequisites
- Python 3
- Git
- Windows, Linux, or macOS

### Clone the repository

```bash
git clone YOUR_PUBLIC_GITHUB_REPOSITORY_URL
cd yottaflex-quality-traceability
```

Replace the URL with your actual GitHub repository URL.

### Create a virtual environment

Windows CMD:

```cmd
python -m venv venv
venv\Scripts\activate
```

### Install dependencies

```cmd
pip install -r requirements.txt
```

### Configure the synthetic database

Windows CMD:

```cmd
set DATABASE_URL=sqlite:///./yottaflex_synthetic.db
```

### Initialize the database

```cmd
python -m database.init_db
python -m database.check_db
```

## 10. Generate Synthetic Data

For a fresh database, run the generators in this order:

```cmd
python -m generator.master_data
python -m generator.production_data
python -m generator.inspection_data
python -m generator.capa_data
python -m generator.anomaly_data
```

**Important:** Run the database generators against a fresh database. Do not rerun them against an already populated database unless duplicate handling is implemented.

## 11. Export Dataset

```cmd
python -m generator.export_data
```

Exports are saved in:
- `data/csv/`
- `data/json/`
- `data/sql/`

## 12. Validation

Run the validation scripts:

```cmd
python -m validation.production_data_check
python -m validation.check_quality_counts
python -m validation.traceability_check
python -m validation.business_rules
python -m validation.capa_validation
python -m validation.capa_data_check
python -m validation.anomaly_tests
python -m validation.export_check
```

## 13. Reproducibility

Create a checksum baseline:

```cmd
python -m validation.reproducibility_check --baseline
```

Regenerate exports from the existing database:

```cmd
python -m generator.export_data
```

Compare checksums:

```cmd
python -m validation.reproducibility_check --compare
```

The current repeat-export test successfully compared 33 files with matching SHA-256 checksums.

This verifies repeat-export consistency from the same database. A fresh database rebuild test is still a separate task.

## 14. Current Validation Results

| Validation | Result |
|---|---|
| Database initialization | Passed |
| Database table verification | Passed |
| Production data verification | Passed |
| Quality data verification | Passed |
| Defect traceability | Passed |
| Business-rule validation | Passed |
| CAPA lifecycle validation | Passed |
| CAPA data verification | Passed |
| Five anomaly test scenarios | Passed |
| CSV and JSON export verification | Passed |
| SHA-256 repeat-export comparison | Passed |

## 15. Current Limitations

- The dataset is synthetic, not real manufacturing data.
- The audit-events table currently contains zero records.
- Some anomaly scenarios are detected through business-validation logic rather than database constraints.
- Ground-truth anomaly examples are stored separately from operational records.
- Fresh-database rebuild reproducibility has not yet been verified.
- SQLite is currently used as the database backend.

## 16. AI Usage Disclosure

AI assistance was used during development for database design guidance, SQLAlchemy models, synthetic data generation, validation logic, debugging, and documentation.

The project author is responsible for reviewing, testing, understanding, and explaining the final implementation.

The `prompt_history/` directory is intended to contain the actual prompts used during AI-assisted development. Record the prompts and tools used accurately.

## 17. Author

**Project:** YottaFlex Manufacturing Quality & Defect Traceability System

**Technology:** Python, SQLite, SQLAlchemy

**GitHub:** Add your public repository URL here.
