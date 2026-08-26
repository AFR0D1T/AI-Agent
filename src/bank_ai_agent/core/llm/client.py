"""Порт (интерфейс) для LLM-провайдера.

Ядро и все стадии пайплайна зависят только от этого протокола, а не от
конкретного SDK (Gemini/Anthropic/...). Конкретный адаптер выбирается конфигом
кейса — см. `core.llm.providers`.
"""

from __future__ import annotations

from typing import Any, Protocol


class LLMProvider(Protocol):
    """Один структурированный вызов: текст документа + промпт + JSON-схема → dict."""

    def extract(
        self,
        *,
        prompt: str,
        schema: dict[str, Any],
        document_text: str,
    ) -> dict[str, Any]:
        """Вернуть данные, соответствующие `schema`, извлечённые из `document_text`
        по инструкции `prompt`. Реализация отвечает за retry и валидацию структуры
        ответа — вызывающий код получает либо валидный dict, либо исключение.
        """
        ...


def get_provider(name: str, *, model: str, api_key: str | None = None) -> LLMProvider:
    """Фабрика адаптеров по имени из конфига кейса (например "gemini").

    TODO: реализовать после того, как определимся с конкретным адаптером
    (см. core/llm/providers/gemini.py).
    """
    raise NotImplementedError("TODO: подключить провайдер по имени из case.yaml")
