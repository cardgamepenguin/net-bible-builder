import requests
import time
from ebooklib import epub

# --- CONFIGURATION ---
# PASTE YOUR FULL 66-BOOK LIST HERE
BOOKS_DATA = [
    # Old Testament
    ("Genesis", 50), ("Exodus", 40), ("Leviticus", 27), ("Numbers", 36), ("Deuteronomy", 34),
    ("Joshua", 24), ("Judges", 21), ("Ruth", 4), ("1 Samuel", 31), ("2 Samuel", 24),
    ("1 Kings", 22), ("2 Kings", 25), ("1 Chronicles", 29), ("2 Chronicles", 36),
    ("Ezra", 10), ("Nehemiah", 13), ("Esther", 10), ("Job", 42), ("Psalms", 150),
    ("Proverbs", 31), ("Ecclesiastes", 12), ("Song of Solomon", 8), ("Isaiah", 66),
    ("Jeremiah", 52), ("Lamentations", 5), ("Ezekiel", 48), ("Daniel", 12),
    ("Hosea", 14), ("Joel", 3), ("Amos", 9), ("Obadiah", 1), ("Jonah", 4), ("Micah", 7),
    ("Nahum", 3), ("Habakkuk", 3), ("Zephaniah", 3), ("Haggai", 2), ("Zechariah", 14), ("Malachi", 4),
    # New Testament
    ("Matthew", 28), ("Mark", 16), ("Luke", 24), ("John", 21), ("Acts", 28),
    ("Romans", 16), ("1 Corinthians", 16), ("2 Corinthians", 13), ("Galatians", 6),
    ("Ephesians", 6), ("Philippians", 4), ("Colossians", 4), ("1 Thessalonians", 5),
    ("2 Thessalonians", 3), ("1 Timothy", 6), ("2 Timothy", 4), ("Titus", 3),
    ("Philemon", 1), ("Hebrews", 13), ("James", 5), ("1 Peter", 5), ("2 Peter", 3),
    ("1 John", 5), ("2 John", 1), ("3 John", 1), ("Jude", 1), ("Revelation", 22)
]


def get_filename(book_name):
    return f"{book_name.replace(' ', '_').lower()}.xhtml"

def fetch_chapter_text(book, chapter):
    url = "https://labs.bible.org/api/"
    params = {'passage': f"{book} {chapter}", 'formatting': 'para'}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.text
    except Exception:
        pass
    return None

def create_net_bible_gold():
    print("--- Starting Project NET Bible: Gold Master ---")
    
    book = epub.EpubBook()
    book.set_identifier('net-bible-2nd-ed-gold')
    book.set_title('NET Bible (2nd Edition)')
    book.set_language('en')
    book.add_author('Biblical Studies Press')
    
    # 1. THE COVER IMAGE
    # Make sure 'cover.png' is in the same folder!
    try:
        book.set_cover("cover.png", open('cover.png', 'rb').read())
        print(" - Cover image applied.")
    except FileNotFoundError:
        print(" - WARNING: 'cover.png' not found. Skipping cover image.")

    # 2. THE COPYRIGHT PAGE (New!)
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
        <p>This ebook was compiled for personal use via the labs.bible.org API.</p>
        <p>For more information, visit <a href="https://netbible.com">netbible.com</a>.</p>
    </div>
    '''
    c_copyright = epub.EpubHtml(title='Copyright', file_name='copyright.xhtml', lang='en')
    c_copyright.content = copyright_html
    book.add_item(c_copyright)

    # 3. CSS STYLING
    style = '''
    body { font-family: serif; line-height: 1.4; }
    h1 { text-align: center; margin-top: 1em; }
    h3 { margin-top: 2em; border-bottom: 1px solid #ccc; }
    .chapter-grid { display: flex; flex-wrap: wrap; justify-content: center; gap: 5px; margin-bottom: 2em; }
    .grid-link { 
        display: inline-block; padding: 5px 10px; background: #eee; 
        text-decoration: none; color: #333; border-radius: 3px; font-size: 0.8em;
    }
    .chapter-nav { 
        display: flex; justify-content: space-between; font-size: 0.9em; 
        margin-bottom: 1em; font-family: sans-serif; color: #666;
    }
    .nav-link { text-decoration: none; color: #0066cc; font-weight: bold; }
    '''
    css_item = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(css_item)

    epub_chapters = []

    # 4. MAIN LOOP (Book Generation)
    for i, (book_name, total_chapters) in enumerate(BOOKS_DATA):
        print(f"Processing {book_name}...")
        
        # Navigation Links Logic
        prev_book_file = get_filename(BOOKS_DATA[i-1][0]) if i > 0 else None
        prev_book_last_chap = BOOKS_DATA[i-1][1] if i > 0 else None
        next_book_file = get_filename(BOOKS_DATA[i+1][0]) if i < len(BOOKS_DATA)-1 else None

        # Chapter Grid
        grid_html = '<div class="chapter-grid">'
        for c in range(1, total_chapters + 1):
            grid_html += f'<a class="grid-link" href="#chapter-{c}">{c}</a> '
        grid_html += '</div><hr/>'

        book_content = f'<h1 id="book-title">{book_name}</h1>{grid_html}'

        for chapter in range(1, total_chapters + 1):
            text = fetch_chapter_text(book_name, chapter)
            if not text: continue

            # Prev/Next Logic
            if chapter > 1:
                prev_link = f'#chapter-{chapter-1}'
                prev_text = f"&laquo; Ch {chapter-1}"
            elif prev_book_file:
                prev_link = f'{prev_book_file}#chapter-{prev_book_last_chap}'
                prev_text = f"&laquo; {BOOKS_DATA[i-1][0]}"
            else: # Very start of Bible
                prev_link = "copyright.xhtml" # Point back to copyright page!
                prev_text = "&laquo; Intro"

            if chapter < total_chapters:
                next_link = f'#chapter-{chapter+1}'
                next_text = f"Ch {chapter+1} &raquo;"
            elif next_book_file:
                next_link = f'{next_book_file}#chapter-1'
                next_text = f"{BOOKS_DATA[i+1][0]} &raquo;"
            else:
                next_link = "#"
                next_text = ""

            nav_bar = f'''
            <div class="chapter-nav">
                <a class="nav-link" href="{prev_link}">{prev_text}</a>
                <span>Chapter {chapter}</span>
                <a class="nav-link" href="{next_link}">{next_text}</a>
            </div>
            '''
            
            book_content += f'<div id="chapter-{chapter}">{nav_bar}{text}</div><br/><hr/><br/>'
            time.sleep(1.1) # Stay polite!

        filename = get_filename(book_name)
        c = epub.EpubHtml(title=book_name, file_name=filename, lang='en')
        c.content = book_content
        c.add_item(css_item)
        book.add_item(c)
        epub_chapters.append(c)
        print(f"  - Finished {book_name}")

    # 5. BINDING IT ALL TOGETHER
    # This structure creates the hierarchy in the Kindle "Go To" menu
    book.toc = (c_copyright, (epub.Section('Bible Books'), epub_chapters))
    
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # The Spine is the actual reading order
    # Note: 'nav' is the hidden navigation file, we don't usually see it
    book.spine = ['nav', c_copyright] + epub_chapters

    epub.write_epub('NET_Bible_2nd_Ed_Complete.epub', book, {})
    print("\nSuccess! 'NET_Bible_2nd_Ed_Complete.epub' created.")

if __name__ == "__main__":
    create_net_bible_gold()
