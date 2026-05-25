import os
from typing import List

from PyPDF2 import PdfReader

from utils.text_cleaner import clean_text


def extract_text_from_pdf(file_path: str) -> str:
    if not file_path:
        raise ValueError("PDF file path is required.")
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        reader = PdfReader(file_path)
    except Exception as exc:
        raise RuntimeError(f"Unable to open PDF file: {exc}") from exc

    if not reader.pages:
        raise ValueError("The PDF file contains no readable pages.")

    page_text: List[str] = []
    for page in reader.pages:
        extracted = page.extract_text() or ""
        if extracted:
            page_text.append(extracted)

    if not page_text:
        raise ValueError("No text could be extracted from the PDF.")

    return clean_text("\n\n".join(page_text))
