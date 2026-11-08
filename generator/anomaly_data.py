
import csv
import json
from pathlib import Path

from generator.config import (
    RANDOM_SEED,
    PROJECT_NAME,
    DATASET_VERSION,
    ANOMALY_TYPES,
    GROUND_TRUTH_DIR,
    ENABLE_GROUND_TRUTH,
)


def build_anomaly_cases():
    """Build five labelled anomaly examples without changing the database."""

    cases = [
        {
            "anomaly_id": "ANOM-001",
            "anomaly_type": "NONEXISTENT_MATERIAL_LOT",
            "entity_type": "Defect",
            "entity_id": "TEST-DEF-LOT-001",
            "related_entities": {
                "inspection_id": "INSP-WO-2026-000001-001",
                "order_id": "WO-2026-000001",
                "material_lot_id": "LOT-DOES-NOT-EXIST",
            },
            "description": "Defect references a material lot that does not exist.",
            "expected_detection": "Foreign-key or material-lot existence validation should reject the reference.",
            "severity": "HIGH",
            "ground_truth_label": "ANOMALY",
        },
        {
            "anomaly_id": "ANOM-002",
            "anomaly_type": "BOM_MATERIAL_NOT_CONSUMED",
            "entity_type": "ProductionOrder",
            "entity_id": "WO-2026-000001",
            "related_entities": {
                "bom_material_code": "TEST-MISSING-MATERIAL",
                "required_quantity": 1,
                "consumed_quantity": 0,
            },
            "description": "A material required by the production order BOM has no corresponding consumption record.",
            "expected_detection": "BOM-to-consumption reconciliation should identify the missing material.",
            "severity": "HIGH",
            "ground_truth_label": "ANOMALY",
        },
        {
            "anomaly_id": "ANOM-003",
            "anomaly_type": "CAPA_CLOSED_BEFORE_VERIFICATION",
            "entity_type": "CorrectiveAction",
            "entity_id": "TEST-CAPA-INVALID-001",
            "related_entities": {
                "defect_id": "DEF-2026-000001",
                "verified_at": None,
                "closed_at": "2026-10-22T15:00:00",
                "verification_result": "PENDING",
                "lifecycle_status": "CLOSED",
            },
            "description": "CAPA is marked CLOSED even though verification has not been completed.",
            "expected_detection": "CAPA lifecycle validation should reject closure without successful verification.",
            "severity": "CRITICAL",
            "ground_truth_label": "ANOMALY",
        },
        {
            "anomaly_id": "ANOM-004",
            "anomaly_type": "DEFECT_QUANTITY_EXCEEDS_INSPECTED",
            "entity_type": "Defect",
            "entity_id": "TEST-DEF-QTY-001",
            "related_entities": {
                "inspection_id": "INSP-WO-2026-000001-001",
                "inspected_quantity": 10,
                "failed_quantity": 2,
                "defect_quantity": 3,
            },
            "description": "Defect quantity exceeds the failed quantity recorded by inspection.",
            "expected_detection": "Defect quantity must not exceed the inspection failed quantity.",
            "severity": "HIGH",
            "ground_truth_label": "ANOMALY",
        },
        {
            "anomaly_id": "ANOM-005",
            "anomaly_type": "BROKEN_TRACEABILITY_CHAIN",
            "entity_type": "Defect",
            "entity_id": "TEST-DEF-BROKEN-001",
            "related_entities": {
                "inspection_id": "INSP-WO-2026-000001-001",
                "inspection_order_id": "WO-2026-000001",
                "defect_order_id": "WO-2026-TEST-999",
            },
            "description": "Defect references a production order different from the order linked to its inspection.",
            "expected_detection": "Inspection-order relationship validation should identify the mismatch.",
            "severity": "CRITICAL",
            "ground_truth_label": "ANOMALY",
        },
    ]

    return cases


def validate_anomaly_cases(cases):
    """Check that all configured anomaly types have one labelled example."""

    generated_types = {case["anomaly_type"] for case in cases}
    configured_types = set(ANOMALY_TYPES)

    if generated_types != configured_types:
        missing = configured_types - generated_types
        unexpected = generated_types - configured_types

        raise ValueError(
            f"Anomaly type mismatch. Missing: {missing}; "
            f"Unexpected: {unexpected}"
        )

    if len(cases) != len(ANOMALY_TYPES):
        raise ValueError("Unexpected number of anomaly examples.")

    for case in cases:
        if case["ground_truth_label"] != "ANOMALY":
            raise ValueError(
                f"Incorrect ground-truth label: {case['anomaly_id']}"
            )


def export_json(cases, output_dir):
    output_path = output_dir / "anomaly_cases.json"

    dataset = {
        "project_name": PROJECT_NAME,
        "dataset_version": DATASET_VERSION,
        "random_seed": RANDOM_SEED,
        "record_count": len(cases),
        "ground_truth_note": (
            "These are separate synthetic anomaly test cases. "
            "They are not inserted into the operational database."
        ),
        "cases": cases,
    }

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(dataset, file, indent=4)

    return output_path


def export_csv(cases, output_dir):
    output_path = output_dir / "anomaly_cases.csv"

    fieldnames = [
        "anomaly_id",
        "anomaly_type",
        "entity_type",
        "entity_id",
        "related_entities",
        "description",
        "expected_detection",
        "severity",
        "ground_truth_label",
    ]

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for case in cases:
            row = case.copy()
            row["related_entities"] = json.dumps(
                case["related_entities"]
            )
            writer.writerow(row)

    return output_path


def main():
    print("\nYOTTAFLEX ANOMALY DATA GENERATOR")
    print("--------------------------------")

    if not ENABLE_GROUND_TRUTH:
        print("Ground-truth generation is disabled in configuration.")
        return

    output_dir = Path(GROUND_TRUTH_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    cases = build_anomaly_cases()
    validate_anomaly_cases(cases)

    json_file = export_json(cases, output_dir)
    csv_file = export_csv(cases, output_dir)

    print("Anomaly examples generated:", len(cases))
    print("Ground-truth labels: ANOMALY")
    print("JSON file:", json_file)
    print("CSV file:", csv_file)
    print("Operational database modified: NO")
    print("\nANOMALY DATA GENERATION: PASSED")


if __name__ == "__main__":
    main()
