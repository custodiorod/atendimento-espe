"""Message model representing a single message in a conversation."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MessageDirection(str, Enum):
    """Message direction."""

    INBOUND = "inbound"  # From user
    OUTBOUND = "outbound"  # From system


class MessageType(str, Enum):
    """Message type."""

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    LOCATION = "location"
    CONTACT = "contact"
    SYSTEM = "system"  # Internal system messages


class MessageBase(BaseModel):
    """Base message model."""

    conversation_id: UUID
    contact_id: UUID
    direction: MessageDirection
    message_type: MessageType = MessageType.TEXT
    content: Optional[str] = None
    media_url: Optional[str] = None
    transcribed_text: Optional[str] = None
    trace_id: Optional[str] = None


class MessageCreate(MessageBase):
    """Model for creating a new message."""

    provider_message_id: Optional[str] = None


class MessageUpdate(BaseModel):
    """Model for updating a message."""

    transcribed_text: Optional[str] = None
    content: Optional[str] = None


class Message(MessageBase):
    """Complete message model from database."""

    id: UUID
    provider_message_id: Optional[str] = None
    created_at: datetime

    @property
    def is_inbound(self) -> bool:
        """Check if message is from user."""
        return self.direction == MessageDirection.INBOUND

    @property
    def is_outbound(self) -> bool:
        """Check if message is from system."""
        return self.direction == MessageDirection.OUTBOUND

    @property
    def has_media(self) -> bool:
        """Check if message has media attachment."""
        return self.media_url is not None and self.message_type in (
            MessageType.IMAGE,
            MessageType.AUDIO,
            MessageType.VIDEO,
            MessageType.DOCUMENT,
        )

    @property
    def display_content(self) -> str:
        """Get content for display (use transcribed text if available)."""
        if self.message_type == MessageType.AUDIO and self.transcribed_text:
            return f"[Audio] {self.transcribed_text}"
        if self.message_type == MessageType.IMAGE:
            return "[Imagem]" if not self.content else f"[Imagem] {self.content}"
        if self.message_type == MessageType.VIDEO:
            return "[Vídeo]" if not self.content else f"[Vídeo] {self.content}"
        if self.message_type == MessageType.DOCUMENT:
            return "[Documento]"
        if self.message_type == MessageType.LOCATION:
            return "[Localização]"
        if self.message_type == MessageType.CONTACT:
            return "[Contato]"
        return self.content or ""
