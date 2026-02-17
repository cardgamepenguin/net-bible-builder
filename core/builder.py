from pathlib import Path
from ebooklib import epub
from tqdm import tqdm
from .config import BOOKS_DATA, DEFAULT_OUTPUT
from .fetcher import fetch_all_chapters

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
               cover_path: str | None = "cover.png"):

    output_path = Path(output_path)

    # 1. Fetch all chapters
    total_chapters = sum(ch for _, ch in BOOKS_DATA)
    print(f"Fetching {total_chapters} chapters...")
    fetch_results = fetch_all_chapters(
        skip_cache=skip_cache,
        retries=retries,
        max_workers=max_workers,
        max_rps=max_rps,
        resume=resume
    )

    # 2. Build EPUB
    print("Building EPUB with Copyright & Navigation...")
    book = epub.EpubBook()
    book.set_identifier("net-bible-2nd-ed-final")
    book.set_title("NET Bible (2nd Edition)")
    book.set_language("en")
    book.add_author("Biblical Studies Press")

    # Cover Logic
    if cover_path and Path(cover_path).exists():
        ext = Path(cover_path).suffix.lower()
        book.set_cover(f"cover{ext}", Path(cover_path).read_bytes())

    # --- NEW: Copyright Page ---
    copyright_html = '''
    <div style="text-align: center; margin-top: 3em;">
        <h1>THE NET BIBLE®</h1>
        <h2>Second Edition</h2>
        <h3>Reader's Version</h3>
        <br/><br/>
        <p>Copyright © 1996–2019 by Biblical Studies Press, L.L.C.</p>
        <p>All rights reserved.</p>
        <br/>
        <p>Scripture quoted by permission.</p>
        <p>This noteless version was compiled for personal use via the labs.bible.org open API.</p>
        <p>For more information, visit <a href="https://netbible.com">netbible.com</a>.</p>
    </div>
    '''
    c_copyright = epub.EpubHtml(title='Copyright', file_name='copyright.xhtml', lang='en')
    c_copyright.content = copyright_html
    book.add_item(c_copyright)

    # CSS - Enhanced for Grid, Nav, and Intro Text
    style = """
    body { font-family: serif; line-height: 1.4; }
    h1 { text-align: center; margin-top: 1em; margin-bottom: 0.5em; }
    
    /* Force page break before chapters */
    .break-before { page-break-before: always; }
    
    /* Intro Text Style */
    .intro-text { 
        font-style: italic; color: #555; 
        margin: 1em 10%; text-align: center; font-size: 0.85em; 
    }

    /* Chapter Grid at start of Book */
    .chapter-grid { 
        display: flex; flex-wrap: wrap; justify-content: center; 
        gap: 8px; margin-bottom: 2em; padding: 10px;
    }
    .grid-link { 
        display: inline-block; padding: 8px 12px; background: #eee; 
        text-decoration: none; color: #333; border-radius: 4px; 
        font-size: 0.9em; font-family: sans-serif;
    }
    
    /* Prev/Next Navigation Bar */
    .chapter-nav { 
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 1.5em; font-family: sans-serif; font-size: 0.9em;
        border-bottom: 1px solid #ccc; padding-bottom: 10px;
    }
    .nav-link { 
        text-decoration: none; color: #0066cc; font-weight: bold; 
        padding: 5px;
    }
    .nav-center { 
        text-decoration: none; color: #666; font-size: 0.9em;
    }
    """
    css_item = epub.EpubItem(
        uid="style", file_name="style.css",
        media_type="text/css", content=style
    )
    book.add_item(css_item)

    chapters_list = []
    
    # 3. Main Loop
    pbar = tqdm(BOOKS_DATA, desc="Compiling Books", unit="book")

    for i, (book_name, total) in enumerate(pbar):
        
        # --- Cross-Book Linking Logic ---
        # Previous Book Info
        if i > 0:
            prev_book_name, prev_book_total = BOOKS_DATA[i-1]
            prev_file = make_filename(prev_book_name)
            prev_book_link = f"{prev_file}#ch{prev_book_total}"
            prev_book_label = f"&laquo; {prev_book_name}"
        else:
            prev_book_link = "copyright.xhtml" # Start goes back to copyright
            prev_book_label = "&laquo; Intro"

        # Next Book Info
        if i < len(BOOKS_DATA) - 1:
            next_book_name, _ = BOOKS_DATA[i+1]
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
    print(f"\nDone. Wrote {output_path}")
