
import random

from datetime import timedelta

from database.connection import SessionLocal

from database.models import (
    Product,
    ProductionOrder,
    OrderMachineExecution,
    MaterialConsumption,
    InspectionPlan,
    InspectionResult,
    Defect
)

from generator.config import (
    RANDOM_SEED,
    TOTAL_INSPECTION_RESULTS
)


# =====================================================
# REPRODUCIBLE RANDOM DATA
# =====================================================

random.seed(RANDOM_SEED + 2)


INSPECTORS = [
    "Rahul Sharma",
    "Priya Reddy",
    "Arjun Kumar",
    "Sneha Rao",
    "Vikram Singh",
    "Ananya Patel",
    "Kiran Reddy",
    "Meera Nair"
]


INSPECTION_STAGES = {
    "INCOMING": {
        "name": "Incoming Material Inspection",
        "characteristic": "Material Dimension",
        "lower": 9.5,
        "upper": 10.5,
        "unit": "MM"
    },
    "IN_PROCESS": {
        "name": "In-Process Inspection",
        "characteristic": "Process Temperature",
        "lower": 20.0,
        "upper": 80.0,
        "unit": "C"
    },
    "FINAL": {
        "name": "Final Product Inspection",
        "characteristic": "Output Voltage",
        "lower": 4.5,
        "upper": 5.5,
        "unit": "V"
    }
}


DEFECTS = {
    "INCOMING": [
        "Material dimension out of specification",
        "Supplier material contamination",
        "Damaged incoming component"
    ],
    "IN_PROCESS": [
        "Process temperature deviation",
        "Incorrect component alignment",
        "Assembly process variation"
    ],
    "FINAL": [
        "Electrical output failure",
        "Functional performance failure",
        "Final product damage"
    ]
}


# =====================================================
# 1. GENERATE INSPECTION PLANS
# =====================================================

def generate_inspection_plans(session, products):

    print("\nGenerating inspection plans...")

    plans = {}

    for product in products:

        for stage, details in INSPECTION_STAGES.items():

            plan_id = (
                f"INSP-{product.product_id}-{stage}"
            )

            plan = InspectionPlan(
                inspection_plan_id=plan_id,
                product_id=product.product_id,
                inspection_name=details["name"],
                characteristic=details["characteristic"],
                inspection_stage=stage,
                lower_limit=details["lower"],
                upper_limit=details["upper"],
                unit_of_measure=details["unit"],
                sample_size=5,
                lifecycle_status="ACTIVE"
            )

            session.add(plan)

            plans[(product.product_id, stage)] = plan

    # Persist plans before creating inspection results.
    session.flush()

    print(f"Generated {len(plans)} inspection plans.")

    return plans


# =====================================================
# 2. GENERATE INSPECTION RESULTS AND DEFECTS
# =====================================================

def generate_inspection_results(
    session,
    orders,
    plans,
    executions_by_order,
    lots_by_order
):

    print("\nGenerating inspection results...")

    total_results = 0
    total_defects = 0

    pending_defects = []

    stages_per_order = [
        "INCOMING",
        "IN_PROCESS",
        "IN_PROCESS",
        "FINAL"
    ]

    expected_results = len(orders) * len(stages_per_order)

    if TOTAL_INSPECTION_RESULTS != expected_results:

        raise ValueError(
            f"Expected {TOTAL_INSPECTION_RESULTS} inspections, "
            f"but order count and inspection stages produce "
            f"{expected_results}."
        )

    defect_counter = 0

    for order_index, order in enumerate(orders, start=1):

        executions = executions_by_order.get(
            order.order_id,
            []
        )

        consumed_lots = lots_by_order.get(
            order.order_id,
            []
        )

        if not executions:

            raise ValueError(
                f"No machine executions found for {order.order_id}"
            )

        for inspection_number, stage in enumerate(
            stages_per_order,
            start=1
        ):

            plan = plans[(order.product_id, stage)]

            execution = executions[
                (inspection_number - 1) % len(executions)
            ]

            inspected_quantity = random.randint(5, 10)

            failed_quantity = random.choices(
                [0, 1, 2],
                weights=[80, 15, 5]
            )[0]

            failed_quantity = min(
                failed_quantity,
                inspected_quantity
            )

            passed_quantity = (
                inspected_quantity - failed_quantity
            )

            inspection_status = (
                "FAIL" if failed_quantity > 0 else "PASS"
            )

            if inspection_status == "PASS":

                measured_value = round(
                    random.uniform(
                        plan.lower_limit,
                        plan.upper_limit
                    ),
                    2
                )

            else:

                measured_value = round(
                    random.choice([
                        plan.lower_limit - random.uniform(0.1, 1.0),
                        plan.upper_limit + random.uniform(0.1, 1.0)
                    ]),
                    2
                )

            inspection_date = (
                execution.end_time
                if execution.end_time
                else order.start_date
            )

            inspection_date += timedelta(
                minutes=inspection_number
            )

            inspection_id = (
                f"INSP-{order.order_id}-{inspection_number:03d}"
            )

            result = InspectionResult(
                inspection_id=inspection_id,
                inspection_plan_id=plan.inspection_plan_id,
                order_id=order.order_id,
                execution_id=execution.execution_id,
                inspection_date=inspection_date,
                inspected_quantity=inspected_quantity,
                passed_quantity=passed_quantity,
                failed_quantity=failed_quantity,
                measured_value=measured_value,
                inspection_status=inspection_status,
                inspector_name=random.choice(INSPECTORS)
            )

            session.add(result)

            total_results += 1

            # Collect defects separately.
            # They will be inserted after all inspection results.

            if failed_quantity > 0:

                defect_counter += 1

                category = random.choice(
                    DEFECTS[stage]
                )

                lot_id = (
                    random.choice(consumed_lots).lot_id
                    if consumed_lots
                    else None
                )

                defect = Defect(
                    defect_id=f"DEF-2026-{defect_counter:06d}",
                    inspection_id=inspection_id,
                    order_id=order.order_id,
                    execution_id=execution.execution_id,
                    lot_id=lot_id,
                    defect_category=category,
                    defect_description=(
                        f"{category}. "
                        f"Detected during {stage} inspection "
                        f"for order {order.order_id}."
                    ),
                    defect_quantity=failed_quantity,
                    severity=random.choices(
                        ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                        weights=[40, 35, 20, 5]
                    )[0],
                    detected_at=inspection_date,
                    defect_status=random.choice([
                        "OPEN",
                        "UNDER_REVIEW",
                        "CONTAINED"
                    ])
                )

                pending_defects.append(defect)

                total_defects += 1

        # Flush inspection results periodically.
        # No defect records are inserted in this step.

        if order_index % 500 == 0:

            session.flush()

            print(
                f"Generated {total_results}/"
                f"{TOTAL_INSPECTION_RESULTS} inspections..."
            )

    # =================================================
    # INSERT INSPECTION RESULTS FIRST
    # =================================================

    session.flush()

    print("\nAll inspection results inserted successfully.")

    # =================================================
    # INSERT DEFECTS AFTER THEIR INSPECTIONS EXIST
    # =================================================

    session.add_all(pending_defects)

    session.flush()

    print("\nInspection generation completed.")

    print("Inspection results:", total_results)

    print("Defect records:", total_defects)


# =====================================================
# 3. MAIN GENERATOR
# =====================================================

def generate_inspection_data():

    session = SessionLocal()

    try:

        print("\nYOTTAFLEX QUALITY DATA GENERATOR")
        print("--------------------------------------")

        if (
            session.query(InspectionPlan).first()
            or session.query(InspectionResult).first()
            or session.query(Defect).first()
        ):

            raise ValueError(
                "Quality data already exists. "
                "Generation cancelled to prevent duplicates."
            )

        products = session.query(Product).order_by(
            Product.product_id
        ).all()

        orders = session.query(ProductionOrder).order_by(
            ProductionOrder.order_id
        ).all()

        executions = session.query(
            OrderMachineExecution
        ).order_by(
            OrderMachineExecution.execution_id
        ).all()

        consumptions = session.query(
            MaterialConsumption
        ).all()

        if not products or not orders or not executions:

            raise ValueError(
                "Required production data is missing."
            )

        executions_by_order = {}

        for execution in executions:

            executions_by_order.setdefault(
                execution.order_id,
                []
            ).append(execution)

        lots_by_order = {}

        for consumption in consumptions:

            lots_by_order.setdefault(
                consumption.order_id,
                []
            ).append(consumption)

        plans = generate_inspection_plans(
            session,
            products
        )

        generate_inspection_results(
            session,
            orders,
            plans,
            executions_by_order,
            lots_by_order
        )

        session.commit()

        print("\n--------------------------------------")
        print("QUALITY DATA GENERATED SUCCESSFULLY!")
        print("--------------------------------------")

    except Exception as error:

        session.rollback()

        print("\nQuality generation failed:", error)

        raise

    finally:

        session.close()


if __name__ == "__main__":

    generate_inspection_data()
