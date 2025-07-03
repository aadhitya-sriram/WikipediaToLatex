import wikipedia
import requests
from bs4 import BeautifulSoup
import json

class WikipediaImageDownloader:

    def __init__(self):
        pass

    def fetch_wikipedia_images(self, page_title, lang='en'):
        print(f"Image Processing: {page_title}")
        wikipedia.set_lang(lang)

        try:
            summary = wikipedia.summary(page_title)
            page = wikipedia.page(page_title)
            page_url = page.url
        except wikipedia.exceptions.DisambiguationError as e:
            raise ValueError(f"DisambiguationError: Try a more specific title. Options: {e.options}")
        except wikipedia.exceptions.PageError:
            raise ValueError(f"The page '{page_title}' does not exist.")

        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        images = []
        seen_urls = set()

        for figure in soup.find_all('figure'):
            img_tag = figure.find('img')
            if not img_tag:
                continue
            if 'math-fallback' in img_tag.get('class', []):
                continue
            img_url = img_tag.get('src')
            if not img_url:
                continue
            if not img_url.startswith('http'):
                img_url = f"https:{img_url}"
            if img_url in seen_urls:
                continue
            seen_urls.add(img_url)

            image_name = img_url.split("/")[-1]
            figcaption = figure.find('figcaption')
            description = figcaption.get_text(strip=True) if figcaption else (
                img_tag.get('alt') or img_tag.get('title') or "No description")

            images.append({
                'name': image_name,
                'url': img_url,
                'class': img_tag.get('class', []),
                'description': description
            })

        for img_tag in soup.find_all('img'):
            img_url = img_tag.get('src')
            image_name = img_url.split("/")[-1]
            description = img_tag.get('alt') or img_tag.get('title') or "No description"

            if 'logo' in image_name.lower() or 'icon' in image_name.lower() or 'edit' in image_name.lower() or 'clear' in image_name.lower():
                continue

            flag = True
            for c in img_tag.get('class', []):
                if 'math-fallback' in c:
                    flag = False
                    break
            
            if not flag:
                continue
            if not img_url:
                continue
            if 'resources/assets' in img_url or 'static/images' in img_url or 'logo' in img_url.lower() or 'icon' in img_url.lower() or 'icons' in img_url or 'edit' in img_url.lower() or 'clear' in img_url.lower():
                continue
            if not img_url.startswith('http'):
                img_url = f"https:{img_url}"
            if img_url in seen_urls:
                continue
            seen_urls.add(img_url)

            images.append({
                'name': image_name,
                'url': img_url,
                'class': img_tag.get('class', []),
                'description': description
            })

        data = {
            'wiki_page_title': page.title,
            'wiki_page_summary': summary,
            'images': images
        }

        return data

    # Integrate and use if needed
    def save_to_json(self, data):
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
