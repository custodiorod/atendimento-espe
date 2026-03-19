"""Database models for Clinic AI."""

from app.database.models.contact import Contact, ContactCreate, ContactUpdate
from app.database.models.conversation import (
    Conversation,
    ConversationCreate,
    ConversationUpdate,
    Owner,
    ConversationMode,
    ConversationStatus,
)
from app.database.models.message import (
    Message,
    MessageCreate,
    MessageDirection,
    MessageType,
)
from app.database.models.appointment import (
    Appointment,
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentStatus,
)
from app.database.models.payment import (
    Payment,
    PaymentCreate,
    PaymentUpdate,
    PaymentStatus,
    PaymentProvider,
)

__all__ = [
    # Contact
    "Contact",
    "ContactCreate",
    "ContactUpdate",
    # Conversation
    "Conversation",
    "ConversationCreate",
    "ConversationUpdate",
    "Owner",
    "ConversationMode",
    "ConversationStatus",
    # Message
    "Message",
    "MessageCreate",
    "MessageDirection",
    "MessageType",
    # Appointment
    "Appointment",
    "AppointmentCreate",
    "AppointmentUpdate",
    "AppointmentStatus",
    # Payment
    "Payment",
    "PaymentCreate",
    "PaymentUpdate",
    "PaymentStatus",
    "PaymentProvider",
]
