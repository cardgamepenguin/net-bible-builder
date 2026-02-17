import shutil
import subprocess
from pathlib import Path

from .config import DEFAULT_OUTPUT


def validate_epub(epub_path: str | Path = DEFAULT_OUTPUT):
    epub_path = Path(epub_path)

    if not epub_path.exists():
        print(f"EPUB not found: {epub_path}")
        return False

    if not shutil.which("epubcheck"):
        print("epubcheck not found on PATH. Install it to enable validation.")
        return False

    print(f"Running epubcheck on {epub_path}...")
    result = subprocess.run(
        ["epubcheck", str(epub_path)],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.returncode == 0:
        print("EPUB is valid.")
        return True
    else:
        print("EPUB has issues.")
        print(result.stderr)
        return False

