
# YottaFlex AI – Manufacturing Quality Traceability
# Data Dictionary

Version: 1.0
Database: SQLite
Project: Manufacturing Quality and Defect Traceability

---

## 1. Product

Purpose: Stores manufactured product information.

| Field | Type | Required | Constraints |
|---|---|---|---|
| product_id | VARCHAR(20) | Yes | PK, unique, SKU-000001 |
| product_name | VARCHAR(100) | Yes | Not null |
| category | VARCHAR(50) | Yes | Controlled category |
| description | TEXT | No | Optional |
| unit_of_measure | VARCHAR(20) | Yes | PCS, KG, LITRE |
| lifecycle_status | VARCHAR(20) | Yes | ACTIVE, INACTIVE |
| created_at | DATETIME | Yes | Valid timestamp |
| updated_at | DATETIME | Yes | Must be >= created_at |

---

## 2. BOM (Bill of Materials)

Purpose: Defines the materials required to manufacture a product.

| Field | Type | Required | Constraints |
|---|---|---|---|
| bom_id | VARCHAR(30) | Yes | PK, unique |
| product_id | VARCHAR(20) | Yes | FK → Product |
| version | INTEGER | Yes | Greater than zero |
| effective_from | DATE | Yes | Valid date |
| effective_to | DATE | No | Must be >= effective_from |
| lifecycle_status | VARCHAR(20) | Yes | DRAFT, ACTIVE, OBSOLETE |
| created_at | DATETIME | Yes | Valid timestamp |

BOM Material Lines:

| Field | Type | Required | Constraints |
|---|---|---|---|
| bom_line_id | INTEGER | Yes | PK |
| bom_id | VARCHAR(30) | Yes | FK → BOM |
| material_code | VARCHAR(30) | Yes | Unique within BOM |
| material_description | VARCHAR(100) | Yes | Not null |
| quantity_required | FLOAT | Yes | Greater than zero |
| unit_of_measure | VARCHAR(20) | Yes | Valid unit |
| scrap_allowance_pct | FLOAT | Yes | 0–100 |

---

## 3. Supplier

Purpose: Stores supplier information.

| Field | Type | Required | Constraints |
|---|---|---|---|
| supplier_id | VARCHAR(20) | Yes | PK, unique |
| supplier_name | VARCHAR(100) | Yes | Not null |
| supplier_location | VARCHAR(100) | Yes | Not null |
| supplier_category | VARCHAR(50) | Yes | Controlled category |
| quality_rating | FLOAT | Yes | 0–100 |
| lifecycle_status | VARCHAR(20) | Yes | ACTIVE, INACTIVE |
| created_at | DATETIME | Yes | Valid timestamp |

---

## 4. MaterialLot

Purpose: Tracks incoming batches of raw materials.

| Field | Type | Required | Constraints |
|---|---|---|---|
| lot_id | VARCHAR(50) | Yes | PK, unique |
| supplier_id | VARCHAR(20) | Yes | FK → Supplier |
| material_code | VARCHAR(30) | Yes | Must match BOM material |
| supplier_batch_number | VARCHAR(50) | Yes | Not null |
| received_quantity | FLOAT | Yes | Greater than zero |
| available_quantity | FLOAT | Yes | 0 to received quantity |
| unit_of_measure | VARCHAR(20) | Yes | Valid unit |
| received_date | DATE | Yes | Valid date |
| expiry_date | DATE | No | Must be >= received date |
| inspection_status | VARCHAR(20) | Yes | PENDING, ACCEPTED, REJECTED |
| lifecycle_status | VARCHAR(20) | Yes | AVAILABLE, PARTIALLY_USED, CONSUMED, QUARANTINED |

---

## 5. ProductionOrder

Purpose: Records manufacturing orders.

| Field | Type | Required | Constraints |
|---|---|---|---|
| order_id | VARCHAR(30) | Yes | PK, WO-2026-000001 |
| product_id | VARCHAR(20) | Yes | FK → Product |
| bom_id | VARCHAR(30) | Yes | FK → BOM |
| planned_quantity | INTEGER | Yes | Greater than zero |
| actual_quantity | INTEGER | No | 0 or greater |
| start_date | DATETIME | Yes | Valid date |
| end_date | DATETIME | No | >= start_date |
| priority | VARCHAR(20) | Yes | LOW, MEDIUM, HIGH |
| lifecycle_status | VARCHAR(20) | Yes | PLANNED, IN_PROGRESS, COMPLETED, CANCELLED |

---

## 6. Machine

Purpose: Stores manufacturing equipment details.

| Field | Type | Required | Constraints |
|---|---|---|---|
| machine_id | VARCHAR(20) | Yes | PK, unique |
| machine_name | VARCHAR(100) | Yes | Not null |
| machine_type | VARCHAR(50) | Yes | Controlled type |
| location | VARCHAR(100) | Yes | Not null |
| installation_date | DATE | Yes | Valid date |
| lifecycle_status | VARCHAR(20) | Yes | ACTIVE, MAINTENANCE, INACTIVE |
| created_at | DATETIME | Yes | Valid timestamp |

---

## 7. ProcessStep

Purpose: Defines manufacturing operations.

| Field | Type | Required | Constraints |
|---|---|---|---|
| step_id | VARCHAR(30) | Yes | PK, unique |
| order_id | VARCHAR(30) | Yes | FK → ProductionOrder |
| machine_id | VARCHAR(20) | Yes | FK → Machine |
| step_name | VARCHAR(100) | Yes | Not null |
| sequence_number | INTEGER | Yes | Greater than zero |
| start_time | DATETIME | Yes | Valid timestamp |
| end_time | DATETIME | No | >= start_time |
| temperature | FLOAT | No | Celsius |
| pressure | FLOAT | No | Bar |
| process_status | VARCHAR(20) | Yes | PENDING, RUNNING, COMPLETED, FAILED |

---

## 8. InspectionPlan

Purpose: Defines quality inspection requirements.

| Field | Type | Required | Constraints |
|---|---|---|---|
| inspection_plan_id | VARCHAR(30) | Yes | PK, unique |
| product_id | VARCHAR(20) | Yes | FK → Product |
| plan_name | VARCHAR(100) | Yes | Not null |
| inspection_type | VARCHAR(30) | Yes | INCOMING, IN_PROCESS, FINAL |
| sample_size | INTEGER | Yes | Greater than zero |
| acceptance_limit | FLOAT | Yes | 0–100 |
| effective_from | DATE | Yes | Valid date |
| effective_to | DATE | No | >= effective_from |
| lifecycle_status | VARCHAR(20) | Yes | ACTIVE, INACTIVE |

---

## 9. InspectionResult

Purpose: Records actual inspection outcomes.

| Field | Type | Required | Constraints |
|---|---|---|---|
| inspection_id | VARCHAR(40) | Yes | PK, INSP-<order-id>-001 |
| inspection_plan_id | VARCHAR(30) | Yes | FK → InspectionPlan |
| order_id | VARCHAR(30) | Yes | FK → ProductionOrder |
| lot_id | VARCHAR(50) | No | FK → MaterialLot |
| step_id | VARCHAR(30) | No | FK → ProcessStep |
| inspection_date | DATETIME | Yes | Valid timestamp |
| inspected_quantity | INTEGER | Yes | Greater than zero |
| passed_quantity | INTEGER | Yes | 0 to inspected quantity |
| failed_quantity | INTEGER | Yes | 0 to inspected quantity |
| inspection_status | VARCHAR(20) | Yes | PASS, FAIL, CONDITIONAL |

Validation:
passed_quantity + failed_quantity = inspected_quantity.

---

## 10. Defect

Purpose: Records defects identified during inspection.

| Field | Type | Required | Constraints |
|---|---|---|---|
| defect_id | VARCHAR(30) | Yes | PK, DEF-2026-000001 |
| inspection_id | VARCHAR(40) | Yes | FK → InspectionResult |
| order_id | VARCHAR(30) | Yes | FK → ProductionOrder |
| lot_id | VARCHAR(50) | No | FK → MaterialLot |
| step_id | VARCHAR(30) | No | FK → ProcessStep |
| machine_id | VARCHAR(20) | No | FK → Machine |
| defect_type | VARCHAR(50) | Yes | Controlled defect category |
| severity | VARCHAR(20) | Yes | LOW, MEDIUM, HIGH, CRITICAL |
| defect_quantity | INTEGER | Yes | Greater than zero |
| detection_date | DATETIME | Yes | Valid timestamp |
| containment_status | VARCHAR(20) | Yes | OPEN, CONTAINED, RELEASED |
| lifecycle_status | VARCHAR(20) | Yes | OPEN, UNDER_INVESTIGATION, RESOLVED, CLOSED |

---

## 11. CorrectiveAction

Purpose: Tracks corrective and preventive actions (CAPA).

| Field | Type | Required | Constraints |
|---|---|---|---|
| capa_id | VARCHAR(30) | Yes | PK, CAPA-2026-000001 |
| defect_id | VARCHAR(30) | Yes | FK → Defect |
| root_cause | TEXT | Yes | Not null |
| containment_action | TEXT | Yes | Not null |
| corrective_action | TEXT | Yes | Not null |
| preventive_action | TEXT | No | Optional |
| assigned_to | VARCHAR(100) | Yes | Not null |
| created_date | DATETIME | Yes | Valid timestamp |
| target_date | DATE | Yes | >= created_date date |
| closed_date | DATETIME | No | Only after verification |
| verification_status | VARCHAR(20) | Yes | PENDING, PASSED, FAILED |
| lifecycle_status | VARCHAR(20) | Yes | OPEN, IN_PROGRESS, PENDING_VERIFICATION, CLOSED |

Validation:
CAPA cannot be CLOSED unless verification_status = PASSED.

---

## 12. Supporting Relationship Tables

### MaterialConsumption

Connects ProductionOrder and MaterialLot.

| Field | Type | Required | Constraints |
|---|---|---|---|
| consumption_id | INTEGER | Yes | PK |
| order_id | VARCHAR(30) | Yes | FK → ProductionOrder |
| lot_id | VARCHAR(50) | Yes | FK → MaterialLot |
| material_code | VARCHAR(30) | Yes | Must match BOM |
| consumed_quantity | FLOAT | Yes | Greater than zero |
| consumption_date | DATETIME | Yes | Valid timestamp |

### OrderMachineExecution

Connects ProductionOrder and Machine execution records.

| Field | Type | Required | Constraints |
|---|---|---|---|
| execution_id | INTEGER | Yes | PK |
| order_id | VARCHAR(30) | Yes | FK → ProductionOrder |
| machine_id | VARCHAR(20) | Yes | FK → Machine |
| step_id | VARCHAR(30) | Yes | FK → ProcessStep |
| start_time | DATETIME | Yes | Valid timestamp |
| end_time | DATETIME | No | >= start_time |

### EntityEvent

Preserves lifecycle and state change history.

| Field | Type | Required | Constraints |
|---|---|---|---|
| event_id | INTEGER | Yes | PK |
| entity_type | VARCHAR(50) | Yes | Entity name |
| entity_id | VARCHAR(50) | Yes | Referenced entity ID |
| previous_state | VARCHAR(30) | No | Previous status |
| new_state | VARCHAR(30) | Yes | New status |
| event_timestamp | DATETIME | Yes | Valid timestamp |
| changed_by | VARCHAR(100) | Yes | Actor |
| event_reason | TEXT | No | Explanation |

---

## 13. Data Generation Rules

1. Generate parent records before dependent records.
2. All primary keys must be unique.
3. All foreign keys must reference valid parent records in the baseline dataset.
4. Use deterministic ID counters.
5. Use random seed 20261022.
6. Generate derived values from source records.
7. Keep anomaly labels separate from input data.
8. Preserve lifecycle history using events.
9. Validate quantities and dates.
10. Never silently overwrite historical records.

---

## 14. Required Anomaly Scenarios

| Anomaly | Expected Detection |
|---|---|
| Defect linked to nonexistent lot | Foreign key exception |
| BOM material not consumed | Material reconciliation failure |
| CAPA closes before verification | Lifecycle violation |
| Defect quantity exceeds inspected quantity | Quantity validation failure |
| Broken traceability chain | Traceability exception |

Anomalies must be labelled in a separate ground_truth dataset.

---

## 15. Naming Conventions

| Entity | Example |
|---|---|
| Product | SKU-000001 |
| Supplier | SUP-000001 |
| MaterialLot | LOT-SUP-000001-2026-000001 |
| ProductionOrder | WO-2026-000001 |
| Inspection | INSP-WO-2026-000001-001 |
| Defect | DEF-2026-000001 |
| CorrectiveAction | CAPA-2026-000001 |

---

## 16. Database Integrity

- Primary keys must be unique.
- Foreign keys must be validated.
- Quantities must reconcile.
- Dates must follow valid chronological order.
- Lifecycle transitions must follow business rules.
- Defect rates must use inspected quantities as denominators.
- CAPA closure requires successful verification.
- Baseline data must contain no unintended integrity violations.
- Deliberate anomalies must be explicitly labelled.
