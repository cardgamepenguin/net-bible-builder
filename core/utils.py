# ---------------------------------------------------------------------------
# NET Bible (2nd Ed) Builder
# Copyright (C) 2026 The net-bible-builder Authors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# ---------------------------------------------------------------------------

from pathlib import Path
from .config import CACHE_DIR, ERROR_LOG_PATH

def log_error(msg: str):
    """Appends a message to the error log file."""
    try:
        with ERROR_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception as e:
        print(f"Failed to write to log file: {e}")

def chapter_cache_path(book: str, chapter: int) -> Path:
    """Generates the cache path for a given book and chapter."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    safe_book_name = book.replace(" ", "_").lower()
    return CACHE_DIR / f"{safe_book_name}_{chapter}.html"