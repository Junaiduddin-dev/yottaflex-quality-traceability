
from database.connection import SessionLocal

from database.models import (
    BOMLine,
    MaterialConsumption,
    MaterialLot,
    ProductionOrder,
    InspectionResult,
    Defect,
    OrderMachineExecution,
    ProcessStep
)


def validate_business_rules():

    session = SessionLocal()
    errors = []
    passed = []

    try:

        defects = session.query(Defect).all()

        for defect in defects:

            inspection = session.get(
                InspectionResult,
                defect.inspection_id
            )

            order = session.get(
                ProductionOrder,
                defect.order_id
            )

            # 1. Check inspection exists and belongs to order
            if not inspection:
                errors.append(
                    f"{defect.defect_id}: Inspection does not exist"
                )

            elif inspection.order_id != defect.order_id:
                errors.append(
                    f"{defect.defect_id}: Inspection belongs to another order"
                )
            else:
                passed.append(
                    f"{defect.defect_id}: Inspection-order relationship valid"
                )

            # 2. Check defect quantity
            if inspection and defect.defect_quantity > inspection.failed_quantity:
                errors.append(
                    f"{defect.defect_id}: Defect quantity exceeds failed quantity"
                )
            elif inspection:
                passed.append(
                    f"{defect.defect_id}: Defect quantity valid"
                )

            # 3. Check production order
            if not order:
                errors.append(
                    f"{defect.defect_id}: Production order does not exist"
                )

            # 4. Check machine execution
            if defect.execution_id is not None:

                execution = session.get(
                    OrderMachineExecution,
                    defect.execution_id
                )

                if not execution:
                    errors.append(
                        f"{defect.defect_id}: Machine execution missing"
                    )

                elif execution.order_id != defect.order_id:
                    errors.append(
                        f"{defect.defect_id}: Machine execution belongs to another order"
                    )

                else:
                    step = session.get(
                        ProcessStep,
                        execution.step_id
                    )

                    if not step:
                        errors.append(
                            f"{defect.defect_id}: Process step missing"
                        )

                    elif (
                        step.order_id != execution.order_id
                        or step.machine_id != execution.machine_id
                    ):
                        errors.append(
                            f"{defect.defect_id}: Process step and machine execution mismatch"
                        )

                    else:
                        passed.append(
                            f"{defect.defect_id}: Machine traceability valid"
                        )

            # 5. Check material lot consumption
            if defect.lot_id is not None:

                lot = session.get(
                    MaterialLot,
                    defect.lot_id
                )

                consumption = session.query(
                    MaterialConsumption
                ).filter_by(
                    order_id=defect.order_id,
                    lot_id=defect.lot_id
                ).first()

                if not lot:
                    errors.append(
                        f"{defect.defect_id}: Material lot missing"
                    )

                elif not consumption:
                    errors.append(
                        f"{defect.defect_id}: Lot was not consumed by this order"
                    )

                elif consumption.material_code != lot.material_code:
                    errors.append(
                        f"{defect.defect_id}: Consumption material code mismatch"
                    )

                else:
                    passed.append(
                        f"{defect.defect_id}: Material lot traceability valid"
                    )

            # 6. Check BOM material consumption
            if order:

                bom_line = session.query(BOMLine).filter_by(
                    bom_id=order.bom_id,
                    material_code=(
                        lot.material_code if defect.lot_id and lot else None
                    )
                ).first() if defect.lot_id and lot else None

                if defect.lot_id and lot and not bom_line:
                    errors.append(
                        f"{defect.defect_id}: Material not found in order BOM"
                    )

        # 7. Check consumption against lot balances
        lots = session.query(MaterialLot).all()

        for lot in lots:

            total_consumed = sum(
                row.consumed_quantity
                for row in session.query(MaterialConsumption).filter_by(
                    lot_id=lot.lot_id
                ).all()
            )

            expected_available = lot.received_quantity - total_consumed

            if abs(expected_available - lot.available_quantity) > 0.000001:
                errors.append(
                    f"{lot.lot_id}: Available quantity does not reconcile"
                )
            else:
                passed.append(
                    f"{lot.lot_id}: Material quantity reconciled"
                )

        # Print report
        print("\nYOTTAFLEX BUSINESS VALIDATION REPORT")
        print("------------------------------------")

        for message in passed:
            print("[PASS]", message)

        for message in errors:
            print("[FAIL]", message)

        print("------------------------------------")
        print("Passed checks:", len(passed))
        print("Failed checks:", len(errors))

        if errors:
            print("VALIDATION RESULT: FAILED")
        else:
            print("VALIDATION RESULT: PASSED")

    finally:
        session.close()


if __name__ == "__main__":
    validate_business_rules()
