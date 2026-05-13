from media_catalog_etl.utils import (
    normalize_text,
    parse_duration_minutes,
    parse_release_year,
)


def test_normalize_text_collapses_whitespace() -> None:
    assert normalize_text("  Example\n  title\t ") == "Example title"


def test_normalize_text_returns_none_for_blank_values() -> None:
    assert normalize_text("   ") is None
    assert normalize_text(None) is None


def test_parse_release_year() -> None:
    assert parse_release_year("Released in 2024") == 2024
    assert parse_release_year("no year") is None


def test_parse_duration_minutes() -> None:
    assert parse_duration_minutes("102 min") == 102
    assert parse_duration_minutes("1h 42m") == 102
    assert parse_duration_minutes("2h") == 120
    assert parse_duration_minutes("45m") == 45
    assert parse_duration_minutes(None) is None
