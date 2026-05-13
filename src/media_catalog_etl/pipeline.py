"""Demo pipeline orchestration."""

from dataclasses import dataclass
from pathlib import Path

import aiohttp

from media_catalog_etl.config import AppConfig
from media_catalog_etl.parser import parse_list_page, parse_title_page
from media_catalog_etl.storage import CatalogStorage


@dataclass(slots=True)
class PipelineResult:
    parsed_titles: int
    inserted_or_updated_titles: int
    database_path: Path


def _examples_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "examples"


def _read_example_fixture(name: str) -> str:
    return (_examples_dir() / name).read_text(encoding="utf-8")


async def fetch_html(
    url: str,
    *,
    timeout_seconds: int = 15,
    retry_attempts: int = 3,
) -> str:
    """Fetch HTML from a generic URL.

    The demo pipeline does not call this by default; local fixtures are used for
    public-safe execution.
    """
    timeout = aiohttp.ClientTimeout(total=timeout_seconds)
    headers = {"User-Agent": "MediaCatalogETLDemo/1.0 (+https://example.com)"}
    last_error: Exception | None = None

    for _ in range(retry_attempts):
        try:
            async with aiohttp.ClientSession(
                timeout=timeout,
                headers=headers,
            ) as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.text()
        except aiohttp.ClientError as exc:
            last_error = exc

    if last_error is not None:
        raise last_error

    raise ValueError("retry_attempts must be greater than zero")


async def run_demo_pipeline(config: AppConfig) -> PipelineResult:
    """Run the sanitized demo ETL pipeline using local HTML fixtures."""
    storage = CatalogStorage(config.database_path)
    await storage.create_schema()

    list_html = _read_example_fixture("sample_list_page.html")
    source_ids = parse_list_page(list_html)
    fixture_by_source_id = {
        "demo-001": "sample_title_page.html",
        "demo-002": "sample_title_page_2.html",
    }

    inserted_or_updated_titles = 0
    for source_id in source_ids:
        fixture_name = fixture_by_source_id.get(source_id)
        if fixture_name is None:
            raise ValueError(f"No demo fixture configured for source_id: {source_id}")

        title_html = _read_example_fixture(fixture_name)
        item = parse_title_page(title_html, source_id=source_id)
        await storage.upsert_title(item)
        inserted_or_updated_titles += 1

    return PipelineResult(
        parsed_titles=len(source_ids),
        inserted_or_updated_titles=inserted_or_updated_titles,
        database_path=config.database_path,
    )
