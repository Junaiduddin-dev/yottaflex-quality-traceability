
from datetime import date, datetime

from sqlalchemy.exc import IntegrityError

from database.connection import SessionLocal
from database.models import CorrectiveAction, Defect


def validate_capa():

    session = SessionLocal()
    passed = 0
    failed = 0

    try:

        print("\nYOTTAFLEX CAPA VALIDATION REPORT")
        print("--------------------------------")

        # TEST 1: Validate existing CAPA records

        capas = session.query(CorrectiveAction).all()

        for capa in capas:

            valid = True

            if capa.lifecycle_status == "CLOSED":

                if (
                    capa.closed_at is None
                    or capa.verified_at is None
                    or capa.verification_result != "PASSED"
                ):
                    valid = False

                elif capa.closed_at < capa.verified_at:
                    valid = False

            if capa.verified_at and capa.verified_at < capa.opened_at:
                valid = False

            if valid:
                print(f"[PASS] {capa.capa_id}: CAPA lifecycle valid")
                passed += 1
            else:
                print(f"[FAIL] {capa.capa_id}: Invalid CAPA lifecycle")
                failed += 1

        # TEST 2: Attempt invalid CAPA closure

        defect = session.query(Defect).first()

        if defect:

            invalid_capa = CorrectiveAction(
                capa_id="TEST-CAPA-INVALID-001",
                defect_id=defect.defect_id,
                assigned_to="Validation Tester",
                opened_at=datetime.now(),
                due_date=date.today(),
                verified_at=None,
                closed_at=datetime.now(),
                verification_result="PENDING",
                lifecycle_status="CLOSED"
            )

            try:

                with session.begin_nested():

                    session.add(invalid_capa)
                    session.flush()

                print(
                    "[FAIL] Database allowed CAPA closure without verification"
                )
                failed += 1

            except IntegrityError:

                print(
                    "[PASS] Database rejected CAPA closure without verification"
                )
                passed += 1

        else:

            print("[FAIL] Cannot test CAPA closure: No defect exists")
            failed += 1

        print("--------------------------------")
        print("Passed checks:", passed)
        print("Failed checks:", failed)

        if failed == 0:
            print("CAPA VALIDATION RESULT: PASSED")
        else:
            print("CAPA VALIDATION RESULT: FAILED")

    finally:
        session.close()


if __name__ == "__main__":
    validate_capa()
