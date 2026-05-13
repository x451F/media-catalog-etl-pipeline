"""SQLite storage for normalized catalog records."""

from pathlib import Path
from typing import Any

import aiosqlite

from media_catalog_etl.models import TitleItem
from media_catalog_etl.utils import normalize_text


class CatalogStorage:
    def __init__(self, database_path: Path):
        self.database_path = database_path

    async def create_schema(self) -> None:
        """Create the normalized catalog schema if it does not already exist."""
        async with aiosqlite.connect(self.database_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            await db.executescript(
                """
                CREATE TABLE IF NOT EXISTS titles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    original_title TEXT,
                    description TEXT,
                    release_year INTEGER,
                    duration_minutes INTEGER,
                    age_rating TEXT,
                    poster_url TEXT,
                    trailer_url TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS genres (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                );

                CREATE TABLE IF NOT EXISTS countries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                );

                CREATE TABLE IF NOT EXISTS persons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                );

                CREATE TABLE IF NOT EXISTS collections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                );

                CREATE TABLE IF NOT EXISTS title_genres (
                    title_id INTEGER NOT NULL,
                    genre_id INTEGER NOT NULL,
                    UNIQUE(title_id, genre_id),
                    FOREIGN KEY(title_id) REFERENCES titles(id) ON DELETE CASCADE,
                    FOREIGN KEY(genre_id) REFERENCES genres(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS title_countries (
                    title_id INTEGER NOT NULL,
                    country_id INTEGER NOT NULL,
                    UNIQUE(title_id, country_id),
                    FOREIGN KEY(title_id) REFERENCES titles(id) ON DELETE CASCADE,
                    FOREIGN KEY(country_id) REFERENCES countries(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS title_persons (
                    title_id INTEGER NOT NULL,
                    person_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    UNIQUE(title_id, person_id, role),
                    FOREIGN KEY(title_id) REFERENCES titles(id) ON DELETE CASCADE,
                    FOREIGN KEY(person_id) REFERENCES persons(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS title_collections (
                    title_id INTEGER NOT NULL,
                    collection_id INTEGER NOT NULL,
                    UNIQUE(title_id, collection_id),
                    FOREIGN KEY(title_id) REFERENCES titles(id) ON DELETE CASCADE,
                    FOREIGN KEY(collection_id)
                        REFERENCES collections(id) ON DELETE CASCADE
                );
                """
            )
            await db.commit()

    async def upsert_title(self, item: TitleItem) -> int:
        """Insert or update a title and its normalized lookup links."""
        async with aiosqlite.connect(self.database_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            await db.execute("BEGIN")

            try:
                await db.execute(
                    """
                    INSERT INTO titles (
                        source_id,
                        title,
                        original_title,
                        description,
                        release_year,
                        duration_minutes,
                        age_rating,
                        poster_url,
                        trailer_url
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(source_id) DO UPDATE SET
                        title = excluded.title,
                        original_title = excluded.original_title,
                        description = excluded.description,
                        release_year = excluded.release_year,
                        duration_minutes = excluded.duration_minutes,
                        age_rating = excluded.age_rating,
                        poster_url = excluded.poster_url,
                        trailer_url = excluded.trailer_url,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (
                        item.source_id,
                        item.title,
                        item.original_title,
                        item.description,
                        item.release_year,
                        item.duration_minutes,
                        item.age_rating,
                        item.poster_url,
                        item.trailer_url,
                    ),
                )
                cursor = await db.execute(
                    "SELECT id FROM titles WHERE source_id = ?",
                    (item.source_id,),
                )
                row = await cursor.fetchone()
                if row is None:
                    raise RuntimeError("Unable to read title after upsert.")

                title_id = int(row[0])
                await self._link_title_values(
                    db, title_id, "genres", "title_genres", "genre_id", item.genres
                )
                await self._link_title_values(
                    db,
                    title_id,
                    "countries",
                    "title_countries",
                    "country_id",
                    item.countries,
                )
                await self._link_title_values(
                    db,
                    title_id,
                    "collections",
                    "title_collections",
                    "collection_id",
                    item.collections,
                )

                for actor in item.actors:
                    await self._link_person(db, title_id, actor, "actor")
                for director in item.directors:
                    await self._link_person(db, title_id, director, "director")

                await db.commit()
                return title_id
            except Exception:
                await db.rollback()
                raise

    async def count_titles(self) -> int:
        return await self._count_table("titles")

    async def count_persons(self) -> int:
        return await self._count_table("persons")

    async def count_genres(self) -> int:
        return await self._count_table("genres")

    async def get_title_summary(self) -> list[dict[str, Any]]:
        """Return compact title summaries with linked lookup values."""
        async with aiosqlite.connect(self.database_path) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA foreign_keys = ON")
            cursor = await db.execute(
                """
                SELECT
                    id,
                    source_id,
                    title,
                    release_year,
                    duration_minutes
                FROM titles
                ORDER BY source_id
                """
            )
            rows = await cursor.fetchall()

            summaries: list[dict[str, Any]] = []
            for row in rows:
                title_id = int(row["id"])
                summaries.append(
                    {
                        "source_id": row["source_id"],
                        "title": row["title"],
                        "release_year": row["release_year"],
                        "duration_minutes": row["duration_minutes"],
                        "genres": await self._linked_names(
                            db,
                            "genres",
                            "title_genres",
                            "genre_id",
                            title_id,
                        ),
                        "countries": await self._linked_names(
                            db,
                            "countries",
                            "title_countries",
                            "country_id",
                            title_id,
                        ),
                        "actors": await self._linked_person_names(
                            db, title_id, "actor"
                        ),
                        "directors": await self._linked_person_names(
                            db, title_id, "director"
                        ),
                        "collections": await self._linked_names(
                            db,
                            "collections",
                            "title_collections",
                            "collection_id",
                            title_id,
                        ),
                    }
                )

            return summaries

    async def _count_table(self, table: str) -> int:
        async with aiosqlite.connect(self.database_path) as db:
            cursor = await db.execute(f"SELECT COUNT(*) FROM {table}")
            row = await cursor.fetchone()
            return int(row[0]) if row else 0

    async def _upsert_lookup(
        self, db: aiosqlite.Connection, table: str, name: str
    ) -> int:
        await db.execute(f"INSERT OR IGNORE INTO {table} (name) VALUES (?)", (name,))
        cursor = await db.execute(f"SELECT id FROM {table} WHERE name = ?", (name,))
        row = await cursor.fetchone()
        if row is None:
            raise RuntimeError(f"Unable to read lookup value from {table}.")

        return int(row[0])

    async def _link_title_to_lookup(
        self,
        db: aiosqlite.Connection,
        title_id: int,
        link_table: str,
        lookup_column: str,
        lookup_id: int,
    ) -> None:
        await db.execute(
            f"""
            INSERT OR IGNORE INTO {link_table} (title_id, {lookup_column})
            VALUES (?, ?)
            """,
            (title_id, lookup_id),
        )

    async def _link_title_values(
        self,
        db: aiosqlite.Connection,
        title_id: int,
        lookup_table: str,
        link_table: str,
        lookup_column: str,
        values: list[str],
    ) -> None:
        for value in values:
            name = normalize_text(value)
            if name is None:
                continue

            lookup_id = await self._upsert_lookup(db, lookup_table, name)
            await self._link_title_to_lookup(
                db, title_id, link_table, lookup_column, lookup_id
            )

    async def _link_person(
        self,
        db: aiosqlite.Connection,
        title_id: int,
        name: str,
        role: str,
    ) -> None:
        person_name = normalize_text(name)
        role_name = normalize_text(role)
        if person_name is None or role_name is None:
            return

        person_id = await self._upsert_lookup(db, "persons", person_name)
        await db.execute(
            """
            INSERT OR IGNORE INTO title_persons (title_id, person_id, role)
            VALUES (?, ?, ?)
            """,
            (title_id, person_id, role_name),
        )

    async def _linked_names(
        self,
        db: aiosqlite.Connection,
        lookup_table: str,
        link_table: str,
        lookup_column: str,
        title_id: int,
    ) -> list[str]:
        cursor = await db.execute(
            f"""
            SELECT lookup.name
            FROM {lookup_table} AS lookup
            JOIN {link_table} AS link ON link.{lookup_column} = lookup.id
            WHERE link.title_id = ?
            ORDER BY lookup.name
            """,
            (title_id,),
        )
        rows = await cursor.fetchall()
        return [str(row["name"]) for row in rows]

    async def _linked_person_names(
        self, db: aiosqlite.Connection, title_id: int, role: str
    ) -> list[str]:
        cursor = await db.execute(
            """
            SELECT persons.name
            FROM persons
            JOIN title_persons ON title_persons.person_id = persons.id
            WHERE title_persons.title_id = ? AND title_persons.role = ?
            ORDER BY persons.name
            """,
            (title_id, role),
        )
        rows = await cursor.fetchall()
        return [str(row["name"]) for row in rows]
