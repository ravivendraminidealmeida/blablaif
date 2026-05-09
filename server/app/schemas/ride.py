from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.models import PassengerStatus, RideDirection, RideStatus

CAMPUS_NAME = "IFSP Campus Votuporanga"


class RideCreate(BaseModel):
    direction: RideDirection
    origin: str = Field(min_length=1)
    destination: str = Field(min_length=1)
    departure_time: datetime
    available_seats: int = Field(ge=1, le=8)
    price_per_seat: Decimal = Field(ge=0)
    allow_custom_pickup: bool = False
    fixed_gathering_point: Optional[str] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_pickup_mode(self):
        if not self.allow_custom_pickup and not self.fixed_gathering_point:
            raise ValueError("fixed_gathering_point is required when custom pickup is disabled")
        return self


class RideRequestCreate(BaseModel):
    pickup_address: str = Field(min_length=1)
    message: Optional[str] = None


class UserSummary(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None


class RideSummary(BaseModel):
    id: int
    direction: RideDirection
    origin: str
    destination: str
    departure_time: datetime
    price_per_seat: Decimal
    rider_name: str


class RideRequestResponse(BaseModel):
    id: int
    ride_id: int
    passenger_id: int
    pickup_address: str
    message: Optional[str] = None
    status: PassengerStatus
    passenger: Optional[UserSummary] = None
    ride: Optional[RideSummary] = None
    driver_phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RideResponse(BaseModel):
    id: int
    rider_id: int
    direction: RideDirection
    origin: str
    destination: str
    departure_time: datetime
    price_per_seat: Decimal
    available_seats: int
    accepted_seats: int = 0
    allow_custom_pickup: bool
    fixed_gathering_point: Optional[str] = None
    notes: Optional[str] = None
    status: RideStatus
    rider_name: str
    rider_phone: Optional[str] = None
    current_user_request_status: Optional[PassengerStatus] = None
    requests: list[RideRequestResponse] = []

    model_config = ConfigDict(from_attributes=True)
