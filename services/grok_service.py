import os
import time
from typing import Any, Dict, Optional

import requests
from utils.env_loader import load_project_env

load_project_env()

GROK_API_KEY = os.getenv("GROK_API_KEY", "").strip()


class GrokService:
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30) -> None:
        api_key_value = api_key if api_key is not None else GROK_API_KEY
        if not api_key_value:
            raise ValueError("GROK_API_KEY is not configured in the environment.")
        
        # Detect service provider (Groq vs xAI) based on the key prefix
        if api_key_value.startswith("gsk_"):
            self.endpoint = "https://api.groq.com/openai/v1/chat/completions"
            self.model_name = "llama-3.3-70b-versatile"
        else:
            self.endpoint = "https://api.x.ai/v1/chat/completions"
            self.model_name = "grok-2"

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key_value}",
                "Content-Type": "application/json",
            }
        )
        self.timeout = timeout

    def _parse_response(self, data: Dict[str, Any]) -> str:
        if not isinstance(data, dict):
            raise ValueError("Grok response payload is malformed.")

        # OpenAI-compatible format (used by Grok)
        choices = data.get("choices", [])
        if choices and isinstance(choices, list):
            first_choice = choices[0]
            if isinstance(first_choice, dict):
                message = first_choice.get("message", {})
                if isinstance(message, dict):
                    content = message.get("content", "").strip()
                    if content:
                        return content

        # Fallback for other formats
        if isinstance(data.get("output_text"), str):
            return data.get("output_text", "").strip()

        return str(data.get("response", "")).strip()

    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 600,
        temperature: float = 0.2,
        retries: int = 3,
    ) -> str:
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        for attempt in range(1, retries + 1):
            try:
                response = self.session.post(
                    self.endpoint,
                    json=payload,
                    timeout=self.timeout,
                )
                if response.status_code == 200:
                    return self._parse_response(response.json())

                if response.status_code in {401, 403}:
                    raise PermissionError(
                        f"Invalid API key or access denied. Response: {response.text.strip()}"
                    )

                if response.status_code == 429:
                    raise RuntimeError(
                        f"Grok API rate limit exceeded. Response: {response.text.strip()}"
                    )

                if response.status_code == 400:
                    print(f"DEBUG - Request payload: {payload}")
                    print(f"DEBUG - Response: {response.text}")
                    raise RuntimeError(
                        f"Bad Request (400): {response.text.strip()}"
                    )

            except PermissionError:
                raise
            except requests.RequestException as exc:
                if attempt >= retries:
                    raise RuntimeError(
                        f"Grok API request failed after {retries} attempts: {exc}"
                    ) from exc
                time.sleep(attempt * 2)
            except ValueError as exc:
                raise RuntimeError("Invalid Grok response format.") from exc

        raise RuntimeError("Grok service request could not be completed.")
