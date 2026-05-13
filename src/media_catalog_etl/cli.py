"""Command-line interface for the sanitized demo ETL pipeline."""

import argparse
import asyncio
import logging
from pathlib import Path

from media_catalog_etl.config import load_config
from media_catalog_etl.pipeline import run_demo_pipeline
from media_catalog_etl.storage import CatalogStorage

logger = logging.getLogger(__name__)


def _format_path(path: Path) -> str:
    return str(path)


async def _run_demo() -> None:
    config = load_config()
    logger.info("Running demo pipeline with local fixtures")
    result = await run_demo_pipeline(config)

    print(f"Initialized database: {_format_path(result.database_path)}")
    print(f"Parsed {result.parsed_titles} demo titles")
    print(f"Inserted/updated {result.inserted_or_updated_titles} titles")
    print("Linked genres, countries, persons, and collections")
    print("Done.")


async def _init_db() -> None:
    config = load_config()
    storage = CatalogStorage(config.database_path)
    logger.info("Creating database schema")
    await storage.create_schema()

    print(f"Initialized database: {_format_path(config.database_path)}")


async def _inspect_db() -> None:
    config = load_config()
    if not config.database_path.exists():
        print(f"Database not found: {_format_path(config.database_path)}")
        return

    storage = CatalogStorage(config.database_path)
    title_count = await storage.count_titles()
    genre_count = await storage.count_genres()
    person_count = await storage.count_persons()
    summaries = await storage.get_title_summary()

    print(f"Titles: {title_count}")
    print(f"Genres: {genre_count}")
    print(f"Persons: {person_count}")

    if summaries:
        print("Title summaries:")
        for summary in summaries:
            print(
                "- "
                f"{summary['source_id']}: {summary['title']} "
                f"({summary['release_year'] or 'unknown year'})"
            )
            print(f"  Genres: {', '.join(summary['genres']) or '-'}")
            print(f"  Countries: {', '.join(summary['countries']) or '-'}")
            print(f"  Actors: {', '.join(summary['actors']) or '-'}")
            print(f"  Directors: {', '.join(summary['directors']) or '-'}")
            print(f"  Collections: {', '.join(summary['collections']) or '-'}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-catalog-etl",
        description="Run the sanitized media catalog ETL demo.",
    )
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set internal logging level.",
    )

    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("run-demo", help="Run the local fixture ETL demo.")
    subcommands.add_parser("init-db", help="Create the SQLite schema.")
    subcommands.add_parser("inspect-db", help="Print database counts and summaries.")

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the command-line interface."""
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level))

    if args.command == "run-demo":
        asyncio.run(_run_demo())
    elif args.command == "init-db":
        asyncio.run(_init_db())
    elif args.command == "inspect-db":
        asyncio.run(_inspect_db())
    else:
        parser.error(f"Unknown command: {args.command}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
