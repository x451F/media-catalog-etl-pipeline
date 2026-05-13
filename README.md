# Media Catalog ETL Pipeline

A minimal Python ETL demo for parsing media catalog pages from local HTML fixtures,
normalizing metadata, and preparing it for storage.

This repository contains a sanitized demo version. It does not include private
target website configuration, production URLs, collected datasets, or copyrighted
data dumps.

## Status

Initial public project scaffold with configuration, models, utilities, examples,
and tests.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```bash
python -m media_catalog_etl.cli run-demo
python -m media_catalog_etl.cli inspect-db
pytest
ruff check .
```

## Demo fixtures

This project uses sanitized local HTML fixtures from the `examples/` directory.
They are fictional and do not represent any real website or collected dataset.

## Database schema

The demo uses SQLite for portability. Catalog titles are stored in a normalized
schema with lookup tables for genres, countries, persons, and collections.
Many-to-many relation tables link titles to those lookup records, and title
upserts avoid duplicate titles or duplicate relation rows.

## Example output

```text
Initialized database: catalog.sqlite3
Parsed 2 demo titles
Inserted/updated 2 titles
Linked genres, countries, persons, and collections
Done.
```
