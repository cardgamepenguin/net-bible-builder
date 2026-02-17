# NET Bible (2nd Edition) Builder 📖🐍

A Python tool that procedurally generates a "Gold Master" EPUB of the NET Bible (2nd Edition) using the `labs.bible.org` API.

**Purpose:** To create a clean, distraction-free "Reader's Version" of the scriptures for personal use and ministry, featuring distinct "Fresh Page" chapter breaks and smart cross-book navigation.

## Features

*   **GUI and CLI:** Run with a simple graphical interface or from the command line.
*   **Customizable Builds:** Select which books of the Bible to include in your EPUB, with presets for Old and New Testaments.
*   **Parallel Fetching:** Scrapes all chapters using multi-threading for speed.
*   **Smart Caching:** Saves raw HTML locally; if a build is interrupted, you don't have to re-download everything.
*   **Clean Navigation:** The EPUB menu lists only the books (not all 1,189 chapters) to keep the interface clean.
*   **Modern UX:** Includes a "Chapter Grid" at the start of every book for fast navigation, plus easy previous/next chapter and book links.
*   **Validation:** Optional EPUB validation using `epubcheck` to ensure compatibility.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/cardgamepenguin/net-bible-builder.git
    cd net-bible-builder
    ```

2.  **Install dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```
    > **Note for Linux users:** The GUI requires GTK. You may need to install it via your package manager, e.g., `sudo apt-get install libgtk-3-dev gir1.2-gtk-3.0` on Debian/Ubuntu.

## Usage

### Graphical User Interface (GUI)

For the easiest experience, run the GTK-based GUI:

```bash
python gui_gtk.py
