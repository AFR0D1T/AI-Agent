"""Извлечение Reclassification (переклассификация транзакций) из аудиторских записок.

Промпт (config/prompts/extract_audit_note.md) читает вызывающий код.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from bank_ai_agent.core.llm.client import LLMProvider
from bank_ai_agent.core.llm.schemas import schema_for
from bank_ai_agent.core.models import ClassifiedDocument, RawDocument, Reclassification


class _ReclassificationItem(BaseModel):
    txn_id: str
    new_category: str
    is_final: bool


class _AuditNoteOutput(BaseModel):
    reclassifications: list[_ReclassificationItem] = Field(default_factory=list)


def extract(
    raw: RawDocument,
    classified: ClassifiedDocument,
    provider: LLMProvider,
    prompt: str,
) -> list[Reclassification]:
    raw_result = provider.extract(
        prompt=prompt,
        schema=schema_for(_AuditNoteOutput),
        document_text=raw.text,
    )
    parsed = _AuditNoteOutput.model_validate(raw_result)

    return [
        Reclassification(
            txn_id=item.txn_id,
            new_category=item.new_category,
            source_doc_id=raw.doc_id,
            is_final=item.is_final,
        )
        for item in parsed.reclassifications
    ]
