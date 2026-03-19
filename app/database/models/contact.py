"""Contact model representing a patient/lead."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ContactBase(BaseModel):
    """Base contact model."""

    external_id: Optional[str] = None
    full_name: Optional[str] = None
    phone_e164: str = Field(..., description="Phone number in E.164 format")
    birth_date: Optional[str] = None
    is_existing_patient: bool = False
    consent_status: str = Field(default="unknown", description="unknown, opted_in, opted_out")
    opt_out: bool = False
    source: str = Field(default="whatsapp")
    notes: Optional[str] = None


class ContactCreate(ContactBase):
    """Model for creating a new contact."""

    pass


class ContactUpdate(BaseModel):
    """Model for updating a contact."""

    full_name: Optional[str] = None
    birth_date: Optional[str] = None
    is_existing_patient: Optional[bool] = None
    consent_status: Optional[str] = None
    opt_out: Optional[bool] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    last_seen_at: Optional[datetime] = None


class Contact(ContactBase):
    """Complete contact model from database."""

    id: UUID
    first_seen_at: datetime
    last_seen_at: datetime
    created_at: datetime
    updated_at: datetime

    @field_validator("phone_e164")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format."""
        if not v.startswith("+55"):
            raise ValueError("Phone number must be in E.164 format (+55...)")

        if len(v) != 13:
            raise ValueError("Invalid Brazilian phone number length")

        return v

    @property
    def display_name(self) -> str:
        """Get display name (full name or phone)."""
        return self.full_name or self.phone_e164

    @property
    def can_receive_messages(self) -> bool:
        """Check if contact can receive messages."""
        return not self.opt_out and self.consent_status in ("opted_in", "unknown")


class ContactWithStats(Contact):
    """Contact with additional statistics."""

    total_conversations: int = 0
    total_messages: int = 0
    last_conversation_at: Optional[datetime] = None
    total_appointments: int = 0
    last_appointment_at: Optional[datetime] = None
