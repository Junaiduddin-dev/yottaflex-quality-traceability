
from database.connection import engine, Base

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


def initialize_database():

    print("Initializing YottaFlex database...")

    Base.metadata.create_all(bind=engine)

    print("Database tables created successfully!")


if __name__ == "__main__":
    initialize_database()
