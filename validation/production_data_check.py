
from database.connection import SessionLocal

from database.models import (
    MaterialLot,
    ProductionOrder,
    MaterialConsumption,
    ProcessStep,
    OrderMachineExecution
)


def verify_production_data():

    session = SessionLocal()

    try:
        print("\nYOTTAFLEX PRODUCTION DATA VERIFICATION")
        print("--------------------------------------")

        counts = {
            "Material Lots": session.query(MaterialLot).count(),
            "Production Orders": session.query(ProductionOrder).count(),
            "Material Consumption Records": session.query(MaterialConsumption).count(),
            "Process Steps": session.query(ProcessStep).count(),
            "Machine Executions": session.query(OrderMachineExecution).count()
        }

        for name, count in counts.items():
            print(f"{name}: {count:,}")

        print("--------------------------------------")

        checks = [
            counts["Material Lots"] == 2000,
            counts["Production Orders"] == 5000,
            counts["Material Consumption Records"] > 0,
            counts["Process Steps"] == 15000,
            counts["Machine Executions"] == 15000
        ]

        if all(checks):
            print("PRODUCTION DATA VERIFICATION: PASSED")
        else:
            print("PRODUCTION DATA VERIFICATION: FAILED")

    finally:
        session.close()


if __name__ == "__main__":
    verify_production_data()
