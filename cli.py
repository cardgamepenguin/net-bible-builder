import argparse

from core.builder import build_epub
from core.validate import validate_epub
from core.config import DEFAULT_OUTPUT


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
        help="Alias for --skip-cache (for clarity)"
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

    args = parser.parse_args()

    skip_cache = args.skip_cache or args.force_refresh
    resume = not args.no_resume

    build_epub(
        output_path=args.output,
        skip_cache=skip_cache,
        retries=3,
        max_workers=args.max_workers,
        max_rps=args.max_rps,
        resume=resume,
    )

    if args.validate:
        validate_epub(args.output)


if __name__ == "__main__":
    main()

