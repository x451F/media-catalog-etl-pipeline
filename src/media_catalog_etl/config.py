"""Application configuration."""

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    database_path: Path
    base_url: str | None = None
    concurrency: int = 4
    timeout_seconds: int = 15
    retry_attempts: int = 3
    use_demo_fixtures: bool = True


def _read_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default

    try:
        parsed = int(value)
    except ValueError:
        return default

    return parsed if parsed > 0 else default


def load_config() -> AppConfig:
    """Load configuration from environment variables with safe defaults."""
    database_path = Path(os.getenv("CATALOG_DB_PATH", "./catalog.sqlite3"))
    base_url = os.getenv("CATALOG_BASE_URL") or None

    return AppConfig(
        database_path=database_path,
        base_url=base_url,
        concurrency=_read_int("CATALOG_CONCURRENCY", 4),
        timeout_seconds=_read_int("CATALOG_TIMEOUT_SECONDS", 15),
        retry_attempts=_read_int("CATALOG_RETRY_ATTEMPTS", 3),
    )
