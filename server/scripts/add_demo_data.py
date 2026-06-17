"""One-off seeder to populate the local DB with demo users, rides, and
ride requests so screens look full for screenshots.

Usage:
    .venv/bin/python -m scripts.add_demo_data
"""
from datetime import datetime

from app.core import security
from app.db.database import SessionLocal
from app.models import models
from app.services.seed import CAMPUS_ID

DEMO_USERS = [
    ("Carla Souza", "carla.souza@aluno.ifsp.edu.br", "(17) 99700-3000"),
    ("Diego Almeida", "diego.almeida@aluno.ifsp.edu.br", "(17) 99700-4000"),
    ("Eduarda Lima", "eduarda.lima@aluno.ifsp.edu.br", "(17) 99700-5000"),
    ("Felipe Rocha", "felipe.rocha@aluno.ifsp.edu.br", "(17) 99700-6000"),
    ("Gabriela Nunes", "gabriela.nunes@aluno.ifsp.edu.br", "(17) 99700-7000"),
    ("Henrique Tavares", "henrique.tavares@aluno.ifsp.edu.br", "(17) 99700-8000"),
]

CAMPUS = "IFSP Campus Votuporanga"

DEMO_RIDES = [
    # (driver_email, direction, origin, destination, departure, price, seats, gathering, notes)
    (
        "carla.souza@aluno.ifsp.edu.br",
        models.RideDirection.ToCampus,
        "Fernandopolis",
        CAMPUS,
        datetime(2026, 5, 13, 6, 45),
        8,
        3,
        "Rodoviaria de Fernandopolis",
        "Saida pontual, paro na entrada do campus.",
    ),
    (
        "diego.almeida@aluno.ifsp.edu.br",
        models.RideDirection.ToCampus,
        "Rio Preto - Zona Sul",
        CAMPUS,
        datetime(2026, 5, 14, 7, 15),
        12,
        2,
        None,
        "Pego no caminho via Av. Brasil.",
    ),
    (
        "eduarda.lima@aluno.ifsp.edu.br",
        models.RideDirection.FromCampus,
        CAMPUS,
        "Votuporanga - Centro",
        datetime(2026, 5, 13, 18, 30),
        5,
        4,
        "Portaria principal",
        None,
    ),
    (
        "felipe.rocha@aluno.ifsp.edu.br",
        models.RideDirection.ToCampus,
        "Valentim Gentil",
        CAMPUS,
        datetime(2026, 5, 15, 7, 0),
        6,
        3,
        "Praca da Matriz",
        "Tenho ar condicionado.",
    ),
    (
        "gabriela.nunes@aluno.ifsp.edu.br",
        models.RideDirection.FromCampus,
        CAMPUS,
        "Alvares Florence",
        datetime(2026, 5, 16, 17, 45),
        7,
        3,
        None,
        "Volto direto, sem paradas.",
    ),
    (
        "henrique.tavares@aluno.ifsp.edu.br",
        models.RideDirection.ToCampus,
        "Cosmorama",
        CAMPUS,
        datetime(2026, 5, 18, 7, 30),
        10,
        2,
        "Posto Ipiranga BR-153",
        "Aceito embarque no caminho.",
    ),
    (
        "ana.motorista@aluno.ifsp.edu.br",
        models.RideDirection.ToCampus,
        "Centro de Votuporanga",
        CAMPUS,
        datetime(2026, 5, 20, 7, 0),
        5,
        3,
        "Praca Matriz",
        "Saida pontual.",
    ),
]

# (passenger_email, driver_email, ride_origin, pickup_address, message, status)
DEMO_REQUESTS = [
    (
        "bruno.passageiro@aluno.ifsp.edu.br",
        "carla.souza@aluno.ifsp.edu.br",
        "Fernandopolis",
        "Av. Brasilia, 1500 - Fernandopolis",
        "Posso ir ate a rodoviaria, obrigado!",
        models.PassengerStatus.Accepted,
    ),
    (
        "diego.almeida@aluno.ifsp.edu.br",
        "felipe.rocha@aluno.ifsp.edu.br",
        "Valentim Gentil",
        "Rua Sao Paulo, 220",
        "Tenho aula as 8h, da pra chegar antes?",
        models.PassengerStatus.Pending,
    ),
    (
        "eduarda.lima@aluno.ifsp.edu.br",
        "henrique.tavares@aluno.ifsp.edu.br",
        "Cosmorama",
        "Posto Ipiranga BR-153",
        None,
        models.PassengerStatus.Pending,
    ),
    # Requests aimed at "Gui" so the driver dashboard shows pending items.
    (
        "carla.souza@aluno.ifsp.edu.br",
        "gui@aluno.ifsp.edu.br",
        "fernandopolis",
        "Av. Brasil, 980 - Fernandopolis",
        "Posso pagar via Pix antes da viagem.",
        models.PassengerStatus.Pending,
    ),
    (
        "felipe.rocha@aluno.ifsp.edu.br",
        "gui@aluno.ifsp.edu.br",
        "fernandopolis",
        "Rua das Palmeiras, 45",
        "Levo mochila e notebook apenas.",
        models.PassengerStatus.Pending,
    ),
    # Requests from "Gui" so the passenger dashboard also has content.
    (
        "gui@aluno.ifsp.edu.br",
        "diego.almeida@aluno.ifsp.edu.br",
        "Rio Preto - Zona Sul",
        "Av. Bady Bassitt, 3200",
        "Tenho aula as 8h, agradeco a carona.",
        models.PassengerStatus.Accepted,
    ),
    (
        "gui@aluno.ifsp.edu.br",
        "gabriela.nunes@aluno.ifsp.edu.br",
        CAMPUS,
        "Saida da portaria principal",
        None,
        models.PassengerStatus.Pending,
    ),
]


def main() -> None:
    db = SessionLocal()
    try:
        password_hash = security.get_password_hash("demo1234")

        for name, email, phone in DEMO_USERS:
            if db.query(models.User).filter(models.User.email == email).first():
                continue
            db.add(
                models.User(
                    college_id=CAMPUS_ID,
                    name=name,
                    email=email,
                    phone=phone,
                    role=models.RoleType.Student,
                    password_hash=password_hash,
                )
            )
        db.flush()

        emails_to_users = {
            u.email: u for u in db.query(models.User).all()
        }

        for (
            driver_email,
            direction,
            origin,
            destination,
            departure,
            price,
            seats,
            gathering,
            notes,
        ) in DEMO_RIDES:
            driver = emails_to_users.get(driver_email)
            if driver is None:
                continue
            existing = (
                db.query(models.Ride)
                .filter(
                    models.Ride.rider_id == driver.id,
                    models.Ride.origin == origin,
                    models.Ride.destination == destination,
                    models.Ride.departure_time == departure,
                )
                .first()
            )
            if existing:
                continue
            db.add(
                models.Ride(
                    rider_id=driver.id,
                    direction=direction,
                    origin=origin,
                    destination=destination,
                    departure_time=departure,
                    price_per_seat=price,
                    available_seats=seats,
                    allow_custom_pickup=gathering is None,
                    fixed_gathering_point=gathering,
                    notes=notes,
                    status=models.RideStatus.Scheduled,
                )
            )
        db.flush()

        for (
            passenger_email,
            driver_email,
            ride_origin,
            pickup_address,
            message,
            req_status,
        ) in DEMO_REQUESTS:
            passenger = emails_to_users.get(passenger_email)
            driver = emails_to_users.get(driver_email)
            if not passenger or not driver:
                continue
            ride = (
                db.query(models.Ride)
                .filter(
                    models.Ride.rider_id == driver.id,
                    models.Ride.origin == ride_origin,
                    models.Ride.status == models.RideStatus.Scheduled,
                )
                .order_by(models.Ride.departure_time.asc())
                .first()
            )
            if not ride:
                continue
            existing = (
                db.query(models.RidePassenger)
                .filter(
                    models.RidePassenger.ride_id == ride.id,
                    models.RidePassenger.passenger_id == passenger.id,
                    models.RidePassenger.status.in_([
                        models.PassengerStatus.Pending,
                        models.PassengerStatus.Accepted,
                    ]),
                )
                .first()
            )
            if existing:
                continue
            db.add(
                models.RidePassenger(
                    ride_id=ride.id,
                    passenger_id=passenger.id,
                    pickup_address=pickup_address,
                    message=message,
                    status=req_status,
                )
            )

        # Seed a few notifications for Gui so the bell shows a count.
        gui = emails_to_users.get("gui@aluno.ifsp.edu.br")
        if gui:
            existing_titles = {
                n.title
                for n in db.query(models.Notification)
                .filter(models.Notification.user_id == gui.id)
                .all()
            }
            seed_notifs = [
                (
                    "Nova solicitacao",
                    "Carla Souza pediu uma vaga na sua carona de fernandopolis.",
                ),
                (
                    "Nova solicitacao",
                    "Felipe Rocha pediu uma vaga na sua carona de fernandopolis.",
                ),
                (
                    "Solicitacao aceita",
                    "Diego Almeida aceitou sua solicitacao para Rio Preto - Zona Sul -> IFSP Campus Votuporanga.",
                ),
            ]
            for title, message in seed_notifs:
                if title in existing_titles and message in {
                    n.message
                    for n in db.query(models.Notification)
                    .filter(models.Notification.user_id == gui.id)
                    .all()
                }:
                    continue
                db.add(
                    models.Notification(
                        user_id=gui.id,
                        title=title,
                        message=message,
                        read=False,
                    )
                )

        db.commit()
        print("Demo data seeded.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
