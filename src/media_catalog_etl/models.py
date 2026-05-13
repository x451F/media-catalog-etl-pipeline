"""Domain models for normalized catalog records."""

from dataclasses import dataclass


@dataclass(slots=True)
class TitleItem:
    source_id: str
    title: str
    original_title: str | None
    description: str | None
    release_year: int | None
    duration_minutes: int | None
    age_rating: str | None
    poster_url: str | None
    trailer_url: str | None
    genres: list[str]
    countries: list[str]
    actors: list[str]
    directors: list[str]
    collections: list[str]


@dataclass(slots=True)
class Person:
    source_id: str
    name: str
    role: str | None = None
