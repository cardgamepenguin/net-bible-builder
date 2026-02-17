import time
import threading
from concurrent.futures import ThreadPoolExecutor

import requests
from tqdm import tqdm  # <--- CHANGE 1: Add this import

from .config import API_URL, USER_AGENT, BOOKS_DATA
from .utils import chapter_cache_path, log_error


class RateLimiter:
    def __init__(self, max_per_second: float):
        self.interval = 1.0 / max_per_second
        self.lock = threading.Lock()
        self.last_time = 0.0

    def wait(self):
        with self.lock:
            now = time.time()
            wait_for = self.interval - (now - self.last_time)
            if wait_for > 0:
                time.sleep(wait_for)
            self.last_time = time.time()


def fetch_single_chapter(book: str, chapter: int,
                         skip_cache: bool,
                         retries: int,
                         limiter: RateLimiter | None):
    cache_path = chapter_cache_path(book, chapter)

    if cache_path.exists() and not skip_cache:
        return cache_path.read_text(encoding="utf-8")

    params = {"passage": f"{book} {chapter}", "formatting": "para"}
    headers = {"User-Agent": USER_AGENT}

    for attempt in range(1, retries + 1):
        try:
            if limiter:
                limiter.wait()

            resp = requests.get(API_URL, params=params, headers=headers, timeout=10)
            if resp.status_code == 200:
                cache_path.write_text(resp.text, encoding="utf-8")
                return resp.text
            else:
                log_error(f"{book} {chapter}: HTTP {resp.status_code}")
        except Exception as e:
            log_error(f"{book} {chapter}: {e}")

        time.sleep(attempt * 1.5)

    return None


def fetch_all_chapters(skip_cache: bool = False,
                       retries: int = 3,
                       max_workers: int = 8,
                       max_rps: float = 2.0,
                       resume: bool = True):
    """
    Returns dict[(book, chapter)] = text or None.
    If resume=True, we still fetch everything, but cached chapters are reused.
    """
    limiter = RateLimiter(max_rps) if max_rps > 0 else None

    tasks = []
    results = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for book_name, total_chapters in BOOKS_DATA:
            for ch in range(1, total_chapters + 1):
                future = executor.submit(
                    fetch_single_chapter,
                    book_name, ch, skip_cache, retries, limiter
                )
                tasks.append((future, book_name, ch))

        # --- CHANGE 2: Wrap 'tasks' in tqdm for the progress bar ---
        for future, book_name, ch in tqdm(tasks, desc="Fetching chapters", unit="ch"):
            try:
                text = future.result()
                results[(book_name, ch)] = text
            except Exception as e:
                log_error(f"Failed to fetch {book_name} {ch}: {e}")

    return results
