import enum
from datetime import UTC, date, datetime
from typing import Annotated
from uuid import UUID, uuid4

from sqlalchemy import (
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)

# Custom types
id_uuid = Annotated[
    UUID,
    mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4),
]
str100 = Annotated[str, 100]
email_unique = Annotated[str, mapped_column(String(320), unique=True)]
phone_unique = Annotated[str, mapped_column(String(16), unique=True)]
doctor_FK = Annotated[int, mapped_column(ForeignKey("doctors.id"))]


class Role(str, enum.Enum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"
    SUPERADMIN = "SUPERADMIN"


class AppointmentStatus(str, enum.Enum):
    NEW = "NEW"
    CONFIRMED = "CONFIRMED"
    CANCELED = "CANCELED"
    COMPLETED = "COMPLETED"


class SlotStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    BOOKED = "BOOKED"


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    def __repr__(self):
        columns = [
            f"{col}={getattr(self, col)}" for col in self.__table__.columns.keys()
        ]
        return f"<{self.__class__.__name__}({', '.join(columns)})>"


class User(Base):
    first_name: Mapped[str100]
    last_name: Mapped[str100]
    email: Mapped[email_unique]
    hashed_pwd: Mapped[str]
    phone: Mapped[phone_unique]
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.PATIENT)

    doctor: Mapped["Doctor"] = relationship(back_populates="user")
    patient: Mapped["Patient"] = relationship(back_populates="user")


class Doctor(Base):
    __table_args__ = (UniqueConstraint("user_id"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    services: Mapped[list["Service"]] = relationship(
        secondary="doctors_services",
        back_populates="doctors",
        lazy="joined",
    )
    user: Mapped["User"] = relationship(back_populates="doctor")
    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="doctor",
        lazy="joined",
    )
    schedules: Mapped[list["Schedule"]] = relationship(
        back_populates="doctor",
        lazy="joined",
    )


class Patient(Base):
    __table_args__ = (UniqueConstraint("user_id"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="patient")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="patient")


class Service(Base):
    title: Mapped[str] = mapped_column(String(200), unique=True)
    description: Mapped[str | None] = mapped_column(Text())

    doctors: Mapped[list["Doctor"]] = relationship(
        secondary="doctors_services",
        back_populates="services",
    )


class DoctorService(Base):
    __tablename__ = "doctors_services"  # type: ignore
    __table_args__ = (
        UniqueConstraint(
            "doctor_id",
            "service_id",
            name="idx_unique_doctors_services",
        ),
    )

    doctor_id: Mapped[doctor_FK]
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))


class Appointment(Base):
    doctor_id: Mapped[doctor_FK]
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    date: Mapped[date]
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    service: Mapped[int] = mapped_column(ForeignKey("services.id"))
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus),
        default=AppointmentStatus.NEW,
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
    )

    doctor: Mapped["Doctor"] = relationship(back_populates="appointments")
    patient: Mapped["Patient"] = relationship(back_populates="appointments")


class Schedule(Base):
    __table_args__ = (UniqueConstraint("doctor_id", "date"),)

    doctor_id: Mapped[doctor_FK]
    date: Mapped[date]
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    is_available: Mapped[bool] = mapped_column(default=True)

    doctor: Mapped["Doctor"] = relationship(back_populates="schedules")
