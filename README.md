# NET Bible (2nd Edition) Builder 📖🐍

A Python tool that procedurally generates a "Gold Master" EPUB of the NET Bible (2nd Edition) using the `labs.bible.org` API.

**Purpose:** To create a clean, distraction-free "Reader's Version" of the scriptures for personal use and ministry, featuring distinct "Fresh Page" chapter breaks and smart cross-book navigation.

## Features
* **Parallel Fetching:** Scrapes all 1,189 chapters using multi-threading.
* **Smart Caching:** Saves raw HTML locally; if the build fails, you don't have to re-download.
* **Clean Spine:** The EPUB menu lists only the 66 Books (not 1,000+ chapters) to keep the interface clean.
* **Grid Navigation:** Includes a "Chapter Grid" at the start of every book for fast navigation.
* **Booklet Mode:** Includes a script (`make_booklet.py`) to generate PDF booklets (e.g., The Gospel of John) for printing and folding.

## How to Use

### 1. Install Dependencies
```bash
pip install ebooklib requests tqdm weasyprint pypdf
