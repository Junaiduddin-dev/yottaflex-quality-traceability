
import random
from datetime import date, datetime, time, timedelta

from faker import Faker

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
    OrderMachineExecution
)

from generator.config import (
    RANDOM_SEED,
    TOTAL_MATERIAL_LOTS,
    TOTAL_PRODUCTION_ORDERS,
    DATA_START_DATE,
    DATA_END_DATE
)


# =====================================================
# REPRODUCIBLE RANDOM GENERATORS
# =====================================================

random.seed(RANDOM_SEED + 1)

fake = Faker()
fake.seed_instance(RANDOM_SEED + 1)


# =====================================================
# HELPER: GENERATE RANDOM MANUFACTURING DATE
# =====================================================

START_DATE = date.fromisoformat(DATA_START_DATE)
END_DATE = date.fromisoformat(DATA_END_DATE)


def random_manufacturing_date():

    return fake.date_between(
        start_date=START_DATE,
        end_date=END_DATE
    )


# =====================================================
# 1. GENERATE MATERIAL LOTS
# =====================================================

def generate_material_lots(session, suppliers):

    print("\nGenerating material lots...")

    material_codes = [
        "PCB-001",
        "CHIP-001",
        "RES-001",
        "CAP-001",
        "SEN-001",
        "CON-001",
        "BAT-001",
        "CAS-001"
    ]

    material_descriptions = {
        "PCB-001": ("Printed Circuit Board", "PCS"),
        "CHIP-001": ("Microcontroller Chip", "PCS"),
        "RES-001": ("Electronic Resistor", "PCS"),
        "CAP-001": ("Electronic Capacitor", "PCS"),
        "SEN-001": ("Sensor Module", "PCS"),
        "CON-001": ("Electrical Connector", "PCS"),
        "BAT-001": ("Lithium Battery", "PCS"),
        "CAS-001": ("Product Casing", "PCS")
    }

    lots_by_material = {
        code: [] for code in material_codes
    }

    supplier_counters = {
        supplier.supplier_id: 0
        for supplier in suppliers
    }

    lots = []

    for i in range(1, TOTAL_MATERIAL_LOTS + 1):

        supplier = random.choice(suppliers)

        material_code = random.choice(material_codes)

        description, unit = material_descriptions[material_code]

        supplier_counters[supplier.supplier_id] += 1

        counter = supplier_counters[supplier.supplier_id]

        lot_id = (
            f"LOT-{supplier.supplier_id}-2026-{counter:06d}"
        )

        received_quantity = random.randint(1000, 5000)

        received_date = random_manufacturing_date()

        expiry_date = received_date + timedelta(
            days=random.randint(365, 1095)
        )

        lot = MaterialLot(
            lot_id=lot_id,
            supplier_id=supplier.supplier_id,
            material_code=material_code,
            supplier_batch_number=f"BATCH-{i:07d}",
            received_quantity=received_quantity,
            available_quantity=received_quantity,
            unit_of_measure=unit,
            received_date=received_date,
            expiry_date=expiry_date,
            inspection_status="ACCEPTED",
            lifecycle_status="AVAILABLE"
        )

        session.add(lot)

        lots.append(lot)

        lots_by_material[material_code].append(lot)

    session.flush()

    print(f"Generated {len(lots)} material lots.")

    return lots_by_material


# =====================================================
# 2. CONSUME MATERIAL FROM AVAILABLE LOTS
# =====================================================

def consume_material(
    session,
    order,
    bom_line,
    required_quantity,
    lots_by_material,
    consumption_date
):

    material_code = bom_line.material_code

    available_lots = lots_by_material.get(
        material_code,
        []
    )

    remaining_quantity = float(required_quantity)

    for lot in available_lots:

        if remaining_quantity <= 0:
            break

        if lot.available_quantity <= 0:
            continue

        quantity_to_consume = min(
            lot.available_quantity,
            remaining_quantity
        )

        consumption = MaterialConsumption(
            order_id=order.order_id,
            lot_id=lot.lot_id,
            material_code=material_code,
            consumed_quantity=quantity_to_consume,
            consumption_date=consumption_date
        )

        session.add(consumption)

        lot.available_quantity -= quantity_to_consume

        if lot.available_quantity <= 0:
            lot.available_quantity = 0
            lot.lifecycle_status = "CONSUMED"

        else:
            lot.lifecycle_status = "PARTIALLY_USED"

        remaining_quantity -= quantity_to_consume

    if remaining_quantity > 0.000001:

        raise ValueError(
            f"Insufficient material stock for {material_code}. "
            f"Shortage: {remaining_quantity}"
        )


# =====================================================
# 3. GENERATE PRODUCTION ORDERS
# =====================================================

def generate_production_orders(
    session,
    products,
    boms,
    machines,
    lots_by_material
):

    print("\nGenerating production orders...")

    total_consumption_records = 0
    total_process_steps = 0
    total_executions = 0

    # Map products to their BOMs
    bom_by_product = {
        bom.product_id: bom
        for bom in boms
    }

    for i in range(1, TOTAL_PRODUCTION_ORDERS + 1):

        product = random.choice(products)

        bom = bom_by_product[product.product_id]

        planned_quantity = random.randint(10, 100)

        actual_quantity = random.randint(
            int(planned_quantity * 0.90),
            planned_quantity
        )

        start_day = random_manufacturing_date()

        start_datetime = datetime.combine(
            start_day,
            time(8, 0)
        ) + timedelta(hours=random.randint(0, 4))

        end_datetime = start_datetime + timedelta(
            hours=random.randint(3, 10)
        )

        order = ProductionOrder(
            order_id=f"WO-2026-{i:06d}",
            product_id=product.product_id,
            bom_id=bom.bom_id,
            planned_quantity=planned_quantity,
            actual_quantity=actual_quantity,
            start_date=start_datetime,
            end_date=end_datetime,
            priority=random.choice([
                "LOW",
                "MEDIUM",
                "HIGH"
            ]),
            lifecycle_status="COMPLETED"
        )

        session.add(order)

        # Ensure order exists before dependent records
        session.flush()

        # -------------------------------------------------
        # MATERIAL CONSUMPTION
        # -------------------------------------------------

        bom_lines = session.query(BOMLine).filter_by(
            bom_id=bom.bom_id
        ).all()

        for bom_line in bom_lines:

            required_quantity = (
                bom_line.quantity_required * actual_quantity
            )

            consume_material(
                session=session,
                order=order,
                bom_line=bom_line,
                required_quantity=required_quantity,
                lots_by_material=lots_by_material,
                consumption_date=start_datetime
            )

            total_consumption_records += 1

        # -------------------------------------------------
        # PROCESS STEPS AND MACHINE EXECUTIONS
        # -------------------------------------------------

        operation_names = [
            "Material Preparation",
            "Assembly",
            "Electrical Testing",
            "Quality Inspection",
            "Packaging"
        ]

        selected_operations = operation_names[:3]

        current_time = start_datetime

        for sequence, operation_name in enumerate(
            selected_operations,
            start=1
        ):

            machine = random.choice(machines)

            duration = random.randint(30, 90)

            step_end = current_time + timedelta(
                minutes=duration
            )

            step = ProcessStep(
                step_id=f"STEP-{i:06d}-{sequence:02d}",
                order_id=order.order_id,
                machine_id=machine.machine_id,
                step_name=operation_name,
                sequence_number=sequence,
                start_time=current_time,
                end_time=step_end,
                temperature=round(
                    random.uniform(20, 80),
                    2
                ),
                pressure=round(
                    random.uniform(1, 5),
                    2
                ),
                process_status="COMPLETED"
            )

            session.add(step)

            session.flush()

            execution = OrderMachineExecution(
                order_id=order.order_id,
                machine_id=machine.machine_id,
                step_id=step.step_id,
                start_time=current_time,
                end_time=step_end
            )

            session.add(execution)

            total_process_steps += 1
            total_executions += 1

            current_time = step_end

        # Periodic progress display
        if i % 500 == 0:

            print(
                f"Generated {i}/{TOTAL_PRODUCTION_ORDERS} "
                "production orders..."
            )

    session.flush()

    print("\nProduction generation completed.")

    print("Production orders:", TOTAL_PRODUCTION_ORDERS)

    print("Material consumption records:", total_consumption_records)

    print("Process steps:", total_process_steps)

    print("Machine executions:", total_executions)


# =====================================================
# 4. MAIN GENERATOR
# =====================================================

def generate_production_data():

    session = SessionLocal()

    try:

        print("\nYOTTAFLEX PRODUCTION DATA GENERATOR")
        print("--------------------------------------")

        # Prevent duplicate production generation
        if session.query(MaterialLot).first():

            print(
                "Material lots already exist. "
                "Generation cancelled to prevent duplicates."
            )

            return

        if session.query(ProductionOrder).first():

            print(
                "Production orders already exist. "
                "Generation cancelled."
            )

            return

        suppliers = session.query(Supplier).all()

        products = session.query(Product).all()

        boms = session.query(BOM).all()

        machines = session.query(Machine).all()

        if not suppliers or not products or not boms or not machines:

            raise ValueError(
                "Master data is missing. "
                "Generate master data first."
            )

        # Generate lots
        lots_by_material = generate_material_lots(
            session,
            suppliers
        )

        # Generate production orders and related records
        generate_production_orders(
            session,
            products,
            boms,
            machines,
            lots_by_material
        )

        session.commit()

        print("\n--------------------------------------")
        print("Production dataset generated successfully!")
        print("--------------------------------------")

    except Exception as error:

        session.rollback()

        print("\nProduction generation failed:", error)

        raise

    finally:

        session.close()


if __name__ == "__main__":

    generate_production_data()
