import os
import json
import sys
import wikipedia
from wiki_latex import WikipediaToLatexConverter
from wiki_image import WikipediaImageDownloader

# CHANGE THIS TO YOUR DESIRED OUTPUT DIRECTORY
output_dir = r""
latex_converter = WikipediaToLatexConverter()
image_downloader = WikipediaImageDownloader()

if __name__ == "__main__":
    if sys.argv[1]:
        page_title = sys.argv[1]

    wikipedia.set_lang('en')
    page_title = wikipedia.search(page_title)[0]
    try:
        wikipedia.page(page_title)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)
    
    if not page_title:
        print("No Wikipedia page found for the given title.")
        exit(1)

    output_dir += page_title.replace(" ", "_").lower()
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Processing page: {page_title}")    
    try:
        latex_data = latex_converter.wikipedia_to_clean_latex(page_title)
        image_data = image_downloader.fetch_wikipedia_images(page_title)
    except wikipedia.exceptions.PageError:
        print(f"No page found for: '{page_title}'")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)

    with open(os.path.join(output_dir, f'{page_title}_latex.tex'), 'w', encoding='utf-8') as f:
        f.write(latex_data)
    
    with open(os.path.join(output_dir, f'{page_title}_images.json'), 'w', encoding='utf-8') as f:
        json.dump(image_data, f, indent=2, ensure_ascii=False)