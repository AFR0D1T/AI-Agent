"""Дешёвый проход классификации: тип документа + кандидат account_id/company.

Отсеивает ~60-70% шумовых документов (см. PLAN.md) до дорогого извлечения.
Промпт (config/prompts/classify_document.md) читает и передаёт вызывающий код
(core/pipeline.py) — сам классификатор чистый и не трогает файловую систему.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from bank_ai_agent.core.llm.client import LLMProvider
from bank_ai_agent.core.llm.schemas import schema_for
from bank_ai_agent.core.models import ClassifiedDocument, DocumentType, RawDocument


class _ClassificationOutput(BaseModel):
    """То, что должен вернуть LLM. Отдельно от ClassifiedDocument: doc_id
    документу присваивает наш код (по хешу содержимого), а не модель."""

    doc_type: DocumentType
    account_id: str | None = None
    company_name: str | None = None
    effective_date: date | None = None
    is_superseded: bool = False
    confidence: float = Field(ge=0.0, le=1.0)


def classify(document: RawDocument, provider: LLMProvider, prompt: str) -> ClassifiedDocument:
    raw_result = provider.extract(
        prompt=prompt,
        schema=schema_for(_ClassificationOutput),
        document_text=document.text,
    )
    parsed = _ClassificationOutput.model_validate(raw_result)
    return ClassifiedDocument(doc_id=document.doc_id, **parsed.model_dump())
