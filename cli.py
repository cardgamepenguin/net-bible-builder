# ---------------------------------------------------------------------------
# NET Bible (2nd Ed) Builder
# Copyright (C) 2026 The net-bible-builder Authors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# ---------------------------------------------------------------------------

import argparse
from tqdm import tqdm

from core.builder import build_epub
from core.validate import validate_epub
from core.config import DEFAULT_OUTPUT, BOOKS_DATA, OLD_TESTAMENT_BOOKS, NEW_TESTAMENT_BOOKS


def create_cli_progress_handler():
    """Creates a closure for handling progress updates with tqdm bars."""
    progress_bars = {}

    def handler(stage: str, current: int, total: int):
        if stage not in progress_bars:
            unit = "ch" if "Fetching" in stage else "book"
            progress_bars[stage] = tqdm(total=total, desc=stage, unit=unit, ncols=80)

        bar = progress_bars[stage]
        bar.n = current
        bar.refresh()

    return handler


def main():
    parser = argparse.ArgumentParser(
        description="Build NET Bible EPUB from labs.bible.org"
    )

    parser.add_argument(
        "-o", "--output",
        default=DEFAULT_OUTPUT,
        help="Output EPUB file path"
    )
    parser.add_argument(
        "--skip-cache",
        action="store_true",
        help="Ignore cached chapters and refetch everything"
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        dest="skip_cache",
        help="Alias for --skip-cache (for clarity)",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=8,
        help="Maximum parallel fetch workers"
    )
    parser.add_argument(
        "--max-rps",
        type=float,
        default=2.0,
        help="Maximum requests per second (rate limiting)"
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Do not use resume behavior (still uses cache, but semantics flag)"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run epubcheck after building"
    )
    parser.add_argument(
        "--books",
        type=str,
        help="Comma-separated list of books to include (e.g., 'Genesis,Exodus,John')."
    )
    parser.add_argument(
        "--only-ot",
        action="store_true",
        help="Include only Old Testament books."
    )
    parser.add_argument(
        "--only-nt",
        action="store_true",
        help="Include only New Testament books."
    )

    args = parser.parse_args()

    resume = not args.no_resume

    # --- Determine which books to build ---
    books_to_build = None  # Default to all books
    if args.only_ot:
        print("Selecting Old Testament books...")
        books_to_build = [book for book in BOOKS_DATA if book[0] in OLD_TESTAMENT_BOOKS]
    elif args.only_nt:
        print("Selecting New Testament books...")
        books_to_build = [book for book in BOOKS_DATA if book[0] in NEW_TESTAMENT_BOOKS]
    elif args.books:
        print(f"Selecting custom books: {args.books}")
        books_to_build = []
        all_book_map = {book[0].lower(): book for book in BOOKS_DATA}
        requested_books = [b.strip().lower() for b in args.books.split(',')]

        for req_book in requested_books:
            if req_book in all_book_map:
                books_to_build.append(all_book_map[req_book])
            else:
                print(f"Warning: Book '{req_book}' not found and will be skipped.")
    if books_to_build is not None and not books_to_build:
        print("Error: No valid books selected. Aborting.")
        return

    progress_handler = create_cli_progress_handler()

    build_epub(
        output_path=args.output,
        skip_cache=args.skip_cache,
        retries=3,
        max_workers=args.max_workers,
        max_rps=args.max_rps,
        resume=resume,
        progress_callback=progress_handler,
        books_to_build=books_to_build,
    )

    if args.validate:
        print("Validating EPUB...")
        validate_epub(args.output)
    print(f"\nDone. Wrote {args.output}")


if __name__ == "__main__":
    main()
