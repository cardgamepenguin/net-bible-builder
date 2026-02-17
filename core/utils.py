from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)
LOG_FILE = BASE_DIR / "errors.log"
BUILD_DIR = BASE_DIR / "build"
BUILD_DIR.mkdir(exist_ok=True)


def log_error(msg: str):
    timestamp = datetime.now().isoformat(timespec="seconds")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")


def chapter_cache_path(book: str, chapter: int) -> Path:
    safe = book.replace(" ", "_").lower()
    return CACHE_DIR / f"{safe}_{chapter}.html"


def chapter_xhtml_path(book: str, chapter: int) -> Path:
    safe = book.replace(" ", "_").lower()
    return BUILD_DIR / f"{safe}_{chapter}.xhtml"

