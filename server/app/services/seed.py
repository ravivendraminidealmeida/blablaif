from datetime import datetime

from sqlalchemy.orm import Session

from app.core import security
from app.models import models
from app.schemas.ride import CAMPUS_NAME

CAMPUS_ID = 1
CAMPUS_ADDRESS = "Av. Jeronimo Figueira da Costa, 3014 - Pozzobon, Votuporanga - SP"


def seed_initial_data(db: Session) -> None:
    college = db.query(models.College).filter(models.College.id == CAMPUS_ID).first()
    if not college:
        college = models.College(
            id=CAMPUS_ID,
            name=CAMPUS_NAME,
            address=CAMPUS_ADDRESS,
        )
        db.add(college)
    else:
        college.name = CAMPUS_NAME
        college.address = CAMPUS_ADDRESS

    has_users = db.query(models.User).first() is not None
    if has_users:
        db.commit()
        return

    driver = models.User(
        college_id=CAMPUS_ID,
        name="Ana Motorista",
        email="ana.motorista@aluno.ifsp.edu.br",
        phone="(17) 99700-1000",
        role=models.RoleType.Student,
        password_hash=security.get_password_hash("demo1234"),
    )
    passenger = models.User(
        college_id=CAMPUS_ID,
        name="Bruno Passageiro",
        email="bruno.passageiro@aluno.ifsp.edu.br",
        phone="(17) 99700-2000",
        role=models.RoleType.Student,
        password_hash=security.get_password_hash("demo1234"),
    )
    db.add_all([driver, passenger])
    db.flush()

    db.add(
        models.Ride(
            rider_id=driver.id,
            direction=models.RideDirection.ToCampus,
            origin="Centro de Votuporanga",
            destination=CAMPUS_NAME,
            departure_time=datetime(2026, 6, 1, 7, 0),
            price_per_seat=5,
            available_seats=3,
            allow_custom_pickup=False,
            fixed_gathering_point="Praca Matriz",
            notes="Saida pontual.",
            status=models.RideStatus.Scheduled,
        )
    )
    db.commit()
