import os
import time
import requests
from pathlib import Path

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

ERROR_LOG = Path("errors.log")


def log_error(msg):
    with ERROR_LOG.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def cache_path(book, chapter):
    safe = book.replace(" ", "_").lower()
    return CACHE_DIR / f"{safe}_{chapter}.html"


def fetch_chapter(book, chapter, retries=3):
    """Fetch chapter text with caching + retries."""
    cp = cache_path(book, chapter)

    # Cached?
    if cp.exists():
        return cp.read_text(encoding="utf-8")

    url = "https://labs.bible.org/api/"
    params = {"passage": f"{book} {chapter}", "formatting": "para"}
    headers = {"User-Agent": "Mozilla/5.0"}

    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=10)
            if r.status_code == 200:
                cp.write_text(r.text, encoding="utf-8")
                return r.text
            else:
                log_error(f"{book} {chapter}: HTTP {r.status_code}")
        except Exception as e:
            log_error(f"{book} {chapter}: {e}")

        time.sleep(attempt * 1.5)  # exponential backoff

    return None

