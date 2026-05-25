from datetime import datetime
from typing import Any, Dict

from database.mongodb import MongoDBClient
from models.summary_model import SummaryRecord
from utils.summarizer import summarize_text
from utils.text_cleaner import analyze_text


class SummaryService:
    def __init__(self) -> None:
        self.db_client = MongoDBClient()

    def create_summary(
        self,
        source_type: str,
        source_content: str,
        summary_style: str,
        document_style: str,
        title: str = "",
    ) -> Dict[str, Any]:
        cleaned_text = source_content.strip()
        if not cleaned_text:
            raise ValueError("No content available for summarization.")

        summary_text = summarize_text(
            text=cleaned_text,
            summary_style=summary_style,
            document_style=document_style,
            title=title,
        )
        stats = analyze_text(cleaned_text)
        record = SummaryRecord(
            original_text=cleaned_text,
            summary=summary_text,
            summary_type=summary_style,
            document_style=document_style,
            source_type=source_type,
            title=title,
            created_at=datetime.utcnow(),
            statistics=stats,
        )
        record_id = self.db_client.save_summary(record.to_dict())
        saved_record = record.to_dict()
        saved_record["id"] = record_id
        return saved_record

    def get_history(self, limit: int = 20) -> Any:
        return self.db_client.get_summary_history(limit=limit)

    def close(self) -> None:
        self.db_client.close()
