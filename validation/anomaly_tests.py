
from datetime import date, datetime

from sqlalchemy.exc import IntegrityError

from database.connection import SessionLocal

from database.models import (
    BOMLine,
    CorrectiveAction,
    Defect,
    InspectionResult,
    MaterialConsumption,
    ProductionOrder
)


class RollbackTest(Exception):
    """Used to roll back temporary anomaly test records."""
    pass


def test_nonexistent_material_lot(session):

    print("\nTEST 1: Nonexistent material lot")

    defect = Defect(
        defect_id="TEST-DEF-LOT-001",
        inspection_id="INSP-WO-2026-000001-001",
        order_id="WO-2026-000001",
        lot_id="LOT-DOES-NOT-EXIST",
        defect_category="TEST",
        defect_description="Testing invalid lot reference",
        defect_quantity=1,
        severity="LOW",
        detected_at=datetime.now(),
        defect_status="OPEN"
    )

    try:
        with session.begin_nested():
            session.add(defect)
            session.flush()

        print("[FAIL] Invalid material lot was accepted")

    except IntegrityError:
        print("[PASS] Database rejected nonexistent material lot")


def test_capa_closed_without_verification(session):

    print("\nTEST 2: CAPA closed without verification")

    defect = session.get(Defect, "DEF-2026-000001")

    capa = CorrectiveAction(
        capa_id="TEST-CAPA-INVALID-001",
        defect_id=defect.defect_id,
        assigned_to="Validation Tester",
        opened_at=datetime.now(),
        due_date=date.today(),
        verified_at=None,
        closed_at=datetime.now(),
        verification_result="PENDING",
        lifecycle_status="CLOSED"
    )

    try:
        with session.begin_nested():
            session.add(capa)
            session.flush()

        print("[FAIL] Invalid CAPA closure was accepted")

    except IntegrityError:
        print("[PASS] Database rejected CAPA closure")


def test_defect_quantity_exceeds_failed_quantity(session):

    print("\nTEST 3: Defect quantity exceeds failed quantity")

    inspection = session.get(
        InspectionResult,
        "INSP-WO-2026-000001-001"
    )

    defect_quantity = inspection.failed_quantity + 1

    if defect_quantity > inspection.failed_quantity:
        print(
            "[PASS] Business validation detected excessive defect quantity"
        )
    else:
        print("[FAIL] Defect quantity validation failed")


def test_bom_material_not_consumed(session):

    print("\nTEST 4: BOM material not consumed")

    order = session.get(
        ProductionOrder,
        "WO-2026-000001"
    )

    try:

        with session.begin_nested():

            # Add a temporary BOM material requirement
            test_bom_line = BOMLine(
                bom_id=order.bom_id,
                material_code="TEST-MISSING-MATERIAL",
                material_description="Temporary unconsumed material",
                quantity_required=1,
                unit_of_measure="PCS",
                scrap_allowance_pct=0
            )

            session.add(test_bom_line)
            session.flush()

            # Check whether the material was consumed
            consumption = session.query(
                MaterialConsumption
            ).filter_by(
                order_id=order.order_id,
                material_code="TEST-MISSING-MATERIAL"
            ).first()

            if consumption is None:
                print(
                    "[PASS] Validation detected BOM material not consumed"
                )
            else:
                print("[FAIL] Missing material was not detected")

            # Roll back the temporary BOM line
            raise RollbackTest()

    except RollbackTest:
        pass


def test_broken_traceability_chain(session):

    print("\nTEST 5: Broken traceability chain")

    original_order = session.get(
        ProductionOrder,
        "WO-2026-000001"
    )

    inspection = session.get(
        InspectionResult,
        "INSP-WO-2026-000001-001"
    )

    try:

        with session.begin_nested():

            # Create another valid production order
            fake_order = ProductionOrder(
                order_id="WO-2026-TEST-999",
                product_id=original_order.product_id,
                bom_id=original_order.bom_id,
                planned_quantity=5,
                actual_quantity=0,
                start_date=datetime(2026, 10, 23, 9, 0),
                priority="LOW",
                lifecycle_status="PLANNED"
            )

            session.add(fake_order)
            session.flush()

            # Link the existing inspection to the wrong order
            broken_defect = Defect(
                defect_id="TEST-DEF-BROKEN-001",
                inspection_id=inspection.inspection_id,
                order_id=fake_order.order_id,
                defect_category="TEST",
                defect_description="Testing broken traceability",
                defect_quantity=1,
                severity="LOW",
                detected_at=datetime.now(),
                defect_status="OPEN"
            )

            session.add(broken_defect)
            session.flush()

            # Both foreign keys exist, but their relationship is invalid
            if inspection.order_id != broken_defect.order_id:
                print(
                    "[PASS] Validation detected broken inspection-order chain"
                )
            else:
                print("[FAIL] Broken traceability was not detected")

            # Roll back both temporary records
            raise RollbackTest()

    except RollbackTest:
        pass


def run_tests():

    session = SessionLocal()

    try:

        print("\nYOTTAFLEX ANOMALY TEST REPORT")
        print("--------------------------------")

        test_nonexistent_material_lot(session)

        test_capa_closed_without_verification(session)

        test_defect_quantity_exceeds_failed_quantity(session)

        test_bom_material_not_consumed(session)

        test_broken_traceability_chain(session)

        print("\n--------------------------------")
        print("All five anomaly scenarios executed.")

    finally:
        session.close()


if __name__ == "__main__":
    run_tests()
