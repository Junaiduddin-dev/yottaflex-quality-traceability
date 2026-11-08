
from database.models import (
    InspectionPlan,
    InspectionResult,
    Defect
)

models = [
    InspectionPlan,
    InspectionResult,
    Defect
]

for model in models:

    print("\n" + "=" * 50)
    print(model.__name__)
    print("=" * 50)

    for constraint in model.__table__.constraints:

        if hasattr(constraint, "sqltext"):
            print(
                f"{constraint.name}: "
                f"{constraint.sqltext}"
            )
