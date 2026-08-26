"""Извлечение RelatedPartyInfo (порог владения + связанные контрагенты) из KYC-досье.

Промпт (config/prompts/extract_kyc_dossier.md) читает вызывающий код.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from bank_ai_agent.core.llm.client import LLMProvider
from bank_ai_agent.core.llm.schemas import schema_for
from bank_ai_agent.core.models import ClassifiedDocument, RawDocument, RelatedPartyInfo


class _KycOutput(BaseModel):
    account_id: str | None = None
    ownership_threshold_pct: float
    related_counterparties: list[str] = Field(default_factory=list)


def extract(
    raw: RawDocument,
    classified: ClassifiedDocument,
    provider: LLMProvider,
    prompt: str,
) -> RelatedPartyInfo:
    raw_result = provider.extract(
        prompt=prompt,
        schema=schema_for(_KycOutput),
        document_text=raw.text,
    )
    parsed = _KycOutput.model_validate(raw_result)

    account_id = classified.account_id or parsed.account_id
    if account_id is None:
        raise ValueError(f"Не удалось определить account_id для KYC-досье (doc_id={raw.doc_id})")

    return RelatedPartyInfo(
        account_id=account_id,
        ownership_threshold_pct=parsed.ownership_threshold_pct,
        related_counterparties=parsed.related_counterparties,
        source_doc_id=raw.doc_id,
    )
