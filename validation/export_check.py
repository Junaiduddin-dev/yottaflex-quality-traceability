
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CSV_DIR = ROOT / "data" / "csv"
JSON_DIR = ROOT / "data" / "json"
SQL_FILE = ROOT / "data" / "sql" / "yottaflex_database.sql"

EXPECTED_TABLES = {
    "audit_events",
    "bom_lines",
    "boms",
    "corrective_actions",
    "defects",
    "inspection_plans",
    "inspection_results",
    "machines",
    "material_consumptions",
    "material_lots",
    "order_machine_executions",
    "process_steps",
    "production_orders",
    "products",
    "suppliers",
}


def verify_exports():
    print("\nYOTTAFLEX EXPORT VERIFICATION")
    print("=============================")

    csv_tables = {path.stem for path in CSV_DIR.glob("*.csv")}
    json_tables = {path.stem for path in JSON_DIR.glob("*.json")}

    if csv_tables != EXPECTED_TABLES:
        print("[FAIL] CSV table list does not match expected tables.")
        print("Missing:", EXPECTED_TABLES - csv_tables)
        print("Unexpected:", csv_tables - EXPECTED_TABLES)
        return False

    if json_tables != EXPECTED_TABLES:
        print("[FAIL] JSON table list does not match expected tables.")
        print("Missing:", EXPECTED_TABLES - json_tables)
        print("Unexpected:", json_tables - EXPECTED_TABLES)
        return False

    total_records = 0

    for table_name in sorted(EXPECTED_TABLES):
        csv_path = CSV_DIR / f"{table_name}.csv"
        json_path = JSON_DIR / f"{table_name}.json"

        with csv_path.open(
            "r", newline="", encoding="utf-8-sig"
        ) as file:
            csv_count = sum(1 for _ in csv.DictReader(file))

        with json_path.open(
            "r", encoding="utf-8"
        ) as file:
            json_records = json.load(file)

        if not isinstance(json_records, list):
            print(f"[FAIL] {table_name}: JSON is not a list.")
            return False

        json_count = len(json_records)

        if csv_count != json_count:
            print(
                f"[FAIL] {table_name}: CSV={csv_count}, "
                f"JSON={json_count}"
            )
            return False

        total_records += csv_count
        print(
            f"[PASS] {table_name}: "
            f"CSV={csv_count}, JSON={json_count}"
        )

    if not SQL_FILE.exists() or SQL_FILE.stat().st_size == 0:
        print("[FAIL] SQL dump is missing or empty.")
        return False

    anomaly_json = ROOT / "data" / "ground_truth" / "anomaly_cases.json"
    anomaly_csv = ROOT / "data" / "ground_truth" / "anomaly_cases.csv"

    if not anomaly_json.exists() or not anomaly_csv.exists():
        print("[FAIL] Ground-truth anomaly files are missing.")
        return False

    with anomaly_json.open("r", encoding="utf-8") as file:
        anomaly_data = json.load(file)

    anomaly_count = len(anomaly_data["cases"])

    if anomaly_count != 5:
        print("[FAIL] Expected five ground-truth anomaly cases.")
        return False

    print("\n-----------------------------")
    print("EXPORT VERIFICATION SUMMARY")
    print("-----------------------------")
    print("Tables verified:", len(EXPECTED_TABLES))
    print("Records verified:", total_records)
    print("SQL dump: PRESENT")
    print("Ground-truth anomaly cases:", anomaly_count)
    print("\nEXPORT VERIFICATION: PASSED")

    return True


if __name__ == "__main__":
    success = verify_exports()

    if not success:
        raise SystemExit(1)
