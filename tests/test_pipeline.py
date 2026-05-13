import asyncio

from media_catalog_etl.config import AppConfig
from media_catalog_etl.pipeline import run_demo_pipeline
from media_catalog_etl.storage import CatalogStorage


def test_run_demo_pipeline_creates_database_and_titles(tmp_path) -> None:
    async def run_test() -> None:
        database_path = tmp_path / "catalog.sqlite3"
        config = AppConfig(database_path=database_path)

        result = await run_demo_pipeline(config)
        storage = CatalogStorage(database_path)

        assert database_path.exists()
        assert result.parsed_titles == 2
        assert result.inserted_or_updated_titles == 2
        assert await storage.count_titles() == 2
        assert [
            summary["title"] for summary in await storage.get_title_summary()
        ] == ["Example Movie", "Sample Series"]

    asyncio.run(run_test())
