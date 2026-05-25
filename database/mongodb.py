import os
import warnings
from typing import Any, Dict, List

from utils.env_loader import load_project_env
from pymongo import MongoClient, errors

load_project_env()

try:
    import mongomock  # type: ignore
except Exception:
    mongomock = None


MONGODB_URL = os.getenv("MONGODB_URL", "").strip()
DATABASE_NAME = "content_summarizer"
COLLECTION_NAME = "summaries"


class MongoDBClient:
    def __init__(self, connection_string: str = MONGODB_URL) -> None:
        if not connection_string:
            raise ValueError("MONGODB_URL is not configured in the environment.")

        self._in_memory = False
        try:
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            self.db = self.client[DATABASE_NAME]
            self.collection = self.db[COLLECTION_NAME]
            self._verify_connection()
        except errors.PyMongoError as exc:
            if mongomock is not None:
                warnings.warn(
                    "Could not connect to MongoDB at the configured URL; falling back to an in-memory database (mongomock)."
                )
                self.client = mongomock.MongoClient()
                self.db = self.client[DATABASE_NAME]
                self.collection = self.db[COLLECTION_NAME]
                self._in_memory = True
            else:
                raise ConnectionError(f"Failed to connect to MongoDB: {exc}") from exc

    def _verify_connection(self) -> None:
        try:
            self.client.admin.command("ping")
        except errors.PyMongoError as exc:
            raise ConnectionError(f"MongoDB ping failed: {exc}") from exc

    def save_summary(self, summary_record: Dict[str, Any]) -> str:
        try:
            result = self.collection.insert_one(summary_record)
            return str(result.inserted_id)
        except Exception as exc:
            raise RuntimeError(f"Failed to save summary to MongoDB: {exc}") from exc

    def get_summary_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        try:
            records = list(
                self.collection.find()
                .sort("created_at", -1)
                .limit(limit)
            )
            for record in records:
                record["_id"] = str(record["_id"])
            return records
        except Exception as exc:
            raise RuntimeError(f"Failed to retrieve summary history: {exc}") from exc

    def close(self) -> None:
        if hasattr(self, "client"):
            try:
                self.client.close()
            except Exception:
                pass
