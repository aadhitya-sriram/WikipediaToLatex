# Wikipedia to LaTeX format

A small set of Python scripts and a shell helper to fetch Wikipedia articles, convert their wikitext into clean LaTeX, and download associated images. This was specifically developed to convert with full-math text intact in .tex format

---

## Features

- **Scrape & Convert**  
  – Fetch raw wikitext for a given page title via the MediaWiki API  
  – Convert to LaTeX using [pypandoc]  
  – Post-process and clean up common wiki artifacts, math markup, and unwanted sections (e.g. “See also”)

- **Image Extraction**  
  – Download all relevant `<figure>` and `<img>` elements from the live page HTML  
  – Filter out math fallbacks, icons/logos, static assets, etc.  
  – Produce a JSON manifest with image URLs, filenames, and descriptions

- **Batch Processing**  
  – Read a list of page titles from `wiki_data.txt`  
  – Loop through them via `run_pipeline.sh`, invoking the scraper for each entry

---

## Repository Structure

```
.
├── wiki_scrapper.py      # Entry-point: orchestrates LaTeX conversion & image download
├── wiki_latex.py         # Module: fetches wikitext → converts & cleans to LaTeX
├── wiki_image.py         # Module: scrapes HTML → downloads image metadata
├── wiki_data.txt         # Input: one Wikipedia page title per line
├── requirements.txt      # Python dependencies
└── run_pipeline.sh       # Bash wrapper to process all titles in wiki_data.txt
```

---

## Prerequisites

- Python 3.6 or newer  
- [Pandoc] installed and on your `$PATH`  
- `git` (if cloning from a remote repository)  

---

## Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/your-username/WikipediaToLaTeX.git
   cd WikipediaToLaTeX
   ```

2. **Install Python dependencies**  
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Ensure `pandoc` is available**  
   ```bash
   pandoc --version
   ```
   And then run,
   ```python
   pypandoc.download_pandoc()
   ```
---

## Configuration

1. **Output directory**  
   At the top of `wiki_scrapper.py`, set:
   ```python
   # CHANGE THIS TO YOUR DESIRED OUTPUT DIRECTORY
   output_dir = r"/path/to/your/outputs"
   ```

2. **Input list**  
   Edit `wiki_data.txt`, one page title per line:
   ```
   Scalar multiplication
   Eigenvalue
   Fourier transform
   ```

---

## Usage

### Single page

```bash
python3 wiki_scrapper.py "Page Title"
```

This will generate in `output_dir`:

- `Page_Title_latex.tex` — the cleaned-up LaTeX document  
- `Page_Title_images.json` — metadata for each downloaded image

### Batch mode

```bash
chmod +x run_pipeline.sh
./run_pipeline.sh
```

Reads `wiki_data.txt` and processes each non-empty line.

---

## Dependencies

- `wikipedia`  
- `requests`  
- `beautifulsoup4`  
- `pypandoc`  

Install via:
```bash
pip install wikipedia requests beautifulsoup4 pypandoc
```

---

## Extending & Troubleshooting

- **Custom cleanup rules**  
  Modify or extend the regex maps in `wiki_latex.py` to handle additional templates or symbols.

- **Error handling**  
  The scraper will exit if a page isn’t found or on unexpected errors—wrap calls in your own scripts to continue on failure.

- **Image filters**  
  Tweak the class- and filename-based filters in `wiki_image.py` to include/exclude other assets.

---
