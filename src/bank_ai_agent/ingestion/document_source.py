"""Чтение папки документов (PDF/txt/csv) в список RawDocument.

TODO: реализовать извлечение текста из PDF (pymupdf), doc_id = хеш содержимого
файла (не имя файла — имена намеренно непрозрачны).
"""

from __future__ import annotations

from pathlib import Path

from bank_ai_agent.core.models import RawDocument


def load_documents(documents_dir: Path) -> list[RawDocument]:
    raise NotImplementedError("TODO: обойти папку, извлечь текст, посчитать doc_id")
