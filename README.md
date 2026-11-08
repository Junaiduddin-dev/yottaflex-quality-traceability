# YottaFlex – Manufacturing Quality & Defect Traceability System

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-blue.svg)](https://www.sqlite.org/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#license)

**A Python-based manufacturing quality management and defect traceability system with synthetic data generation, database validation, anomaly detection, and an interactive Streamlit dashboard.**

## 🚀 Live Dashboard

**[Open YottaFlex Live Dashboard](https://yottaflex-quality-traceability-95iw6daf9ls8zspfihtczx.streamlit.app/)**

Explore the interactive manufacturing quality dashboard featuring:

- **Dashboard Overview:** Manufacturing KPIs and production summaries.
- **Quality Analytics:** Inspection results, pass/fail rates, and defect trends.
- **Defect Traceability:** Trace defects through production orders, machines, materials, and suppliers.
- **CAPA Management:** Monitor corrective and preventive action lifecycles.
- **Anomaly Monitoring:** Explore five synthetic data-quality and traceability anomaly scenarios.

The dashboard is developed using Streamlit, Pandas, and Plotly.

---

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

An interactive Streamlit dashboard provides visual access to manufacturing quality metrics, defect traceability, CAPA records, and anomaly examples.

## 2. Project Objectives

- Build a relational manufacturing database.
- Generate realistic synthetic manufacturing data.
- Maintain traceability between defects, inspections, production orders, machines, material lots, and suppliers.
- Represent corrective actions and verification lifecycles.
- Detect data-quality and traceability anomalies.
- Export datasets in CSV, JSON, and SQL formats.
- Validate database integrity and business rules.
- Support reproducible dataset exports using SHA-256 checksums.
- Develop an interactive dashboard for manufacturing quality monitoring.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development and data generation |
| SQLite | Relational database |
| SQLAlchemy | ORM and database operations |
| Faker | Synthetic data generation |
| Pandas | Data loading and analysis |
| Streamlit | Interactive web dashboard |
| Plotly | Interactive charts and visualizations |
| CSV | Tabular data export |
| JSON | Structured data export |
| SQL | Database dump |
| SHA-256 | File integrity and reproducibility checks |
| Git | Version control |

## 4. Project Structure

```text
yottaflex-quality-traceability/
│
├── app.py
├── yottaflex_synthetic.db
├── requirements.txt
├── .gitignore
├── README.md
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
└── prompt_history/
    ├── AI_USAGE.md
    └── PROMPT_LOG.md
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

Refer to the following documentation for detailed database information:

- `docs/data_dictionary.md`
- `docs/erd.md`

## 6. Synthetic Dataset

The dataset was generated using the fixed random seed configured in `generator/config.py`.

**Dataset configuration and actual record counts:**

| Entity | Record count |
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
| **Total records** | **88,049** |

**Dataset details:**

- Random seed: `20261022`
- Dataset version: `1.0.0`
- Date range: `2025-01-01` to `2026-10-22`
- Database: SQLite
- Total relational tables: 15

The generated dataset is synthetic and is intended for development, testing, and demonstration purposes.

## 7. Defect Traceability

The system supports tracing a manufacturing defect through its related production and quality records.

```text
Product
   |
   v
Production Order
   |
   v
Inspection Result
   |
   v
Defect
   |
   v
Production Order / Process Execution
   |
   v
Machine
   |
   v
Material Consumption
   |
   v
Material Lot
   |
   v
Supplier
   |
   v
Corrective Action (CAPA)
```

Traceability validation checks relationships between defects, inspections, production orders, process executions, machines, material lots, and suppliers.

This helps identify potential sources of manufacturing quality issues.

## 8. Anomaly Scenarios

Five synthetic anomaly cases are maintained separately from the operational database.

| Anomaly | Description |
|---|---|
| `NONEXISTENT_MATERIAL_LOT` | Defect references a material lot that does not exist |
| `BOM_MATERIAL_NOT_CONSUMED` | BOM-required material has no consumption record |
| `CAPA_CLOSED_BEFORE_VERIFICATION` | CAPA is closed before successful verification |
| `DEFECT_QUANTITY_EXCEEDS_INSPECTED` | Defect quantity exceeds the recorded failed quantity |
| `BROKEN_TRACEABILITY_CHAIN` | Defect and inspection reference different production orders |

**Ground-truth files:**

- `data/ground_truth/anomaly_cases.json`
- `data/ground_truth/anomaly_cases.csv`

All five anomaly examples are labelled as `ANOMALY` in the ground-truth dataset.

These examples are stored separately from operational records and are used for anomaly-testing and demonstration purposes.

## 9. Installation and Setup

### Prerequisites

- Python 3
- Git
- Windows, Linux, or macOS

### Clone the repository

```bash
git clone https://github.com/Junaiduddin-dev/yottaflex-quality-traceability.git

cd yottaflex-quality-traceability
```

### Create a virtual environment

**Windows CMD:**

```cmd
python -m venv venv
venv\Scripts\activate
```

### Install dependencies

```cmd
pip install -r requirements.txt
```

### Configure the synthetic database

For backend database operations, configure the database URL:

**Windows CMD:**

```cmd
set DATABASE_URL=sqlite:///./yottaflex_synthetic.db
```

The Streamlit dashboard uses the included `yottaflex_synthetic.db` file directly.

## 10. Run the Streamlit Dashboard

Start the dashboard from the project root directory:

```cmd
streamlit run app.py
```

The application will open in your default browser.

**Live deployment:**

[https://yottaflex-quality-traceability-95iw6daf9ls8zspfihtczx.streamlit.app/](https://yottaflex-quality-traceability-95iw6daf9ls8zspfihtczx.streamlit.app/)

## 11. Generate Synthetic Data

For a fresh database, initialize the database:

```cmd
python -m database.init_db
python -m database.check_db
```

Run the generators in the following order:

```cmd
python -m generator.master_data
python -m generator.production_data
python -m generator.inspection_data
python -m generator.capa_data
python -m generator.anomaly_data
```

**Important:** Run the database generators against a fresh database. Do not rerun them against an already populated database unless duplicate handling is implemented.

The generation scripts use the configuration defined in `generator/config.py`.

## 12. Export Dataset

Run:

```cmd
python -m generator.export_data
```

Exports are saved in:

```text
data/
├── csv/
├── json/
└── sql/
```

The export module generates structured CSV, JSON, and SQL database outputs.

## 13. Validation

The project includes validation scripts for database integrity, production data, quality records, traceability, business rules, CAPA lifecycle, anomaly scenarios, and export consistency.

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

These scripts verify the generated dataset against the implemented database and business rules.

## 14. Reproducibility

The project uses SHA-256 checksums to compare exported files.

### Create a checksum baseline

```cmd
python -m validation.reproducibility_check --baseline
```

### Regenerate exports from the existing database

```cmd
python -m generator.export_data
```

### Compare checksums

```cmd
python -m validation.reproducibility_check --compare
```

**Current result:**

- 33 exported files compared.
- All 33 files produced matching SHA-256 checksums.

This verifies repeat-export consistency from the same database. A fresh database rebuild reproducibility test is still a separate task.

## 15. Current Validation Results

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

**Export verification summary:**

- 15 relational tables.
- 88,049 records.
- CSV and JSON record counts matched.
- SQL dump generated.
- Five ground-truth anomaly cases verified.
- 33 files passed repeat-export checksum comparison.

## 16. Current Limitations

- The dataset is synthetic, not real manufacturing data.
- The audit-events table currently contains zero records.
- Some anomaly scenarios are detected through business-validation logic rather than database constraints.
- Ground-truth anomaly examples are stored separately from operational records.
- Fresh-database rebuild reproducibility has not yet been verified.
- SQLite is currently used as the database backend.
- The dashboard is designed for demonstration and analysis, not production manufacturing operations.

## 17. AI Usage Disclosure

AI assistance was used during development for:

- Database design guidance.
- SQLAlchemy model development.
- Synthetic data generation.
- Validation logic.
- Debugging and troubleshooting.
- Documentation and project organization.
- Dashboard development.

The project author is responsible for reviewing, testing, understanding, and explaining the final implementation.

The `prompt_history/` directory contains reconstructed summaries of AI-assisted development requests. These summaries are not verbatim transcripts of the original prompts.

## 18. Author

**Project:** YottaFlex – Manufacturing Quality & Defect Traceability System

**Technologies:** Python, SQLite, SQLAlchemy, Pandas, Streamlit, Plotly

**GitHub Repository:**

[https://github.com/Junaiduddin-dev/yottaflex-quality-traceability](https://github.com/Junaiduddin-dev/yottaflex-quality-traceability)

**Live Dashboard:**

[https://yottaflex-quality-traceability-95iw6daf9ls8zspfihtczx.streamlit.app/](https://yottaflex-quality-traceability-95iw6daf9ls8zspfihtczx.streamlit.app/)

---

## License

This project is available for educational, demonstration, and portfolio purposes under the MIT License.
