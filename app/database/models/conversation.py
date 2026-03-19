"""Conversation model representing a chat session."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Owner(str, Enum):
    """Conversation owner (who is responding)."""

    AI = "ai"
    HUMAN = "human"


class ConversationMode(str, Enum):
    """Conversation mode/purpose."""

    SDR = "sdr"
    SUPPORT = "support"
    FINANCE = "finance"
    POST_CONSULTA = "post_consulta"


class ConversationStatus(str, Enum):
    """Conversation status."""

    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


class ConversationBase(BaseModel):
    """Base conversation model."""

    contact_id: UUID
    owner: Owner = Owner.AI
    mode: Optional[ConversationMode] = None
    status: ConversationStatus = ConversationStatus.ACTIVE
    paused_until: Optional[datetime] = None
    last_intent: Optional[str] = None
    last_stage: Optional[str] = None


class ConversationCreate(ConversationBase):
    """Model for creating a new conversation."""

    pass


class ConversationUpdate(BaseModel):
    """Model for updating a conversation."""

    owner: Optional[Owner] = None
    mode: Optional[ConversationMode] = None
    status: Optional[ConversationStatus] = None
    paused_until: Optional[datetime] = None
    last_intent: Optional[str] = None
    last_stage: Optional[str] = None
    last_response_at: Optional[datetime] = None


class Conversation(ConversationBase):
    """Complete conversation model from database."""

    id: UUID
    last_message_at: Optional[datetime] = None
    last_response_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    @property
    def is_active(self) -> bool:
        """Check if conversation is active."""
        if self.status != ConversationStatus.ACTIVE:
            return False

        if self.paused_until:
            return datetime.now() > self.paused_until

        return True

    @property
    def is_paused(self) -> bool:
        """Check if conversation is paused."""
        if self.paused_until is None:
            return False
        return datetime.now() < self.paused_until

    @property
    def is_owned_by_ai(self) -> bool:
        """Check if conversation is owned by AI."""
        return self.owner == Owner.AI

    @property
    def requires_human(self) -> bool:
        """Check if conversation requires human intervention."""
        return self.owner == Owner.HUMAN or not self.is_active
