import re
from typing import Dict


def clean_text(text: str) -> str:
    if not text:
        return ""
    cleaned = text.replace("\r", " ").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.replace("\u2014", "-")
    cleaned = cleaned.replace("\u201c", '"').replace("\u201d", '"')
    cleaned = cleaned.replace("\u2018", "'").replace("\u2019", "'")
    cleaned = re.sub(r"\n{2,}", "\n\n", cleaned)
    return cleaned


def count_words(text: str) -> int:
    return len(text.split()) if text else 0


def count_characters(text: str) -> int:
    return len(text) if text else 0


def estimate_reading_time(text: str, words_per_minute: int = 200) -> float:
    word_count = count_words(text)
    return round(word_count / words_per_minute, 2)


def analyze_text(text: str) -> Dict[str, float]:
    cleaned = clean_text(text)
    word_count = count_words(cleaned)
    return {
        "word_count": word_count,
        "character_count": count_characters(cleaned),
        "reading_time_minutes": estimate_reading_time(cleaned),
    }
