
from database.connection import SessionLocal

from database.models import (
    Defect,
    CorrectiveAction
)


def verify_capa_data():

    session = SessionLocal()

    try:

        print("\nYOTTAFLEX CAPA VERIFICATION")
        print("--------------------------------")

        defects_count = session.query(Defect).count()

        capa_count = session.query(CorrectiveAction).count()

        print("Defects:", defects_count)
        print("CAPA records:", capa_count)

        invalid_count = 0

        for capa in session.query(CorrectiveAction).all():

            # Check verification date
            if (
                capa.verified_at is not None
                and capa.verified_at < capa.opened_at
            ):
                invalid_count += 1

            # Check closure rules
            if capa.lifecycle_status == "CLOSED":

                if (
                    capa.verified_at is None
                    or capa.closed_at is None
                    or capa.verification_result != "PASSED"
                    or capa.closed_at < capa.verified_at
                ):
                    invalid_count += 1

        closed_count = session.query(
            CorrectiveAction
        ).filter_by(
            lifecycle_status="CLOSED"
        ).count()

        print("Closed CAPAs:", closed_count)
        print("Invalid CAPA records:", invalid_count)

        print("--------------------------------")

        if defects_count == capa_count and invalid_count == 0:
            print("CAPA VERIFICATION: PASSED")
        else:
            print("CAPA VERIFICATION: FAILED")

    finally:
        session.close()


if __name__ == "__main__":
    verify_capa_data()
