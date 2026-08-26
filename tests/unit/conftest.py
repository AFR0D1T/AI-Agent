"""Общие фикстуры для unit-тестов."""

from __future__ import annotations

from typing import Any

import pytest


class FakeLLMProvider:
    """Реализует core.llm.client.LLMProvider, возвращает заранее заданный dict.

    Позволяет тестировать classifier/экстракторы без сети и без реального
    provider-адаптера (Gemini и т.п.).
    """

    def __init__(self, response: dict[str, Any]) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []

    def extract(self, *, prompt: str, schema: dict[str, Any], document_text: str) -> dict[str, Any]:
        self.calls.append({"prompt": prompt, "schema": schema, "document_text": document_text})
        return self.response


@pytest.fixture
def fake_provider():
    return FakeLLMProvider
