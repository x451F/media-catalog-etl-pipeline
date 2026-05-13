"""Parsers for sanitized demo HTML fixtures."""

from bs4 import BeautifulSoup

from media_catalog_etl.models import Person, TitleItem
from media_catalog_etl.utils import (
    normalize_text,
    parse_duration_minutes,
    parse_release_year,
)


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def get_text_by_field(soup: BeautifulSoup, field: str) -> str | None:
    """Return normalized text for a generic data-field element."""
    element = soup.select_one(f'[data-field="{field}"]')
    if element is None:
        return None

    return normalize_text(element.get_text(" ", strip=True))


def get_attr_by_field(soup: BeautifulSoup, field: str, attr: str) -> str | None:
    """Return a normalized attribute value for a generic data-field element."""
    element = soup.select_one(f'[data-field="{field}"]')
    if element is None:
        return None

    value = element.get(attr)
    if not isinstance(value, str):
        return None

    return normalize_text(value)


def get_list_by_field(soup: BeautifulSoup, field: str) -> list[str]:
    """Return normalized list item text from a generic data-field list."""
    container = soup.select_one(f'[data-field="{field}"]')
    if container is None:
        return []

    values: list[str] = []
    for item in container.select("li"):
        text = normalize_text(item.get_text(" ", strip=True))
        if text is not None:
            values.append(text)

    return values


def parse_list_page(html: str) -> list[str]:
    """Parse source IDs from a sanitized catalog list page."""
    soup = _soup(html)
    source_ids: list[str] = []

    for card in soup.select(".catalog-card[data-source-id]"):
        source_id = card.get("data-source-id")
        if isinstance(source_id, str) and normalize_text(source_id):
            source_ids.append(source_id)

    return source_ids


def parse_title_page(html: str, source_id: str) -> TitleItem:
    """Parse a sanitized title detail page into a normalized TitleItem."""
    soup = _soup(html)
    title = get_text_by_field(soup, "title")
    if title is None:
        raise ValueError("Title page is missing required title field.")

    return TitleItem(
        source_id=source_id,
        title=title,
        original_title=get_text_by_field(soup, "original-title"),
        description=get_text_by_field(soup, "description"),
        release_year=parse_release_year(get_text_by_field(soup, "release-year")),
        duration_minutes=parse_duration_minutes(get_text_by_field(soup, "duration")),
        age_rating=get_text_by_field(soup, "age-rating"),
        poster_url=get_attr_by_field(soup, "poster", "src"),
        trailer_url=get_attr_by_field(soup, "trailer", "href"),
        genres=get_list_by_field(soup, "genres"),
        countries=get_list_by_field(soup, "countries"),
        actors=get_list_by_field(soup, "actors"),
        directors=get_list_by_field(soup, "directors"),
        collections=get_list_by_field(soup, "collections"),
    )


def parse_person_page(html: str) -> Person | None:
    """Parse a sanitized person page, returning None when required data is absent."""
    soup = _soup(html)
    source_element = soup.select_one("[data-source-id]")
    source_id = source_element.get("data-source-id") if source_element else None
    name = get_text_by_field(soup, "name")

    if (
        not isinstance(source_id, str)
        or normalize_text(source_id) is None
        or name is None
    ):
        return None

    return Person(
        source_id=source_id,
        name=name,
        role=get_text_by_field(soup, "role"),
    )
