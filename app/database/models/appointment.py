"""Appointment model for scheduled consultations."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class AppointmentStatus(str, Enum):
    """Appointment status."""

    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    PENDINGConfirmation = "pending_confirmation"


class AppointmentBase(BaseModel):
    """Base appointment model."""

    contact_id: UUID
    doctor_id: UUID
    scheduled_at: datetime
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    is_future: bool = True
    was_realized: bool = False
    created_by: str = "ai"


class AppointmentCreate(AppointmentBase):
    """Model for creating a new appointment."""

    doctoralia_appointment_id: Optional[str] = None


class AppointmentUpdate(BaseModel):
    """Model for updating an appointment."""

    status: Optional[AppointmentStatus] = None
    is_future: Optional[bool] = None
    was_realized: Optional[bool] = None
    realized_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    no_show: Optional[bool] = None
    last_synced_at: Optional[datetime] = None


class Appointment(AppointmentBase):
    """Complete appointment model from database."""

    id: UUID
    doctoralia_appointment_id: Optional[str] = None
    realized_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    no_show: bool = False
    last_synced_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    @field_validator("scheduled_at")
    @classmethod
    def validate_scheduled_at(cls, v: datetime) -> datetime:
        """Validate that appointment is in future or past appropriately."""
        # Validation can be added based on business rules
        return v

    @property
    def is_pending(self) -> bool:
        """Check if appointment is pending (scheduled or confirmed)."""
        return self.status in (AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED)

    @property
    def is_cancelled(self) -> bool:
        """Check if appointment was cancelled."""
        return self.status == AppointmentStatus.CANCELLED

    @property
    def is_completed(self) -> bool:
        """Check if appointment was completed."""
        return self.status == AppointmentStatus.COMPLETEDED or self.was_realized

    @property
    def is_no_show(self) -> bool:
        """Check if patient didn't show up."""
        return self.no_show or self.status == AppointmentStatus.NO_SHOW

    @property
    def can_be_cancelled(self) -> bool:
        """Check if appointment can still be cancelled."""
        if self.is_cancelled or self.is_completed or self.is_no_show:
            return False
        return self.scheduled_at > datetime.now()

    @property
    def needs_confirmation(self) -> bool:
        """Check if appointment needs confirmation."""
        return self.status == AppointmentStatus.SCHEDULED


class AppointmentWithDoctor(Appointment):
    """Appointment with doctor information."""

    doctor_name: Optional[str] = None
    doctor_specialty: Optional[str] = None
    doctor_display_name: Optional[str] = None
