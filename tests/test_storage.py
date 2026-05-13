import asyncio

from media_catalog_etl.models import TitleItem
from media_catalog_etl.storage import CatalogStorage


def demo_title() -> TitleItem:
    return TitleItem(
        source_id="demo-001",
        title="Example Movie",
        original_title="Original Example Movie",
        description="A fictional demo movie used for storage tests.",
        release_year=2024,
        duration_minutes=102,
        age_rating="16+",
        poster_url="https://example.com/posters/demo-001.webp",
        trailer_url="https://example.com/trailers/demo-001",
        genres=["Drama", "Adventure"],
        countries=["France", "Ukraine"],
        actors=["Alex Demo", "Maria Sample"],
        directors=["John Example"],
        collections=["Demo Collection"],
    )


def test_storage_upserts_title_and_links_without_duplicates(tmp_path) -> None:
    async def run_test() -> None:
        storage = CatalogStorage(tmp_path / "catalog.sqlite3")

        await storage.create_schema()
        first_title_id = await storage.upsert_title(demo_title())
        second_title_id = await storage.upsert_title(demo_title())

        assert first_title_id == second_title_id
        assert await storage.count_titles() == 1
        assert await storage.count_genres() == 2
        assert await storage.count_persons() == 3

        summaries = await storage.get_title_summary()

        assert summaries == [
            {
                "source_id": "demo-001",
                "title": "Example Movie",
                "release_year": 2024,
                "duration_minutes": 102,
                "genres": ["Adventure", "Drama"],
                "countries": ["France", "Ukraine"],
                "actors": ["Alex Demo", "Maria Sample"],
                "directors": ["John Example"],
                "collections": ["Demo Collection"],
            }
        ]

    asyncio.run(run_test())
