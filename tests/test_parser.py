from pathlib import Path

import pytest

from media_catalog_etl.parser import parse_list_page, parse_title_page

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


def read_example(name: str) -> str:
    return (EXAMPLES_DIR / name).read_text(encoding="utf-8")


def test_parse_list_page_returns_source_ids() -> None:
    html = read_example("sample_list_page.html")

    assert parse_list_page(html) == ["demo-001", "demo-002"]


def test_parse_title_page_returns_normalized_title_item() -> None:
    html = read_example("sample_title_page.html")

    item = parse_title_page(html, source_id="demo-001")

    assert item.title == "Example Movie"
    assert item.release_year == 2024
    assert item.duration_minutes == 102
    assert item.genres == ["Drama", "Adventure"]
    assert item.countries == ["France", "Ukraine"]
    assert item.actors == ["Alex Demo", "Maria Sample"]
    assert item.directors == ["John Example"]
    assert item.collections == ["Demo Collection"]


def test_parse_title_page_raises_value_error_without_title() -> None:
    html = """
    <main>
      <div data-field="description">Missing required title.</div>
    </main>
    """

    with pytest.raises(ValueError, match="missing required title"):
        parse_title_page(html, source_id="demo-missing")
