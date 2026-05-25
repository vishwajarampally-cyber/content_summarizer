import os
from typing import Optional

from utils.env_loader import load_project_env

from services.summary_service import SummaryService
from utils.pdf_handler import extract_text_from_pdf
from utils.url_extractor import extract_text_from_url
from utils.text_cleaner import analyze_text
from utils.prompts import DOCUMENT_STYLE_OPTIONS, SUMMARY_STYLE_OPTIONS

load_project_env()


def prompt_menu(options: dict, prompt_message: str) -> str:
    while True:
        print(prompt_message)
        for key, value in options.items():
            print(f"{key}. {value}")
        selection = input("Enter choice: ").strip()
        if selection in options:
            return options[selection]
        print("Invalid choice. Please choose one of the listed options.\n")


def prompt_text_input() -> str:
    print("\nPaste your text below. Enter a blank line to finish:")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def prompt_pdf_path() -> Optional[str]:
    path = input("Enter the PDF file path: ").strip()
    if not path:
        print("PDF path cannot be empty.\n")
        return None
    return path


def prompt_url() -> Optional[str]:
    url = input("Enter the article URL: ").strip()
    if not url:
        print("URL cannot be empty.\n")
        return None
    return url


def main() -> None:
    print("AI Content Summarizer\n======================\n")

    try:
        service = SummaryService()
    except Exception as exc:
        print(f"Startup error: {exc}")
        return

    try:
        while True:
            print("\nMain Menu")
            print("1. Paste long text")
            print("2. Summarize PDF file")
            print("3. Summarize article URL")
            print("4. View saved summaries")
            print("5. Exit")
            choice = input("Select an option: ").strip()

            if choice == "1":
                text = prompt_text_input()
                if not text:
                    print("No text entered. Please try again.")
                    continue
                document_style = prompt_menu(DOCUMENT_STYLE_OPTIONS, "Choose the content type:")
                summary_style = prompt_menu(SUMMARY_STYLE_OPTIONS, "Choose the summary style:")
                record = service.create_summary(
                    source_type="text",
                    source_content=text,
                    summary_style=summary_style,
                    document_style=document_style,
                    title="",
                )
                print("\nSummary generated successfully:\n")
                print(record["summary"])
                print_summary_stats(record)

            elif choice == "2":
                path = prompt_pdf_path()
                if not path:
                    continue
                try:
                    extracted_text = extract_text_from_pdf(path)
                except Exception as exc:
                    print(f"PDF error: {exc}")
                    continue
                document_style = prompt_menu(DOCUMENT_STYLE_OPTIONS, "Choose the content type for the PDF:")
                summary_style = prompt_menu(SUMMARY_STYLE_OPTIONS, "Choose the summary style:")
                record = service.create_summary(
                    source_type="pdf",
                    source_content=extracted_text,
                    summary_style=summary_style,
                    document_style=document_style,
                    title=os.path.basename(path),
                )
                print("\nSummary generated successfully:\n")
                print(record["summary"])
                print_summary_stats(record)

            elif choice == "3":
                url = prompt_url()
                if not url:
                    continue
                try:
                    title, article_text = extract_text_from_url(url)
                except Exception as exc:
                    print(f"URL error: {exc}")
                    continue
                document_style = prompt_menu(DOCUMENT_STYLE_OPTIONS, "Choose the content type for the article:")
                summary_style = prompt_menu(SUMMARY_STYLE_OPTIONS, "Choose the summary style:")
                record = service.create_summary(
                    source_type="url",
                    source_content=article_text,
                    summary_style=summary_style,
                    document_style=document_style,
                    title=title,
                )
                print("\nSummary generated successfully:\n")
                print(record["summary"])
                print_summary_stats(record)

            elif choice == "4":
                history = service.get_history()
                if not history:
                    print("No saved summaries found.")
                    continue
                for item in history:
                    print_summary_record(item)

            elif choice == "5":
                print("Exiting. Goodbye!")
                break

            else:
                print("Invalid selection, please choose a number between 1 and 5.")

    finally:
        service.close()


def print_summary_stats(record: dict) -> None:
    stats = record.get("statistics", {})
    print("\nSummary statistics:")
    print(f"- Word count: {stats.get('word_count', 0)}")
    print(f"- Character count: {stats.get('character_count', 0)}")
    print(f"- Estimated reading time: {stats.get('reading_time_minutes', 0):.1f} minutes")
    print(f"- Summary style: {record.get('summary_type', '')}")
    print(f"- Content type: {record.get('document_style', '')}\n")


def print_summary_record(record: dict) -> None:
    print("\n--- Saved Summary ---")
    print(f"Title: {record.get('title', 'N/A')}")
    print(f"Source type: {record.get('source_type', 'N/A')}")
    print(f"Summary type: {record.get('summary_type', 'N/A')}")
    print(f"Content type: {record.get('document_style', 'N/A')}")
    print(f"Created at: {record.get('created_at', 'N/A')}")
    print(f"Summary:\n{record.get('summary', '')}\n")


if __name__ == "__main__":
    main()
