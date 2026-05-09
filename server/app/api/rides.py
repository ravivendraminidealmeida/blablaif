from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models import models
from app.schemas import notification as notification_schema
from app.schemas import ride as ride_schema

router = APIRouter()


def _create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
) -> None:
    db.add(
        models.Notification(
            user_id=user_id,
            title=title,
            message=message,
        )
    )


def _accepted_count(ride: models.Ride) -> int:
    return sum(
        1 for request in ride.passengers
        if request.status == models.PassengerStatus.Accepted
    )


def _active_request_for_user(ride: models.Ride, user_id: int):
    return next(
        (
            request for request in ride.passengers
            if request.passenger_id == user_id
            and request.status in {
                models.PassengerStatus.Pending,
                models.PassengerStatus.Accepted,
            }
        ),
        None,
    )


def _ride_response(
    ride: models.Ride,
    current_user: models.User,
    include_requests: bool = False,
) -> ride_schema.RideResponse:
    accepted_count = _accepted_count(ride)
    current_user_request = _active_request_for_user(ride, current_user.id)
    requests = []

    if include_requests:
        for request in ride.passengers:
            passenger_phone = (
                request.passenger.phone
                if request.status == models.PassengerStatus.Accepted
                else None
            )
            requests.append(
                ride_schema.RideRequestResponse(
                    id=request.id,
                    ride_id=request.ride_id,
                    passenger_id=request.passenger_id,
                    pickup_address=request.pickup_address,
                    message=request.message,
                    status=request.status,
                    passenger=ride_schema.UserSummary(
                        id=request.passenger.id,
                        name=request.passenger.name,
                        email=request.passenger.email,
                        phone=passenger_phone,
                    ),
                )
            )

    rider_phone = None
    if current_user.id == ride.rider_id:
        rider_phone = ride.rider.phone
    elif current_user_request and current_user_request.status == models.PassengerStatus.Accepted:
        rider_phone = ride.rider.phone

    return ride_schema.RideResponse(
        id=ride.id,
        rider_id=ride.rider_id,
        direction=ride.direction,
        origin=ride.origin,
        destination=ride.destination,
        departure_time=ride.departure_time,
        price_per_seat=ride.price_per_seat,
        available_seats=ride.available_seats,
        accepted_seats=accepted_count,
        allow_custom_pickup=ride.allow_custom_pickup,
        fixed_gathering_point=ride.fixed_gathering_point,
        notes=ride.notes,
        status=ride.status,
        rider_name=ride.rider.name,
        rider_phone=rider_phone,
        current_user_request_status=current_user_request.status if current_user_request else None,
        requests=requests,
    )


def _get_ride_or_404(db: Session, ride_id: int) -> models.Ride:
    ride = (
        db.query(models.Ride)
        .options(
            joinedload(models.Ride.rider),
            joinedload(models.Ride.passengers).joinedload(models.RidePassenger.passenger),
        )
        .filter(models.Ride.id == ride_id)
        .first()
    )
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    return ride


def _get_request_or_404(db: Session, request_id: int) -> models.RidePassenger:
    ride_request = (
        db.query(models.RidePassenger)
        .options(
            joinedload(models.RidePassenger.passenger),
            joinedload(models.RidePassenger.ride)
            .joinedload(models.Ride.rider),
            joinedload(models.RidePassenger.ride)
            .joinedload(models.Ride.passengers)
            .joinedload(models.RidePassenger.passenger),
        )
        .filter(models.RidePassenger.id == request_id)
        .first()
    )
    if not ride_request:
        raise HTTPException(status_code=404, detail="Ride request not found")
    return ride_request


@router.get("/rides", response_model=list[ride_schema.RideResponse])
def list_available_rides(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    rides = (
        db.query(models.Ride)
        .options(
            joinedload(models.Ride.rider),
            joinedload(models.Ride.passengers).joinedload(models.RidePassenger.passenger),
        )
        .join(models.User, models.Ride.rider_id == models.User.id)
        .filter(
            models.Ride.status == models.RideStatus.Scheduled,
            models.User.college_id == current_user.college_id,
        )
        .order_by(models.Ride.departure_time.asc())
        .all()
    )
    return [_ride_response(ride, current_user) for ride in rides]


@router.get("/notifications", response_model=list[notification_schema.NotificationResponse])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.Notification)
        .filter(models.Notification.user_id == current_user.id)
        .order_by(models.Notification.created_at.desc(), models.Notification.id.desc())
        .limit(20)
        .all()
    )


@router.patch("/notifications/read", response_model=list[notification_schema.NotificationResponse])
def mark_notifications_read(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    notifications = (
        db.query(models.Notification)
        .filter(models.Notification.user_id == current_user.id)
        .all()
    )
    for notification in notifications:
        notification.read = True

    db.commit()
    return list_notifications(db, current_user)


@router.post("/rides", response_model=ride_schema.RideResponse, status_code=status.HTTP_201_CREATED)
def create_ride(
    ride_in: ride_schema.RideCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ride = models.Ride(
        rider_id=current_user.id,
        direction=ride_in.direction,
        origin=ride_in.origin,
        destination=ride_in.destination,
        departure_time=ride_in.departure_time,
        price_per_seat=ride_in.price_per_seat,
        available_seats=ride_in.available_seats,
        allow_custom_pickup=ride_in.allow_custom_pickup,
        fixed_gathering_point=ride_in.fixed_gathering_point,
        notes=ride_in.notes,
        status=models.RideStatus.Scheduled,
    )
    db.add(ride)
    db.commit()
    db.refresh(ride)
    return _ride_response(_get_ride_or_404(db, ride.id), current_user, include_requests=True)


@router.get("/rides/mine", response_model=list[ride_schema.RideResponse])
def list_my_rides(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    rides = (
        db.query(models.Ride)
        .options(
            joinedload(models.Ride.rider),
            joinedload(models.Ride.passengers).joinedload(models.RidePassenger.passenger),
        )
        .filter(models.Ride.rider_id == current_user.id)
        .order_by(models.Ride.departure_time.asc())
        .all()
    )
    return [_ride_response(ride, current_user, include_requests=True) for ride in rides]


@router.patch("/rides/{ride_id}/cancel", response_model=ride_schema.RideResponse)
def cancel_ride(
    ride_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ride = _get_ride_or_404(db, ride_id)
    if ride.rider_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the driver can cancel this ride")
    if ride.status != models.RideStatus.Scheduled:
        raise HTTPException(status_code=400, detail="Only scheduled rides can be cancelled")

    ride.status = models.RideStatus.Cancelled
    for ride_request in ride.passengers:
        if ride_request.status in {
            models.PassengerStatus.Pending,
            models.PassengerStatus.Accepted,
        }:
            _create_notification(
                db,
                ride_request.passenger_id,
                "Carona cancelada",
                f"{current_user.name} cancelou a carona de {ride.origin} para {ride.destination}.",
            )
    db.commit()
    db.refresh(ride)
    return _ride_response(_get_ride_or_404(db, ride.id), current_user, include_requests=True)


@router.post(
    "/rides/{ride_id}/requests",
    response_model=ride_schema.RideRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def request_ride(
    ride_id: int,
    request_in: ride_schema.RideRequestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ride = _get_ride_or_404(db, ride_id)
    if ride.status != models.RideStatus.Scheduled:
        raise HTTPException(status_code=400, detail="Ride is not available")
    if ride.rider_id == current_user.id:
        raise HTTPException(status_code=400, detail="Drivers cannot request their own ride")
    if _accepted_count(ride) >= ride.available_seats:
        raise HTTPException(status_code=400, detail="Ride has no available seats")
    if _active_request_for_user(ride, current_user.id):
        raise HTTPException(status_code=400, detail="You already have an active request for this ride")

    ride_request = models.RidePassenger(
        ride_id=ride.id,
        passenger_id=current_user.id,
        pickup_address=request_in.pickup_address,
        message=request_in.message,
        status=models.PassengerStatus.Pending,
    )
    db.add(ride_request)
    db.commit()
    db.refresh(ride_request)
    return ride_schema.RideRequestResponse(
        id=ride_request.id,
        ride_id=ride_request.ride_id,
        passenger_id=ride_request.passenger_id,
        pickup_address=ride_request.pickup_address,
        message=ride_request.message,
        status=ride_request.status,
    )


@router.get("/ride-requests/mine", response_model=list[ride_schema.RideRequestResponse])
def list_my_requests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    requests = (
        db.query(models.RidePassenger)
        .options(
            joinedload(models.RidePassenger.passenger),
            joinedload(models.RidePassenger.ride).joinedload(models.Ride.rider),
        )
        .filter(models.RidePassenger.passenger_id == current_user.id)
        .order_by(models.RidePassenger.id.desc())
        .all()
    )

    return [
        ride_schema.RideRequestResponse(
            id=request.id,
            ride_id=request.ride_id,
            passenger_id=request.passenger_id,
            pickup_address=request.pickup_address,
            message=request.message,
            status=request.status,
            ride=ride_schema.RideSummary(
                id=request.ride.id,
                direction=request.ride.direction,
                origin=request.ride.origin,
                destination=request.ride.destination,
                departure_time=request.ride.departure_time,
                price_per_seat=request.ride.price_per_seat,
                rider_name=request.ride.rider.name,
            ),
            driver_phone=(
                request.ride.rider.phone
                if request.status == models.PassengerStatus.Accepted
                else None
            ),
        )
        for request in requests
    ]


@router.patch("/ride-requests/{request_id}/accept", response_model=ride_schema.RideRequestResponse)
def accept_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ride_request = _get_request_or_404(db, request_id)
    if ride_request.ride.rider_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the driver can accept this request")
    if ride_request.status != models.PassengerStatus.Pending:
        raise HTTPException(status_code=400, detail="Only pending requests can be accepted")
    if _accepted_count(ride_request.ride) >= ride_request.ride.available_seats:
        raise HTTPException(status_code=400, detail="Ride has no available seats")

    ride_request.status = models.PassengerStatus.Accepted
    _create_notification(
        db,
        ride_request.passenger_id,
        "Solicitacao aceita",
        f"{current_user.name} aceitou sua solicitacao para {ride_request.ride.origin} -> {ride_request.ride.destination}.",
    )
    db.commit()
    db.refresh(ride_request)
    return _request_response_for_driver(ride_request)


@router.patch("/ride-requests/{request_id}/reject", response_model=ride_schema.RideRequestResponse)
def reject_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ride_request = _get_request_or_404(db, request_id)
    if ride_request.ride.rider_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the driver can reject this request")
    if ride_request.status != models.PassengerStatus.Pending:
        raise HTTPException(status_code=400, detail="Only pending requests can be rejected")

    ride_request.status = models.PassengerStatus.Rejected
    _create_notification(
        db,
        ride_request.passenger_id,
        "Solicitacao recusada",
        f"{current_user.name} recusou sua solicitacao para {ride_request.ride.origin} -> {ride_request.ride.destination}.",
    )
    db.commit()
    db.refresh(ride_request)
    return _request_response_for_driver(ride_request)


@router.patch("/ride-requests/{request_id}/cancel", response_model=ride_schema.RideRequestResponse)
def cancel_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ride_request = _get_request_or_404(db, request_id)
    if ride_request.passenger_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the passenger can cancel this request")
    if ride_request.status not in {
        models.PassengerStatus.Pending,
        models.PassengerStatus.Accepted,
    }:
        raise HTTPException(status_code=400, detail="Only pending or accepted requests can be cancelled")

    ride_request.status = models.PassengerStatus.Cancelled
    _create_notification(
        db,
        ride_request.ride.rider_id,
        "Solicitacao cancelada",
        f"{current_user.name} cancelou a solicitacao para {ride_request.ride.origin} -> {ride_request.ride.destination}.",
    )
    db.commit()
    db.refresh(ride_request)
    return ride_schema.RideRequestResponse(
        id=ride_request.id,
        ride_id=ride_request.ride_id,
        passenger_id=ride_request.passenger_id,
        pickup_address=ride_request.pickup_address,
        message=ride_request.message,
        status=ride_request.status,
    )


def _request_response_for_driver(
    ride_request: models.RidePassenger,
) -> ride_schema.RideRequestResponse:
    return ride_schema.RideRequestResponse(
        id=ride_request.id,
        ride_id=ride_request.ride_id,
        passenger_id=ride_request.passenger_id,
        pickup_address=ride_request.pickup_address,
        message=ride_request.message,
        status=ride_request.status,
        passenger=ride_schema.UserSummary(
            id=ride_request.passenger.id,
            name=ride_request.passenger.name,
            email=ride_request.passenger.email,
            phone=(
                ride_request.passenger.phone
                if ride_request.status == models.PassengerStatus.Accepted
                else None
            ),
        ),
    )
