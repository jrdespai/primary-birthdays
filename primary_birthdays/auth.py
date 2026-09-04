"""Authentication wrapper for lcr-api-2."""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from dotenv import load_dotenv

from primary_birthdays.selenium_fix import apply_lcr_selenium_fix

apply_lcr_selenium_fix()

from lcr import API as LcrApi  # noqa: E402


class LcrConfigError(Exception):
    """Missing or invalid LCR configuration."""


def load_config() -> tuple[str, str, int]:
    load_dotenv()
    username = os.environ.get("LCR_USERNAME", "").strip()
    password = os.environ.get("LCR_PASSWORD", "").strip()
    unit_raw = os.environ.get("LCR_UNIT", "").strip()

    if not username or not password or not unit_raw:
        raise LcrConfigError(
            "Set LCR_USERNAME, LCR_PASSWORD, and LCR_UNIT in .env "
            "(copy from .env.example)."
        )

    try:
        unit_number = int(unit_raw)
    except ValueError as exc:
        raise LcrConfigError(f"LCR_UNIT must be a numeric ward unit number, got: {unit_raw!r}") from exc

    return username, password, unit_number


@contextmanager
def lcr_session() -> Iterator[LcrApi]:
    username, password, unit_number = load_config()
    api = LcrApi(username, password, unit_number)
    try:
        yield api
    finally:
        api.close()
