"""Small parsing and normalization helpers."""

import re


def normalize_text(value: str | None) -> str | None:
    """Collapse whitespace and return None for empty text."""
    if value is None:
        return None

    normalized = " ".join(value.split())
    return normalized or None


def parse_int(value: str | None) -> int | None:
    """Parse the first integer from a string."""
    normalized = normalize_text(value)
    if normalized is None:
        return None

    match = re.search(r"\d+", normalized)
    if match is None:
        return None

    return int(match.group(0))


def parse_release_year(value: str | None) -> int | None:
    """Parse a four-digit release year from text."""
    normalized = normalize_text(value)
    if normalized is None:
        return None

    match = re.search(r"\b(19|20)\d{2}\b", normalized)
    if match is None:
        return None

    return int(match.group(0))


def parse_duration_minutes(value: str | None) -> int | None:
    """Parse duration text such as '102 min', '1h 42m', '2h', or '45m'."""
    normalized = normalize_text(value)
    if normalized is None:
        return None

    hours_match = re.search(r"(\d+)\s*h", normalized, flags=re.IGNORECASE)
    minutes_match = re.search(r"(\d+)\s*(?:m|min)\b", normalized, flags=re.IGNORECASE)

    if hours_match or minutes_match:
        hours = int(hours_match.group(1)) if hours_match else 0
        minutes = int(minutes_match.group(1)) if minutes_match else 0
        return hours * 60 + minutes

    return parse_int(normalized)
