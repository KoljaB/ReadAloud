import requests
from bs4 import BeautifulSoup
from newspaper import Article
from readability import Document
import trafilatura
import re

def extract_with_newspaper(html, url):
    """Extract content using newspaper3k with existing HTML"""
    try:
        article = Article(url)
        article.download(input_html=html)
        article.parse()
        return article.text
    except Exception as e:
        print(f"Newspaper error: {e}")
        return None

def extract_with_trafilatura(html):
    """Extract content using Trafilatura"""
    try:
        return trafilatura.extract(html, include_links=False, include_tables=False)
    except Exception as e:
        print(f"Trafilatura error: {e}")
        return None

def extract_with_readability(html):
    """Extract content using readability-lxml"""
    try:
        doc = Document(html)
        return doc.summary()
    except Exception as e:
        print(f"Readability error: {e}")
        return None

def extract_with_bs4(html):
    """Fallback with BeautifulSoup heuristics"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try semantic HTML5 tags first
        for tag in ['article', 'main', 'section.content']:
            elements = soup.find_all(tag)
            if elements:
                return max(elements, key=lambda e: len(e.text)).text
        
        # Content density analysis
        paragraphs = soup.find_all(['p', 'div'])
        if paragraphs:
            return max([p.text for p in paragraphs], key=lambda x: len(x.split()))
            
        return None
    except Exception as e:
        print(f"BeautifulSoup error: {e}")
        return None

def clean_html_text(text):
    """Enhanced cleaning for TTS"""
    text = re.sub(r'\n{3,}', '\n\n', text)  # Reduce excessive newlines
    text = re.sub(r'\s{2,}', ' ', text)     # Remove multiple spaces
    text = re.sub(r'\[.*?\]', '', text)     # Remove bracketed content
    return text.strip()

def get_main_content(url):
    # Fetch HTML content
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        print(f"Failed to fetch URL: {e}")
        return None

    content = None
    extractor = None

    # List of (function, name) pairs.
    # Note: For Newspaper, we wrap it in a lambda because it requires both html and url.
    extractors = [
        (lambda h: extract_with_newspaper(h, url), "Newspaper"),
        (extract_with_trafilatura, "Trafilatura"),
        (extract_with_readability, "Readability"),
        (extract_with_bs4, "BeautifulSoup")
    ]

    # Try each extractor until one returns a result.
    for func, name in extractors:
        result = func(html)
        if result:
            content = result
            extractor = name
            break

    if content:
        print(f"Content extracted with: {extractor}")
        return clean_html_text(content)
    else:
        print("No content extracted.")
        return None


# Example usage remains the same