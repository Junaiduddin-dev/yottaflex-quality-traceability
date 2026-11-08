
from sqlalchemy import inspect
from database.connection import engine
from database import models


def verify_database():

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    expected_tables = {
        "products",
        "suppliers",
        "machines",
        "boms",
        "bom_lines",
        "material_lots",
        "production_orders",
        "material_consumptions",
        "process_steps",
        "order_machine_executions",
        "inspection_plans",
        "inspection_results",
        "defects",
        "corrective_actions",
        "audit_events"
    }

    print("\nYottaFlex Database Verification")
    print("--------------------------------")

    for table in sorted(tables):
        print(f"Table found: {table}")

    print("--------------------------------")
    print(f"Total tables: {len(tables)}")

    missing_tables = expected_tables - set(tables)

    if not missing_tables:
        print("All 15 expected tables verified!")
    else:
        print("Missing tables:", sorted(missing_tables))


if __name__ == "__main__":
    verify_database()
