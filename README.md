# Media Catalog ETL Pipeline

An async Python ETL pipeline demo that collects catalog-like HTML pages, extracts
structured media metadata, normalizes it, and stores it in SQLite.

## Why this project exists

This project demonstrates how an async Python scraper can be structured as a
small ETL pipeline: collecting HTML, parsing metadata, normalizing entities, and
storing them in a relational SQLite database.

## Highlights

- Async-ready architecture
- HTML parser layer separated from storage
- Sanitized local demo fixtures
- Normalized SQLite schema
- Upsert logic
- Many-to-many relations
- CLI interface
- Tests for parser, utils, and storage

## Architecture

```text
Local demo HTML fixtures
  ↓
Parser layer
  ↓
Normalized dataclasses
  ↓
SQLite storage
  ↓
Catalog database
```

Optional generic fetch path:

```text
Optional HTTP fetcher
  ↓
Parser layer
  ↓
Storage
```

## Project structure

```text
media-catalog-etl/
├── README.md
├── pyproject.toml
├── .gitignore
├── .env.example
├── examples/
│   ├── sample_list_page.html
│   ├── sample_title_page.html
│   ├── sample_title_page_2.html
│   └── sample_person_page.html
├── src/
│   └── media_catalog_etl/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── models.py
│       ├── parser.py
│       ├── pipeline.py
│       ├── storage.py
│       └── utils.py
└── tests/
    ├── test_parser.py
    ├── test_pipeline.py
    ├── test_storage.py
    └── test_utils.py
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

After activating the virtual environment and installing the project in editable
mode, run:

```bash
python -m media_catalog_etl.cli run-demo
python -m media_catalog_etl.cli inspect-db
pytest
ruff check .
```

Without activating the virtual environment, use the venv Python directly:

```bash
.venv/bin/python -m media_catalog_etl.cli run-demo
.venv/bin/python -m media_catalog_etl.cli inspect-db
```

## Example output

```text
Initialized database: catalog.sqlite3
Parsed 2 demo titles
Inserted/updated 2 titles
Linked genres, countries, persons, and collections
Done.
```

After running the demo, inspect the SQLite contents:

```text
Titles: 2
Genres: 3
Persons: 6
Title summaries:
- demo-001: Example Movie (2024)
  Genres: Adventure, Drama
  Countries: France, Ukraine
  Actors: Alex Demo, Maria Sample
  Directors: John Example
  Collections: Demo Collection
- demo-002: Sample Series (2023)
  Genres: Drama, Mystery
  Countries: Canada
  Actors: Sam Fixture, Taylor Demo
  Directors: Jordan Sample
  Collections: Demo Collection
```

## Database schema overview

SQLite is used for demo portability. The schema stores core title metadata in
`titles`, with normalized lookup tables for `genres`, `countries`, `persons`,
and `collections`. Join tables connect titles to those lookup records:
`title_genres`, `title_countries`, `title_persons`, and `title_collections`.

The storage layer upserts titles by `source_id` and uses duplicate-safe inserts
for lookup values and many-to-many relation rows.

## Safety note

This repository contains a sanitized demo version. It does not include private target website configuration, production URLs, collected datasets, or copyrighted data dumps.

## Portfolio note

This project is intended to demonstrate Python ETL structure, async-ready
scraping architecture, parser isolation, data normalization, and SQLite
persistence. Production source configuration and collected data are intentionally
excluded.
