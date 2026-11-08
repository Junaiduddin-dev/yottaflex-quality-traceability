
import random

from datetime import timedelta

from database.connection import SessionLocal

from database.models import (
    Defect,
    CorrectiveAction
)

from generator.config import RANDOM_SEED


# =====================================================
# REPRODUCIBLE RANDOM DATA
# =====================================================

random.seed(RANDOM_SEED + 3)


ASSIGNEES = [
    "Quality Manager",
    "Production Engineer",
    "Supplier Quality Engineer",
    "Manufacturing Engineer",
    "Process Improvement Lead",
    "Quality Assurance Engineer"
]


ROOT_CAUSES = [
    "Insufficient process control caused variation during manufacturing.",
    "Incoming material did not consistently meet specification.",
    "Machine calibration drift affected product quality.",
    "Operator handling variation caused the defect.",
    "Inspection procedures did not detect the issue early.",
    "Supplier manufacturing variation affected component quality.",
    "Preventive maintenance was not performed at the required interval.",
    "Assembly process parameters were outside the recommended range."
]


CONTAINMENT_ACTIONS = [
    "Quarantine affected material lots and inspect all related inventory.",
    "Place affected production orders on quality hold.",
    "Perform 100 percent inspection of potentially affected units.",
    "Notify production and quality teams and isolate suspected components.",
    "Suspend use of the affected material batch until verification."
]


CORRECTIVE_ACTIONS = [
    "Rework affected units and correct the manufacturing process parameters.",
    "Recalibrate the machine and repeat the affected production operation.",
    "Replace nonconforming components and reinspect finished products.",
    "Correct the supplier material acceptance and inspection procedure.",
    "Investigate the process failure and implement the approved repair procedure."
]


PREVENTIVE_ACTIONS = [
    "Introduce periodic machine calibration and preventive maintenance checks.",
    "Add supplier quality monitoring and incoming material sampling.",
    "Train operators on the updated manufacturing work instructions.",
    "Introduce automated process parameter monitoring.",
    "Update the inspection checklist and increase inspection frequency.",
    "Review the process periodically to prevent recurrence."
]


# =====================================================
# 1. GENERATE CAPA RECORDS
# =====================================================

def generate_capa_records(session, defects):

    print("\nGenerating CAPA records...")

    total_capas = 0

    status_counts = {
        "OPEN": 0,
        "INVESTIGATION": 0,
        "ACTION_IN_PROGRESS": 0,
        "VERIFICATION": 0,
        "CLOSED": 0
    }

    for index, defect in enumerate(defects, start=1):

        # Open CAPA after defect detection.
        opened_at = defect.detected_at + timedelta(
            hours=random.randint(1, 24)
        )

        due_date = (
            opened_at.date()
            + timedelta(days=random.choice([14, 21, 30]))
        )

        # Select lifecycle status.
        lifecycle_status = random.choices(
            [
                "OPEN",
                "INVESTIGATION",
                "ACTION_IN_PROGRESS",
                "VERIFICATION",
                "CLOSED"
            ],
            weights=[15, 20, 25, 20, 20]
        )[0]

        # Default verification details.
        verified_at = None
        closed_at = None
        verification_result = "PENDING"

        # CLOSED CAPA must have successful verification.
        if lifecycle_status == "CLOSED":

            verification_result = "PASSED"

            verified_at = opened_at + timedelta(
                days=random.randint(2, 10)
            )

            closed_at = verified_at + timedelta(
                hours=random.randint(1, 48)
            )

        # Some verification-stage CAPAs may fail verification.
        elif lifecycle_status == "VERIFICATION":

            if random.random() < 0.35:

                verification_result = "FAILED"

                verified_at = opened_at + timedelta(
                    days=random.randint(2, 10)
                )

            else:

                verification_result = "PENDING"

        capa = CorrectiveAction(
            capa_id=f"CAPA-2026-{index:06d}",
            defect_id=defect.defect_id,

            root_cause=random.choice(ROOT_CAUSES),

            containment_action=random.choice(
                CONTAINMENT_ACTIONS
            ),

            corrective_action=random.choice(
                CORRECTIVE_ACTIONS
            ),

            preventive_action=random.choice(
                PREVENTIVE_ACTIONS
            ),

            assigned_to=random.choice(ASSIGNEES),

            opened_at=opened_at,
            due_date=due_date,

            verified_at=verified_at,
            closed_at=closed_at,

            verification_result=verification_result,
            lifecycle_status=lifecycle_status
        )

        session.add(capa)

        total_capas += 1
        status_counts[lifecycle_status] += 1

        if index % 500 == 0:

            session.flush()

            print(
                f"Generated {index}/{len(defects)} CAPA records..."
            )

    session.flush()

    print("\nCAPA generation completed.")

    print("Total CAPA records:", total_capas)

    print("\nCAPA lifecycle distribution:")

    for status, count in status_counts.items():

        print(f"{status}: {count}")

    return total_capas


# =====================================================
# 2. MAIN GENERATOR
# =====================================================

def generate_capa_data():

    session = SessionLocal()

    try:

        print("\nYOTTAFLEX CAPA DATA GENERATOR")
        print("--------------------------------------")

        # Prevent duplicate records.
        if session.query(CorrectiveAction).first():

            raise ValueError(
                "CAPA records already exist. "
                "Generation cancelled to prevent duplicates."
            )

        defects = session.query(Defect).order_by(
            Defect.defect_id
        ).all()

        if not defects:

            raise ValueError(
                "No defects found. Generate inspection data first."
            )

        print("Defects available:", len(defects))

        total_capas = generate_capa_records(
            session,
            defects
        )

        session.commit()

        print("\n--------------------------------------")
        print("CAPA DATA GENERATED SUCCESSFULLY!")
        print("--------------------------------------")

        print("Defects:", len(defects))
        print("CAPA records:", total_capas)

    except Exception as error:

        session.rollback()

        print("\nCAPA generation failed:", error)

        raise

    finally:

        session.close()


if __name__ == "__main__":

    generate_capa_data()
