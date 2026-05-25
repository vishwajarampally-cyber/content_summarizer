from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict


@dataclass
class SummaryRecord:
    original_text: str
    summary: str
    summary_type: str
    document_style: str
    source_type: str
    title: str
    created_at: datetime
    statistics: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["created_at"] = self.created_at.isoformat()
        return result
