"""Адаптер LLMProvider для Google Gemini (free tier, Google AI Studio).

Модель по умолчанию — gemini-2.5-flash: нативно читает PDF, щедрая бесплатная
квота. Реализует core.llm.client.LLMProvider — остальной пайплайн не знает,
что за этим интерфейсом стоит именно Gemini.

TODO: реализовать вызов google-genai SDK, retry через tenacity, парсинг/
валидацию structured output по переданной JSON-схеме.
"""

from __future__ import annotations

from typing import Any


class GeminiProvider:
    def __init__(self, *, model: str = "gemini-2.5-flash", api_key: str | None = None) -> None:
        self.model = model
        self.api_key = api_key

    def extract(
        self,
        *,
        prompt: str,
        schema: dict[str, Any],
        document_text: str,
    ) -> dict[str, Any]:
        raise NotImplementedError("TODO: вызов google-genai SDK")
