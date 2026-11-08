
from database.connection import SessionLocal

from database.models import (
    InspectionPlan,
    InspectionResult,
    Defect
)

session = SessionLocal()

try:
    print("Inspection plans:", session.query(InspectionPlan).count())
    print("Inspection results:", session.query(InspectionResult).count())
    print("Defects:", session.query(Defect).count())

finally:
    session.close()
