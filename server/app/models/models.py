from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship
import enum
from app.db.database import Base

class RoleType(enum.Enum):
    Student = "Student"
    Professor = "Professor"

class RideStatus(enum.Enum):
    Scheduled = "Scheduled"
    InProgress = "InProgress"
    Completed = "Completed"
    Cancelled = "Cancelled"

class PassengerStatus(enum.Enum):
    Pending = "Pending"
    Accepted = "Accepted"
    Rejected = "Rejected"
    Cancelled = "Cancelled"

class College(Base):
    __tablename__ = "colleges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)

    users = relationship("User", back_populates="college")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    college_id = Column(Integer, ForeignKey("colleges.id"))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    role = Column(Enum(RoleType), default=RoleType.Student)
    password_hash = Column(String, nullable=False)

    college = relationship("College", back_populates="users")
    rides_offered = relationship("Ride", back_populates="rider")
    ride_requests = relationship("RidePassenger", back_populates="passenger")

class Ride(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    rider_id = Column(Integer, ForeignKey("users.id"))
    departure_time = Column(DateTime, nullable=False)
    total_kilometers = Column(Float, nullable=False)
    estimated_price = Column(Numeric, nullable=False)
    available_seats = Column(Integer, default=4)
    allow_custom_pickup = Column(Boolean, default=False)
    fixed_gathering_point = Column(String, nullable=True)
    status = Column(Enum(RideStatus), default=RideStatus.Scheduled)

    rider = relationship("User", back_populates="rides_offered")
    passengers = relationship("RidePassenger", back_populates="ride")

class RidePassenger(Base):
    __tablename__ = "ride_passengers"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"))
    passenger_id = Column(Integer, ForeignKey("users.id"))
    pickup_address = Column(String, nullable=False)
    status = Column(Enum(PassengerStatus), default=PassengerStatus.Pending)

    ride = relationship("Ride", back_populates="passengers")
    passenger = relationship("User", back_populates="ride_requests")
