"""Порт (интерфейс) для LLM-провайдера.

Ядро и все стадии пайплайна зависят только от этого протокола, а не от
конкретного SDK (Gemini/Anthropic/...). Конкретный адаптер выбирается конфигом
кейса (config/cases/<case>/case.yaml, секция llm) через `get_provider`.
"""

from __future__ import annotations

from typing import Any, Protocol

from bank_ai_agent.core.cache import LLMCache, make_cache_key


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
        по инструкции `prompt`. Реализация отвечает за retry — вызывающий код
        получает либо валидный dict, либо исключение.
        """
        ...


class CachingLLMProvider:
    """Декоратор над LLMProvider: прозрачно кэширует ответы по (prompt, document_text).

    Сам по себе реализует тот же протокол LLMProvider, поэтому classifier/
    extractors не знают, обёрнут провайдер в кэш или нет.
    """

    def __init__(self, inner: LLMProvider, cache: LLMCache) -> None:
        self._inner = inner
        self._cache = cache

    def extract(
        self,
        *,
        prompt: str,
        schema: dict[str, Any],
        document_text: str,
    ) -> dict[str, Any]:
        key = make_cache_key(document_text=document_text, prompt=prompt)
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        result = self._inner.extract(prompt=prompt, schema=schema, document_text=document_text)
        self._cache.set(key, result)
        return result


def get_provider(name: str, *, model: str, api_key: str | None = None) -> LLMProvider:
    """Фабрика адаптеров по имени из конфига кейса (например "gemini").

    Импорт конкретного адаптера — внутри ветки, а не на уровне модуля: core
    не должен требовать установленный SDK провайдера, который не используется.
    """
    if name == "gemini":
        from bank_ai_agent.core.llm.providers.gemini import GeminiProvider

        return GeminiProvider(model=model, api_key=api_key)

    raise ValueError(f"Неизвестный LLM-провайдер: {name!r}")
