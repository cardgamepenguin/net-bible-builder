from ebooklib import epub
from pathlib import Path
from fetcher import fetch_chapter
from config import BOOKS_DATA
from progress import progress_bar


def make_filename(book, chapter):
    safe = book.replace(" ", "_").lower()
    return f"{safe}_{chapter}.xhtml"


def build_epub():
    book = epub.EpubBook()
    book.set_identifier("net-bible-2nd-ed-gold")
    book.set_title("NET Bible (2nd Edition)")
    book.set_language("en")
    book.add_author("Biblical Studies Press")

    # Cover
    if Path("cover.png").exists():
        book.set_cover("cover.png", Path("cover.png").read_bytes())

    # CSS
    style = """
    body { font-family: serif; line-height: 1.4; }
    h1 { text-align: center; margin-top: 1em; }
    .chapter-nav { display: flex; justify-content: space-between; }
    """
    css_item = epub.EpubItem(
        uid="style", file_name="style.css",
        media_type="text/css", content=style
    )
    book.add_item(css_item)

    all_items = []
    toc_sections = []

    total_chapters = sum(ch for _, ch in BOOKS_DATA)
    pbar = progress_bar(total_chapters, "Building EPUB")

    for book_name, chapters in BOOKS_DATA:
        section_items = []

        for ch in range(1, chapters + 1):
            text = fetch_chapter(book_name, ch)
            pbar.update(1)

            if not text:
                continue

            filename = make_filename(book_name, ch)
            html = epub.EpubHtml(
                title=f"{book_name} {ch}",
                file_name=filename,
                lang="en"
            )
            html.content = f"<h1>{book_name} {ch}</h1>{text}"
            html.add_item(css_item)

            book.add_item(html)
            section_items.append(html)
            all_items.append(html)

        toc_sections.append((epub.Section(book_name), section_items))

    pbar.close()

    # TOC + spine
    book.toc = toc_sections
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + all_items

    epub.write_epub("epub/NET_Bible_2nd_Ed_Complete_a.epub", book)

