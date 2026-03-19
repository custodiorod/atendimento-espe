"""Payment model for processing payments."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PaymentProvider(str, Enum):
    """Payment provider."""

    OPENPIX = "openpix"
    STRIPE = "stripe"


class PaymentStatus(str, Enum):
    """Payment status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentBase(BaseModel):
    """Base payment model."""

    contact_id: UUID
    provider: PaymentProvider
    amount: Decimal = Field(..., ge=0, description="Payment amount in BRL")
    payment_method: Optional[str] = None


class PaymentCreate(PaymentBase):
    """Model for creating a new payment."""

    appointment_id: Optional[UUID] = None
    external_payment_id: Optional[str] = None


class PaymentUpdate(BaseModel):
    """Model for updating a payment."""

    status: Optional[PaymentStatus] = None
    payment_link: Optional[str] = None
    paid_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class Payment(PaymentBase):
    """Complete payment model from database."""

    id: UUID
    appointment_id: Optional[UUID] = None
    external_payment_id: Optional[str] = None
    status: PaymentStatus = PaymentStatus.PENDING
    payment_link: Optional[str] = None
    paid_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    @property
    def is_pending(self) -> bool:
        """Check if payment is pending."""
        return self.status == PaymentStatus.PENDING

    @property
    def is_completed(self) -> bool:
        """Check if payment was completed."""
        return self.status == PaymentStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if payment failed."""
        return self.status == PaymentStatus.FAILED

    @property
    def is_expired(self) -> bool:
        """Check if payment expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at and not self.is_completed

    @property
    def can_be_paid(self) -> bool:
        """Check if payment can still be paid."""
        return self.is_pending and not self.is_expired

    @property
    def amount_in_cents(self) -> int:
        """Get amount in cents (for payment providers)."""
        return int(self.amount * 100)

    @property
    def amount_formatted(self) -> str:
        """Get formatted amount (BRL)."""
        return f"R$ {self.amount:.2f}".replace(".", ",")
