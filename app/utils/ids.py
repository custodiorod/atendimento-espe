"""ID generation utilities."""

import secrets
import uuid
from datetime import datetime


def generate_trace_id() -> str:
    """
    Generate a unique trace ID for request tracking.

    Returns:
        Trace ID in format "trace_XXXXXXXX"
    """
    random_bytes = secrets.token_bytes(4)
    return f"trace_{random_bytes.hex()}"


def generate_conversation_id() -> str:
    """
    Generate a unique conversation ID.

    Returns:
        Conversation ID (UUID4)
    """
    return str(uuid.uuid4())


def generate_message_id() -> str:
    """
    Generate a unique message ID.

    Returns:
        Message ID (UUID4)
    """
    return str(uuid.uuid4())


def generate_short_code(length: int = 8) -> str:
    """
    Generate a short alphanumeric code.

    Args:
        length: Length of code (default: 8)

    Returns:
        Short code
    """
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_api_key() -> str:
    """
    Generate a secure API key.

    Returns:
        API key in format "clin_<...>"
    """
    random_bytes = secrets.token_bytes(32)
    return f"clin_{random_bytes.hex()}"


def generate_webhook_secret() -> str:
    """
    Generate a webhook signature secret.

    Returns:
        Webhook secret
    """
    return secrets.token_urlsafe(32)


def generate_event_id() -> str:
    """
    Generate an event ID for logging/auditing.

    Returns:
        Event ID with timestamp prefix
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_part = secrets.token_hex(4)
    return f"evt_{timestamp}_{random_part}"


def is_valid_uuid(uuid_str: str) -> bool:
    """
    Check if string is a valid UUID.

    Args:
        uuid_str: String to validate

    Returns:
        True if valid UUID
    """
    try:
        uuid.UUID(uuid_str)
        return True
    except ValueError:
        return False


def generate_correlation_id() -> str:
    """
    Generate a correlation ID for linking related operations.

    Returns:
        Correlation ID
    """
    return f"corr_{uuid.uuid4().hex[:16]}"
