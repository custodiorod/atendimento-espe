"""Validation and sanitization utilities."""

import re
from typing import Optional


# Markdown patterns to sanitize
MARKDOWN_DANGEROUS_PATTERNS = [
    r"<!DOCTYPE[^>]*>",  # HTML DOCTYPE
    r"<script[^>]*>.*?</script>",  # Script tags
    r"<iframe[^>]*>.*?</iframe>",  # Iframe tags
    r"on\\w+\\s*=",  # Event handlers like onclick=
    r"javascript:",  # JavaScript protocol
]

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
CPF_PATTERN = re.compile(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}")
CNPJ_PATTERN = re.compile(r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}")


def sanitize_markdown(text: str, allow_links: bool = True) -> str:
    """
    Sanitize markdown text to prevent XSS attacks.

    Args:
        text: Text to sanitize
        allow_links: Whether to allow markdown links

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    sanitized = text

    # Remove dangerous patterns
    for pattern in MARKDOWN_DANGEROUS_PATTERNS:
        sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE | re.DOTALL)

    # Remove HTML tags that aren't markdown
    sanitized = re.sub(r"<(?!\/?[a-z]+(?:\s[^>]*)?\/?>)[^>]*>", "", sanitized, flags=re.IGNORECASE)

    return sanitized.strip()


def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def extract_email(text: str) -> Optional[str]:
    """
    Extract email address from text.

    Args:
        text: Text to search

    Returns:
        First email found or None
    """
    match = EMAIL_PATTERN.search(text)
    return match.group(0) if match else None


def extract_cpf(text: str) -> Optional[str]:
    """
    Extract CPF from text.

    Args:
        text: Text to search

    Returns:
        First CPF found or None
    """
    match = CPF_PATTERN.search(text)
    return match.group(0) if match else None


def extract_cnpj(text: str) -> Optional[str]:
    """
    Extract CNPJ from text.

    Args:
        text: Text to search

    Returns:
        First CNPJ found or None
    """
    match = CNPJ_PATTERN.search(text)
    return match.group(0) if match else None


def is_valid_email(email: str) -> bool:
    """
    Validate email address.

    Args:
        email: Email to validate

    Returns:
        True if email is valid
    """
    if not email:
        return False
    return bool(EMAIL_PATTERN.fullmatch(email.strip()))


def mask_email(email: str, mask_char: str = "*") -> str:
    """
    Mask email address for privacy.

    Args:
        email: Email to mask
        mask_char: Character to use for masking

    Returns:
        Masked email like "j***@example.com"
    """
    if not is_valid_email(email):
        return email

    local, domain = email.split("@")
    if len(local) > 1:
        masked_local = local[0] + mask_char * (len(local) - 2) + local[-1]
    else:
        masked_local = mask_char * len(local)

    return f"{masked_local}@{domain}"


def mask_phone(phone: str, mask_char: str = "*") -> str:
    """
    Mask phone number for privacy.

    Args:
        phone: Phone to mask (E.164 format preferred)
        mask_char: Character to use for masking

    Returns:
        Masked phone like "+5511****4321"
    """
    if not phone or len(phone) < 4:
        return phone

    # Keep first 4 and last 4 characters
    return phone[:4] + mask_char * (len(phone) - 8) + phone[-4:]


def clean_whitespaces(text: str) -> str:
    """
    Clean excessive whitespaces from text.

    Args:
        text: Text to clean

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Replace multiple spaces with single space
    cleaned = re.sub(r" +", " ", text)
    # Replace multiple newlines with double newline
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    # Remove leading/trailing whitespace from each line
    cleaned = "\n".join(line.strip() for line in cleaned.split("\n"))

    return cleaned.strip()


def detect_language(text: str) -> str:
    """
    Simple language detection (Portuguese vs others).

    Args:
        text: Text to analyze

    Returns:
        Detected language code ("pt", "en", or "unknown")
    """
    if not text:
        return "unknown"

    # Portuguese indicators
    pt_indicators = [
        " é ", " é ", " que ", " para ", " com ", " sem ",
        " não ", " sim ", " ou ", " e ", " mas ",
        "ç", "ã", "õ", "á", "é", "í", "ó", "ú",
    ]

    text_lower = text.lower()
    pt_count = sum(1 for indicator in pt_indicators if indicator in text_lower)

    # If more than 3 Portuguese indicators, assume Portuguese
    if pt_count >= 3:
        return "pt"

    # Check for common English words
    en_indicators = [" is ", " the ", " and ", " or ", " but ", " with ", " for "]
    en_count = sum(1 for indicator in en_indicators if indicator in text_lower)

    if en_count >= 3:
        return "en"

    return "unknown"
