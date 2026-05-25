from typing import List

from services.grok_service import GrokService
from utils.prompts import build_summary_prompt
from utils.text_cleaner import clean_text

MAX_CHUNK_SIZE = 14000


def _chunk_text(text: str, max_chars: int = MAX_CHUNK_SIZE) -> List[str]:
    segments: List[str] = []
    if len(text) <= max_chars:
        return [text]

    current_segment = []
    current_length = 0

    for word in text.split():
        if current_length + len(word) + 1 > max_chars:
            segments.append(" ".join(current_segment).strip())
            current_segment = [word]
            current_length = len(word)
        else:
            current_segment.append(word)
            current_length += len(word) + 1

    if current_segment:
        segments.append(" ".join(current_segment).strip())

    return segments


def summarize_text(
    text: str,
    summary_style: str,
    document_style: str,
    title: str = "",
) -> str:
    cleaned_text = clean_text(text)
    if not cleaned_text:
        raise ValueError("Text must not be empty for summarization.")

    grok = GrokService()
    chunks = _chunk_text(cleaned_text)
    summaries: List[str] = []

    for index, chunk in enumerate(chunks, start=1):
        prompt = build_summary_prompt(
            content=chunk,
            summary_style=summary_style,
            document_style=document_style,
            title=title,
            is_final=False,
        )
        summaries.append(
            grok.generate_text(
                prompt=prompt,
                max_tokens=700,
            )
        )

    if len(summaries) == 1:
        return summaries[0]

    combined_prompt = build_summary_prompt(
        content="\n\n".join(summaries),
        summary_style=summary_style,
        document_style=document_style,
        title=title,
        is_final=True,
    )
    return grok.generate_text(prompt=combined_prompt, max_tokens=700)
