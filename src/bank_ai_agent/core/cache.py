"""Кэш LLM-вызовов по хешу (документ, версия промпта).

Экономит вызовы при повторных прогонах и бережёт бесплатную квоту провайдера.
TODO: реализовать простой файловый кэш (json на диске в artifacts/.cache/,
ключ = sha256(document_text + prompt)).
"""

from __future__ import annotations

from typing import Any, Protocol


class LLMCache(Protocol):
    def get(self, key: str) -> dict[str, Any] | None: ...

    def set(self, key: str, value: dict[str, Any]) -> None: ...
