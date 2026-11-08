
from datetime import date, datetime

from database.connection import SessionLocal

from database.models import (
    Product,
    Supplier,
    Machine,
    BOM,
    BOMLine,
    MaterialLot,
    ProductionOrder,
    MaterialConsumption,
    ProcessStep,
    OrderMachineExecution,
    InspectionPlan,
    InspectionResult,
    Defect,
    CorrectiveAction,
    AuditEvent
)


def seed_sample_data():

    session = SessionLocal()

    try:

        # Prevent duplicate sample data when rerunning the script
        existing_product = session.get(Product, "SKU-000001")

        if existing_product:
            print("Sample data already exists. No duplicate records inserted.")
            return

        print("Inserting YottaFlex sample manufacturing data...")

        # -------------------------------------------------
        # 1. PRODUCT
        # -------------------------------------------------

        product = Product(
            product_id="SKU-000001",
            product_name="Smart Sensor",
            category="Electronics",
            description="Industrial smart sensor",
            unit_of_measure="PCS",
            lifecycle_status="ACTIVE"
        )

        # -------------------------------------------------
        # 2. SUPPLIER
        # -------------------------------------------------

        supplier = Supplier(
            supplier_id="SUP-000001",
            supplier_name="ABC Electronics",
            supplier_location="Hyderabad",
            supplier_category="Electronic Components",
            quality_rating=95.5,
            lifecycle_status="ACTIVE"
        )

        # -------------------------------------------------
        # 3. MACHINE
        # -------------------------------------------------

        machine = Machine(
            machine_id="MCH-000001",
            machine_name="Assembly Machine 01",
            machine_type="Assembly",
            location="Production Hall A",
            installation_date=date(2024, 1, 15),
            lifecycle_status="ACTIVE"
        )

        session.add_all([product, supplier, machine])
        session.flush()

        # -------------------------------------------------
        # 4. BILL OF MATERIALS
        # -------------------------------------------------

        bom = BOM(
            bom_id="BOM-000001",
            product_id="SKU-000001",
            version=1,
            effective_from=date(2026, 1, 1),
            effective_to=None,
            lifecycle_status="ACTIVE"
        )

        session.add(bom)
        session.flush()

        bom_line = BOMLine(
            bom_id="BOM-000001",
            material_code="PCB-001",
            material_description="Smart Sensor PCB Board",
            quantity_required=2,
            unit_of_measure="PCS",
            scrap_allowance_pct=2
        )

        session.add(bom_line)

        # -------------------------------------------------
        # 5. MATERIAL LOT
        # -------------------------------------------------

        material_lot = MaterialLot(
            lot_id="LOT-SUP-000001-2026-000001",
            supplier_id="SUP-000001",
            material_code="PCB-001",
            supplier_batch_number="BATCH-ABC-001",
            received_quantity=100,
            available_quantity=80,
            unit_of_measure="PCS",
            received_date=date(2026, 10, 20),
            expiry_date=None,
            inspection_status="ACCEPTED",
            lifecycle_status="PARTIALLY_USED"
        )

        session.add(material_lot)

        # -------------------------------------------------
        # 6. PRODUCTION ORDER
        # -------------------------------------------------

        order = ProductionOrder(
            order_id="WO-2026-000001",
            product_id="SKU-000001",
            bom_id="BOM-000001",
            planned_quantity=10,
            actual_quantity=10,
            start_date=datetime(2026, 10, 22, 9, 0),
            end_date=datetime(2026, 10, 22, 15, 0),
            priority="HIGH",
            lifecycle_status="COMPLETED"
        )

        session.add(order)
        session.flush()

        # -------------------------------------------------
        # 7. MATERIAL CONSUMPTION
        # -------------------------------------------------

        consumption = MaterialConsumption(
            order_id="WO-2026-000001",
            lot_id="LOT-SUP-000001-2026-000001",
            material_code="PCB-001",
            consumed_quantity=20,
            consumption_date=datetime(2026, 10, 22, 9, 30)
        )

        session.add(consumption)

        # -------------------------------------------------
        # 8. PROCESS STEP
        # -------------------------------------------------

        process_step = ProcessStep(
            step_id="STEP-000001",
            order_id="WO-2026-000001",
            machine_id="MCH-000001",
            step_name="PCB Assembly",
            sequence_number=1,
            start_time=datetime(2026, 10, 22, 10, 0),
            end_time=datetime(2026, 10, 22, 12, 0),
            temperature=45.5,
            pressure=2.5,
            process_status="COMPLETED"
        )

        session.add(process_step)
        session.flush()

        # -------------------------------------------------
        # 9. MACHINE EXECUTION
        # -------------------------------------------------

        execution = OrderMachineExecution(
            order_id="WO-2026-000001",
            machine_id="MCH-000001",
            step_id="STEP-000001",
            start_time=datetime(2026, 10, 22, 10, 0),
            end_time=datetime(2026, 10, 22, 12, 0)
        )

        session.add(execution)
        session.flush()

        # -------------------------------------------------
        # 10. INSPECTION PLAN
        # -------------------------------------------------

        inspection_plan = InspectionPlan(
            inspection_plan_id="INSP-PLAN-000001",
            product_id="SKU-000001",
            inspection_name="Electrical Performance Test",
            characteristic="Output Voltage",
            inspection_stage="FINAL",
            lower_limit=4.5,
            upper_limit=5.5,
            unit_of_measure="VOLTS",
            sample_size=10,
            lifecycle_status="ACTIVE"
        )

        session.add(inspection_plan)
        session.flush()

        # -------------------------------------------------
        # 11. INSPECTION RESULT
        # -------------------------------------------------

        inspection_result = InspectionResult(
            inspection_id="INSP-WO-2026-000001-001",
            inspection_plan_id="INSP-PLAN-000001",
            order_id="WO-2026-000001",
            execution_id=execution.execution_id,
            inspection_date=datetime(2026, 10, 22, 14, 0),
            inspected_quantity=10,
            passed_quantity=8,
            failed_quantity=2,
            measured_value=4.2,
            inspection_status="FAIL",
            inspector_name="Quality Inspector 01"
        )

        session.add(inspection_result)
        session.flush()

        # -------------------------------------------------
        # 12. DEFECT
        # -------------------------------------------------

        defect = Defect(
            defect_id="DEF-2026-000001",
            inspection_id="INSP-WO-2026-000001-001",
            order_id="WO-2026-000001",
            execution_id=execution.execution_id,
            lot_id="LOT-SUP-000001-2026-000001",
            defect_category="Electrical Failure",
            defect_description="Output voltage below acceptable limit",
            defect_quantity=2,
            severity="HIGH",
            detected_at=datetime(2026, 10, 22, 14, 30),
            defect_status="OPEN"
        )

        session.add(defect)
        session.flush()

        # -------------------------------------------------
        # 13. CORRECTIVE ACTION
        # -------------------------------------------------

        capa = CorrectiveAction(
            capa_id="CAPA-2026-000001",
            defect_id="DEF-2026-000001",
            root_cause="Pending root cause investigation",
            containment_action="Affected products placed on hold",
            corrective_action=None,
            preventive_action=None,
            assigned_to="Quality Manager",
            opened_at=datetime(2026, 10, 22, 15, 0),
            due_date=date(2026, 10, 30),
            verified_at=None,
            closed_at=None,
            verification_result="PENDING",
            lifecycle_status="OPEN"
        )

        session.add(capa)

        # -------------------------------------------------
        # 14. AUDIT EVENT
        # -------------------------------------------------

        audit_event = AuditEvent(
            entity_type="ProductionOrder",
            entity_id="WO-2026-000001",
            event_type="CREATED",
            old_value=None,
            new_value="PLANNED",
            event_timestamp=datetime(2026, 10, 22, 9, 0),
            performed_by="System",
            reason="Sample production order creation"
        )

        session.add(audit_event)

        # Save all records
        session.commit()

        print("\nSample data inserted successfully!")

        print("Product: SKU-000001")
        print("Production Order: WO-2026-000001")
        print("Material Lot: LOT-SUP-000001-2026-000001")
        print("Inspection: INSP-WO-2026-000001-001")
        print("Defect: DEF-2026-000001")
        print("CAPA: CAPA-2026-000001")

    except Exception as error:

        session.rollback()
        print("Error inserting sample data:", error)
        raise

    finally:

        session.close()


if __name__ == "__main__":
    seed_sample_data()
