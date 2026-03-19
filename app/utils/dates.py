"""Date and time utilities."""

from datetime import datetime, time, timezone
from typing import Optional

import pytz

# Brazil timezone
BRASILIA_TZ = pytz.timezone("America/Sao_Paulo")


def now_brasil() -> datetime:
    """
    Get current datetime in Brasilia timezone.

    Returns:
        Current datetime with Brasilia timezone
    """
    return datetime.now(BRASILIA_TZ)


def now_utc() -> datetime:
    """
    Get current datetime in UTC.

    Returns:
        Current datetime with UTC timezone
    """
    return datetime.now(timezone.utc)


def to_brasil(dt: datetime) -> datetime:
    """
    Convert datetime to Brasilia timezone.

    Args:
        dt: Datetime to convert

    Returns:
        Datetime in Brasilia timezone
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(BRASILIA_TZ)


def to_utc(dt: datetime) -> datetime:
    """
    Convert datetime to UTC.

    Args:
        dt: Datetime to convert

    Returns:
        Datetime in UTC timezone
    """
    if dt.tzinfo is None:
        dt = BRASILIA_TZ.localize(dt)
    return dt.astimezone(timezone.utc)


def is_business_hours(
    dt: Optional[datetime] = None,
    start: str = "08:00",
    end: str = "18:00",
    weekdays: str = "1,2,3,4,5",
) -> bool:
    """
    Check if datetime is within business hours.

    Args:
        dt: Datetime to check (defaults to now in Brasilia)
        start: Start time in HH:MM format
        end: End time in HH:MM format
        weekdays: Comma-separated weekdays (1=Monday, 7=Sunday)

    Returns:
        True if datetime is within business hours
    """
    if dt is None:
        dt = now_brasil()
    else:
        dt = to_brasil(dt)

    # Check weekday
    valid_weekdays = [int(w.strip()) for w in weekdays.split(",")]
    if dt.weekday() + 1 not in valid_weekdays:
        return False

    # Check time
    start_time = time.fromisoformat(start)
    end_time = time.fromisoformat(end)
    current_time = dt.time()

    return start_time <= current_time <= end_time


def parse_time_range(time_str: str) -> tuple[time, time]:
    """
    Parse time range string like "08:00-18:00".

    Args:
        time_str: Time range string

    Returns:
        Tuple of (start_time, end_time)
    """
    parts = time_str.split("-")
    if len(parts) != 2:
        raise ValueError(f"Invalid time range: {time_str}")

    start = time.fromisoformat(parts[0].strip())
    end = time.fromisoformat(parts[1].strip())

    return start, end


def format_brasil(dt: datetime, format_str: str = "%d/%m/%Y %H:%M") -> str:
    """
    Format datetime in Brazilian format.

    Args:
        dt: Datetime to format
        format_str: Format string (default: "31/12/2024 14:30")

    Returns:
        Formatted datetime string
    """
    dt_brasil = to_brasil(dt)
    return dt_brasil.strftime(format_str)


def add_business_days(
    dt: datetime, days: int, holidays: Optional[list[datetime]] = None
) -> datetime:
    """
    Add business days to datetime, skipping weekends and holidays.

    Args:
        dt: Start datetime
        days: Number of business days to add
        holidays: List of holiday datetimes to skip

    Returns:
        Datetime after adding business days
    """
    dt_brasil = to_brasil(dt)
    holidays = holidays or []

    added_days = 0
    while added_days < days:
        dt_brasil += __import__("datetime").timedelta(days=1)

        # Skip weekends
        if dt_brasil.weekday() >= 5:  # Saturday=5, Sunday=6
            continue

        # Skip holidays
        if any(h.date() == dt_brasil.date() for h in holidays):
            continue

        added_days += 1

    return dt_brasil
