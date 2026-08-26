"""Кэш LLM-вызовов по хешу (документ, промпт).

Экономит вызовы при повторных прогонах и бережёт бесплатную квоту провайдера
(см. PLAN.md, LLM-слой). `FileCache` — единственная реализация порта
`LLMCache` на сейчас: один JSON-файл на ключ на диске.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Protocol


class LLMCache(Protocol):
    def get(self, key: str) -> dict[str, Any] | None: ...

    def set(self, key: str, value: dict[str, Any]) -> None: ...


def make_cache_key(*, document_text: str, prompt: str) -> str:
    """Ключ кэша: хеш от (промпт, текст документа). Не зависит от имени файла
    на диске — только от того, что реально уйдёт в LLM."""
    payload = f"{prompt}\n---\n{document_text}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class FileCache:
    """Простой файловый кэш: cache_dir/<key>.json."""

    def __init__(self, cache_dir: Path) -> None:
        self._dir = cache_dir
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self._dir / f"{key}.json"

    def get(self, key: str) -> dict[str, Any] | None:
        path = self._path(key)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def set(self, key: str, value: dict[str, Any]) -> None:
        self._path(key).write_text(
            json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8"
        )
