
# =====================================================
# YOTTAFLEX SYNTHETIC DATA GENERATOR CONFIGURATION
# =====================================================

# Fixed random seed for reproducibility
RANDOM_SEED = 20261022


# Dataset sizes
TOTAL_PRODUCTS = 200
TOTAL_SUPPLIERS = 50
TOTAL_MATERIAL_LOTS = 2000
TOTAL_PRODUCTION_ORDERS = 5000
TOTAL_INSPECTION_RESULTS = 20000


# Supporting data sizes
TOTAL_MACHINES = 30

# Date range for generated manufacturing data
DATA_START_DATE = "2025-01-01"
DATA_END_DATE = "2026-10-22"


# Dataset identification
PROJECT_NAME = "YottaFlex Quality Traceability System"
DATASET_VERSION = "1.0.0"


# Anomaly configuration
ANOMALY_TYPES = [
    "NONEXISTENT_MATERIAL_LOT",
    "BOM_MATERIAL_NOT_CONSUMED",
    "CAPA_CLOSED_BEFORE_VERIFICATION",
    "DEFECT_QUANTITY_EXCEEDS_INSPECTED",
    "BROKEN_TRACEABILITY_CHAIN"
]


# Output directories
CSV_OUTPUT_DIR = "data/csv"
JSON_OUTPUT_DIR = "data/json"
SQL_OUTPUT_DIR = "data/sql"
GROUND_TRUTH_DIR = "data/ground_truth"


# Validation configuration
ENABLE_VALIDATION = True
ENABLE_GROUND_TRUTH = True


def display_configuration():

    print("\nYOTTAFLEX DATA GENERATOR CONFIGURATION")
    print("--------------------------------------")

    print("Random Seed:", RANDOM_SEED)

    print("Products:", TOTAL_PRODUCTS)
    print("Suppliers:", TOTAL_SUPPLIERS)
    print("Material Lots:", TOTAL_MATERIAL_LOTS)
    print("Production Orders:", TOTAL_PRODUCTION_ORDERS)
    print("Inspection Results:", TOTAL_INSPECTION_RESULTS)
    print("Machines:", TOTAL_MACHINES)

    print("Dataset Version:", DATASET_VERSION)

    print("--------------------------------------")


if __name__ == "__main__":
    display_configuration()
