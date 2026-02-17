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
from ebooklib import epub
from .config import BOOKS_DATA, DEFAULT_OUTPUT
from .fetcher import fetch_all_chapters

# --- Path to asset files ---
SCRIPT_DIR = Path(__file__).parent
ASSETS_DIR = SCRIPT_DIR.parent / "assets"
COPYRIGHT_FILE = ASSETS_DIR / "copyright.html"
STYLE_FILE = ASSETS_DIR / "style.css"

def make_filename(book: str) -> str:
    # Example: "1 John" -> "1_john.xhtml"
    safe = book.replace(" ", "_").lower()
    return f"{safe}.xhtml"

def build_epub(output_path: str | Path = DEFAULT_OUTPUT,
               skip_cache: bool = False,
               retries: int = 3,
               max_workers: int = 8,
               max_rps: float = 2.0,
               resume: bool = True,
               cover_path: str | None = "cover.png",
               progress_callback: callable | None = None,
               books_to_build: list[tuple[str, int]] | None = None):

    output_path = Path(output_path)

    # --- Externalized Content ---
    if not COPYRIGHT_FILE.exists() or not STYLE_FILE.exists():
        raise FileNotFoundError(
            f"Could not find required asset files in {ASSETS_DIR}. "
            f"Expected: {COPYRIGHT_FILE.name}, {STYLE_FILE.name}"
        )
    copyright_html = COPYRIGHT_FILE.read_text(encoding="utf-8")
    style = STYLE_FILE.read_text(encoding="utf-8")

    # If no specific books are provided, default to all books from config
    if books_to_build is None:
        books_to_build = BOOKS_DATA

    # 1. Fetch all chapters
    fetch_results = fetch_all_chapters(
        skip_cache=skip_cache,
        retries=retries,
        max_workers=max_workers,
        max_rps=max_rps,
        resume=resume,
        progress_callback=progress_callback,
        books_to_fetch=books_to_build
    )

    # 2. Build EPUB
    book = epub.EpubBook()
    book.set_identifier("net-bible-2nd-ed-final")
    book.set_title("NET Bible (2nd Edition)")
    book.set_language("en")
    book.add_author("Biblical Studies Press")

    # Cover Logic
    if cover_path and Path(cover_path).exists():
        ext = Path(cover_path).suffix.lower()
        book.set_cover(f"cover{ext}", Path(cover_path).read_bytes())

    # Copyright Page
    c_copyright = epub.EpubHtml(title='Copyright', file_name='copyright.xhtml', lang='en')
    c_copyright.content = copyright_html
    book.add_item(c_copyright)

    # CSS
    css_item = epub.EpubItem(
        uid="style", file_name="style.css",
        media_type="text/css", content=style
    )
    book.add_item(css_item)

    chapters_list = []
    
    # 3. Main Loop
    total_books = len(books_to_build)
    for i, (book_name, total) in enumerate(books_to_build):

        if progress_callback:
            # Report progress for compiling this book
            progress_callback("Compiling", i + 1, total_books)

        # --- Cross-Book Linking Logic ---
        # Previous Book Info
        if i > 0:
            prev_book_name, prev_book_total = books_to_build[i-1]
            prev_file = make_filename(prev_book_name)
            prev_book_link = f"{prev_file}#ch{prev_book_total}"
            prev_book_label = f"&laquo; {prev_book_name}"
        else:
            prev_book_link = "copyright.xhtml" # Start goes back to copyright
            prev_book_label = "&laquo; Intro"

        # Next Book Info
        if i < len(books_to_build) - 1:
            next_book_name, _ = books_to_build[i+1]
            next_file = make_filename(next_book_name)
            next_book_link = f"{next_file}#ch1"
            next_book_label = f"{next_book_name} &raquo;"
        else:
            next_book_link = "#"
            next_book_label = ""

        # --- Start Building HTML ---
        filename = make_filename(book_name)
        book_html = []
        
        # A. Book Title Page
        # We add id="top" here so the 'Chapters' button knows where to jump
        book_html.append(f'<h1 id="top" style="font-size: 2.5em; margin-top: 15%;">{book_name}</h1>')
        
        # --- NEW: Intro Disclaimer ---
        disclaimer = """
        <div class="intro-text">
            This noteless version of the NET Bible is provided free by Bible.org's open data. 
            Be sure to check out the full NET Bible with over 60,000 translators' notes and visit 
            <a href="http://netbible.org">netbible.org</a> to use the full NET Bible Study Environment.
        </div>
        """
        book_html.append(disclaimer)

        # B. Chapter Grid
        book_html.append('<div class="chapter-grid">')
        for c in range(1, total + 1):
            book_html.append(f'<a class="grid-link" href="#ch{c}">{c}</a>')
        book_html.append('</div>')
        
        # Page break after the title/grid page
        book_html.append('<div class="break-before"></div>')

        # C. Chapters
        for ch in range(1, total + 1):
            text = fetch_results.get((book_name, ch))
            if not text:
                continue

            if ch > 1:
                book_html.append('<div class="break-before"></div>')

            # --- Calculate Local Prev/Next Links ---
            if ch > 1:
                prev_link = f"#ch{ch-1}"
                prev_text = f"&laquo; Ch {ch-1}"
            else:
                prev_link = prev_book_link
                prev_text = prev_book_label

            if ch < total:
                next_link = f"#ch{ch+1}"
                next_text = f"Ch {ch+1} &raquo;"
            else:
                next_link = next_book_link
                next_text = next_book_label

            # --- NEW: Middle "Back to Grid" Link ---
            # Links to the #top of the current file
            grid_link = f"{filename}#top"

            nav_bar = f'''
            <div class="chapter-nav">
                <a class="nav-link" href="{prev_link}">{prev_text}</a>
                <a class="nav-center" href="{grid_link}">☰ Chapters</a>
                <a class="nav-link" href="{next_link}">{next_text}</a>
            </div>
            '''
            
            book_html.append(f'<div id="ch{ch}">')
            book_html.append(nav_bar)
            book_html.append(f'<h1>Chapter {ch}</h1>')
            book_html.append(text)
            book_html.append('</div>')

        # 4. Create the File
        c = epub.EpubHtml(
            title=book_name,
            file_name=filename,
            lang="en"
        )
        c.content = "".join(book_html)
        c.add_item(css_item)

        book.add_item(c)
        chapters_list.append(c)

    # 5. Finalize Spine & TOC
    # Add copyright as the FIRST item
    book.spine = ['nav', c_copyright] + chapters_list
    
    # We want Copyright and then the Books in the TOC
    book.toc = [c_copyright] + chapters_list

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(output_path, book, {})
