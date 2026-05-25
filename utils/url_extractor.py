from typing import Optional, Tuple
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from utils.text_cleaner import clean_text

try:
    from newspaper import Article
except ImportError:
    Article = None


def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Invalid URL format. Please provide a valid http or https URL.")


def _fallback_extract(url: str) -> Tuple[str, str]:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; AIContentSummarizer/1.0)"
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    paragraphs = []

    article_tags = soup.find_all(["article", "section"])
    for node in article_tags:
        text = node.get_text(separator=" ", strip=True)
        if text:
            paragraphs.append(text)

    if not paragraphs:
        for paragraph in soup.find_all("p"):
            text = paragraph.get_text(separator=" ", strip=True)
            if text:
                paragraphs.append(text)

    content = "\n\n".join(paragraphs).strip()
    if not content:
        raise ValueError("Unable to extract article content from the URL.")

    return title or url, clean_text(content)


def extract_text_from_url(url: str) -> Tuple[str, str]:
    if not url:
        raise ValueError("URL is required for extraction.")
    _validate_url(url)

    if Article is not None:
        try:
            article = Article(url)
            article.download()
            article.parse()
            title = article.title.strip() if article.title else ""
            text = article.text.strip() if article.text else ""
            if text and len(text) > 120:
                return title or url, clean_text(text)
        except Exception:
            pass

    return _fallback_extract(url)
