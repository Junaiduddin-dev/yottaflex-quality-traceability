
import random
from datetime import date

from faker import Faker

from database.connection import SessionLocal

from database.models import (
    Product,
    Supplier,
    Machine,
    BOM,
    BOMLine
)

from generator.config import (
    RANDOM_SEED,
    TOTAL_PRODUCTS,
    TOTAL_SUPPLIERS,
    TOTAL_MACHINES
)


# Independent random generators
random.seed(RANDOM_SEED)

fake = Faker()
fake.seed_instance(RANDOM_SEED)


PRODUCT_CATEGORIES = [
    "Electronics",
    "Automotive",
    "Industrial Equipment",
    "Medical Devices",
    "Consumer Electronics"
]

MATERIALS = [
    ("PCB-001", "Printed Circuit Board", "PCS"),
    ("CHIP-001", "Microcontroller Chip", "PCS"),
    ("RES-001", "Electronic Resistor", "PCS"),
    ("CAP-001", "Electronic Capacitor", "PCS"),
    ("SEN-001", "Sensor Module", "PCS"),
    ("CON-001", "Electrical Connector", "PCS"),
    ("BAT-001", "Lithium Battery", "PCS"),
    ("CAS-001", "Product Casing", "PCS")
]

MACHINE_TYPES = [
    "Assembly",
    "Testing",
    "Packaging",
    "Soldering",
    "Inspection"
]


def generate_products(session):

    print("Generating products...")

    products = []

    for i in range(1, TOTAL_PRODUCTS + 1):

        product = Product(
            product_id=f"SKU-{i:06d}",
            product_name=fake.unique.catch_phrase(),
            category=random.choice(PRODUCT_CATEGORIES),
            description=fake.sentence(),
            unit_of_measure="PCS",
            lifecycle_status="ACTIVE"
        )

        session.add(product)
        products.append(product)

    session.flush()

    print(f"Generated {len(products)} products.")

    return products


def generate_suppliers(session):

    print("Generating suppliers...")

    suppliers = []

    for i in range(1, TOTAL_SUPPLIERS + 1):

        supplier = Supplier(
            supplier_id=f"SUP-{i:06d}",
            supplier_name=fake.unique.company(),
            supplier_location=fake.city(),
            supplier_category=random.choice([
                "Electronic Components",
                "Raw Materials",
                "Packaging",
                "Mechanical Parts"
            ]),
            quality_rating=round(random.uniform(65, 100), 2),
            lifecycle_status="ACTIVE"
        )

        session.add(supplier)
        suppliers.append(supplier)

    session.flush()

    print(f"Generated {len(suppliers)} suppliers.")

    return suppliers


def generate_machines(session):

    print("Generating machines...")

    machines = []

    for i in range(1, TOTAL_MACHINES + 1):

        machine = Machine(
            machine_id=f"MCH-{i:06d}",
            machine_name=f"Production Machine {i:03d}",
            machine_type=random.choice(MACHINE_TYPES),
            location=f"Production Hall {random.choice(['A', 'B', 'C'])}",
            installation_date=fake.date_between(
                start_date="-5y",
                end_date="-1y"
            ),
            lifecycle_status="ACTIVE"
        )

        session.add(machine)
        machines.append(machine)

    session.flush()

    print(f"Generated {len(machines)} machines.")

    return machines


def generate_boms(session, products):

    print("Generating BOMs...")

    bom_count = 0
    bom_line_count = 0

    for i, product in enumerate(products, start=1):

        bom = BOM(
            bom_id=f"BOM-{i:06d}-V1",
            product_id=product.product_id,
            version=1,
            effective_from=date(2025, 1, 1),
            effective_to=None,
            lifecycle_status="ACTIVE"
        )

        session.add(bom)
        session.flush()

        # Each product gets between 3 and 5 materials
        selected_materials = random.sample(
            MATERIALS,
            random.randint(3, 5)
        )

        for material_code, description, unit in selected_materials:

            bom_line = BOMLine(
                bom_id=bom.bom_id,
                material_code=material_code,
                material_description=description,
                quantity_required=random.randint(1, 5),
                unit_of_measure=unit,
                scrap_allowance_pct=round(
                    random.uniform(0, 5), 2
                )
            )

            session.add(bom_line)
            bom_line_count += 1

        bom_count += 1

    session.flush()

    print(f"Generated {bom_count} BOMs.")
    print(f"Generated {bom_line_count} BOM material lines.")


def generate_master_data():

    session = SessionLocal()

    try:

        # Prevent accidental duplicate generation
        if session.query(Product).first():
            print(
                "Master data already exists. "
                "Please use a fresh database for full generation."
            )
            return

        print("\nYOTTAFLEX MASTER DATA GENERATOR")
        print("--------------------------------")

        products = generate_products(session)

        generate_suppliers(session)

        generate_machines(session)

        generate_boms(session, products)

        session.commit()

        print("--------------------------------")
        print("Master data generation completed!")

    except Exception as error:

        session.rollback()

        print("Generation failed:", error)

        raise

    finally:

        session.close()


if __name__ == "__main__":

    generate_master_data()
