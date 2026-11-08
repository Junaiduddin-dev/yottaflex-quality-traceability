
from database.connection import SessionLocal

from database.models import (
    Product,
    Supplier,
    MaterialLot,
    ProductionOrder,
    Machine,
    ProcessStep,
    OrderMachineExecution,
    InspectionResult,
    Defect,
    CorrectiveAction
)


def trace_defect(defect_id):

    session = SessionLocal()

    try:

        result = (
            session.query(
                Defect.defect_id,
                Defect.defect_category,
                Defect.defect_description,
                Defect.defect_quantity,
                Defect.severity,

                InspectionResult.inspection_id,
                InspectionResult.inspection_status,
                InspectionResult.inspected_quantity,
                InspectionResult.passed_quantity,
                InspectionResult.failed_quantity,

                ProductionOrder.order_id,
                ProductionOrder.lifecycle_status,
                ProductionOrder.planned_quantity,

                Product.product_id,
                Product.product_name,

                Machine.machine_id,
                Machine.machine_name,

                ProcessStep.step_id,
                ProcessStep.step_name,

                MaterialLot.lot_id,
                MaterialLot.material_code,
                MaterialLot.supplier_batch_number,

                Supplier.supplier_id,
                Supplier.supplier_name,

                CorrectiveAction.capa_id,
                CorrectiveAction.lifecycle_status.label("capa_status"),
                CorrectiveAction.verification_result

            )
            .join(
                InspectionResult,
                Defect.inspection_id == InspectionResult.inspection_id
            )
            .join(
                ProductionOrder,
                Defect.order_id == ProductionOrder.order_id
            )
            .join(
                Product,
                ProductionOrder.product_id == Product.product_id
            )
            .outerjoin(
                OrderMachineExecution,
                Defect.execution_id == OrderMachineExecution.execution_id
            )
            .outerjoin(
                ProcessStep,
                OrderMachineExecution.step_id == ProcessStep.step_id
            )
            .outerjoin(
                Machine,
                OrderMachineExecution.machine_id == Machine.machine_id
            )
            .outerjoin(
                MaterialLot,
                Defect.lot_id == MaterialLot.lot_id
            )
            .outerjoin(
                Supplier,
                MaterialLot.supplier_id == Supplier.supplier_id
            )
            .outerjoin(
                CorrectiveAction,
                Defect.defect_id == CorrectiveAction.defect_id
            )
            .filter(Defect.defect_id == defect_id)
            .first()
        )

        if result is None:
            print("No traceability record found for:", defect_id)
            return

        print("\n========== YOTTAFLEX DEFECT TRACEABILITY ==========")

        print("\n1. DEFECT INFORMATION")
        print("Defect ID:", result.defect_id)
        print("Category:", result.defect_category)
        print("Description:", result.defect_description)
        print("Defect Quantity:", result.defect_quantity)
        print("Severity:", result.severity)

        print("\n2. INSPECTION INFORMATION")
        print("Inspection ID:", result.inspection_id)
        print("Status:", result.inspection_status)
        print("Inspected:", result.inspected_quantity)
        print("Passed:", result.passed_quantity)
        print("Failed:", result.failed_quantity)

        print("\n3. PRODUCTION INFORMATION")
        print("Order ID:", result.order_id)
        print("Order Status:", result.lifecycle_status)
        print("Planned Quantity:", result.planned_quantity)

        print("\n4. PRODUCT INFORMATION")
        print("Product ID:", result.product_id)
        print("Product Name:", result.product_name)

        print("\n5. MACHINE INFORMATION")
        print("Machine ID:", result.machine_id)
        print("Machine Name:", result.machine_name)
        print("Process Step:", result.step_name)

        print("\n6. MATERIAL LOT INFORMATION")
        print("Lot ID:", result.lot_id)
        print("Material Code:", result.material_code)
        print("Supplier Batch:", result.supplier_batch_number)

        print("\n7. SUPPLIER INFORMATION")
        print("Supplier ID:", result.supplier_id)
        print("Supplier Name:", result.supplier_name)

        print("\n8. CORRECTIVE ACTION INFORMATION")
        print("CAPA ID:", result.capa_id)
        print("CAPA Status:", result.capa_status)
        print("Verification:", result.verification_result)

        print("\n===================================================")

    except Exception as error:

        print("Traceability error:", error)
        raise

    finally:
        session.close()


if __name__ == "__main__":

    trace_defect("DEF-2026-000001")
