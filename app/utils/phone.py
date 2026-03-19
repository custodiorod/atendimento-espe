"""Phone number utilities for Brazilian phone numbers."""

import re
from typing import Optional


# Brazilian phone number patterns
PHONE_PATTERNS = [
    r"^(\+?55)?(\d{2})(\d{8,9})$",  # +55 (11) 98765-4321
    r"^(\+?55)?(\d{2})[ -]?(\d{4,5})[ -]?(\d{4})$",  # +55 11 98765-4321
    r"^(\d{2})(\d{8,9})$",  # 11987654321
    r"^(\d{2})[ -]?(\d{4,5})[ -]?(\d{4})$",  # 11 98765-4321
]


def normalize_phone(phone: str) -> Optional[str]:
    """
    Normalize phone number to E.164 format.

    Args:
        phone: Phone number in various formats

    Returns:
        Phone number in E.164 format (+55XXXXXXXXXXX) or None if invalid

    Examples:
        >>> normalize_phone("(11) 98765-4321")
        "+5511987654321"
        >>> normalize_phone("11987654321")
        "+5511987654321"
        >>> normalize_phone("+55 11 98765-4321")
        "+5511987654321"
    """
    if not phone:
        return None

    # Remove all non-numeric characters
    cleaned = re.sub(r"[^\d+]", "", phone)

    # Remove leading +55 if already present
    if cleaned.startswith("+55"):
        return cleaned
    if cleaned.startswith("55") and len(cleaned) == 13:
        return "+" + cleaned

    # Add country code if missing
    if len(cleaned) == 11:  # 11 digits (2 DDD + 9 number)
        return "+55" + cleaned
    if len(cleaned) == 10:  # 10 digits (2 DDD + 8 number)
        return "+55" + cleaned

    # Try to match against patterns
    for pattern in PHONE_PATTERNS:
        match = re.match(pattern, phone)
        if match:
            # Extract DDD and number
            groups = [g for g in match.groups() if g is not None and g.strip()]
            if len(groups) == 2:
                ddd, number = groups
                return f"+55{ddd}{number}"
            elif len(groups) == 3 and groups[0] in ("55", "+55", ""):
                country, ddd, number = groups
                if country in ("55", ""):
                    return f"+55{ddd}{number}"

    return None


def is_valid_phone(phone: str) -> bool:
    """
    Check if phone number is valid.

    Args:
        phone: Phone number to validate

    Returns:
        True if phone number is valid
    """
    normalized = normalize_phone(phone)
    if not normalized:
        return False

    # E.164 format for Brazil: +55XXXXXXXXXXX (13 digits)
    return (
        normalized.startswith("+55")
        and len(normalized) == 13
        and normalized[3:5].isdigit()  # DDD
    )


def extract_ddd(phone: str) -> Optional[str]:
    """Extract DDD from phone number."""
    normalized = normalize_phone(phone)
    if normalized and len(normalized) >= 5:
        return normalized[3:5]
    return None


def format_brasil(phone: str) -> Optional[str]:
    """
    Format phone number in Brazilian format.

    Args:
        phone: Phone number in any format

    Returns:
        Formatted phone number like "(11) 98765-4321" or None if invalid

    Examples:
        >>> format_brasil("+5511987654321")
        "(11) 98765-4321"
        >>> format_brasil("11987654321")
        "(11) 98765-4321"
    """
    normalized = normalize_phone(phone)
    if not normalized:
        return None

    ddd = normalized[3:5]
    number = normalized[5:]

    if len(number) == 9:  # Mobile with 9
        return f"({ddd}) {number[:5]}-{number[5:]}"
    elif len(number) == 8:  # Landline or old mobile format
        return f"({ddd}) {number[:4]}-{number[4:]}"

    return None
