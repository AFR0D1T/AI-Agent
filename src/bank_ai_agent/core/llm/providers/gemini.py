"""Адаптер LLMProvider для Google Gemini (free tier, Google AI Studio).

Модель по умолчанию — gemini-2.5-flash: нативно читает/понимает документы,
щедрая бесплатная квота. Реализует core.llm.client.LLMProvider — остальной
пайплайн не знает, что за этим интерфейсом стоит именно Gemini.
"""

from __future__ import annotations

import json
import os
from typing import Any

from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential


class GeminiProvider:
    def __init__(self, *, model: str = "gemini-2.5-flash", api_key: str | None = None) -> None:
        self.model = model
        # genai.Client сам подхватит GEMINI_API_KEY/GOOGLE_API_KEY из окружения,
        # если api_key явно не передан.
        self._client = genai.Client(api_key=api_key or os.environ.get("GEMINI_API_KEY"))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=20),
        reraise=True,
    )
    def extract(
        self,
        *,
        prompt: str,
        schema: dict[str, Any],
        document_text: str,
    ) -> dict[str, Any]:
        response = self._client.models.generate_content(
            model=self.model,
            contents=f"{prompt}\n\n---\nТекст документа:\n{document_text}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema=schema,
            ),
        )
        if not response.text:
            raise ValueError("Gemini вернул пустой ответ")
        return json.loads(response.text)
