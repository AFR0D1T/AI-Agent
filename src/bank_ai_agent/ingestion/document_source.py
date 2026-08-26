"""Чтение папки документов (PDF/txt/csv) в список RawDocument.

doc_id считается от содержимого файла (не от имени — имена намеренно
непрозрачны и не несут смысла, см. CASE.ru.md), чтобы кэш по документу
(core/cache.py) не зависел от того, как файл называется на диске.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from bank_ai_agent.core.models import RawDocument

_TEXT_SUFFIXES = {".txt", ".csv"}


def _extract_pdf_text(path: Path) -> str:
    import pymupdf

    with pymupdf.open(path) as doc:
        return "\n".join(page.get_text() for page in doc)


def load_documents(documents_dir: Path) -> list[RawDocument]:
    documents: list[RawDocument] = []

    for path in sorted(documents_dir.iterdir()):
        if not path.is_file():
            continue

        suffix = path.suffix.lower()
        if suffix == ".pdf":
            text = _extract_pdf_text(path)
        elif suffix in _TEXT_SUFFIXES:
            text = path.read_text(encoding="utf-8", errors="replace")
        else:
            continue  # напр. Thumbs.db — не документ, пропускаем

        doc_id = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
        documents.append(RawDocument(doc_id=doc_id, source_path=str(path), text=text))

    return documents
