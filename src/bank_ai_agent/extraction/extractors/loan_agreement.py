"""Извлечение CovenantDefinition из текста кредитного договора (Статья 6).

Промпт (config/prompts/extract_loan_agreement.md) читает вызывающий код.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from bank_ai_agent.core.llm.client import LLMProvider
from bank_ai_agent.core.llm.schemas import schema_for
from bank_ai_agent.core.models import (
    AmountFilter,
    ClassifiedDocument,
    CovenantDefinition,
    CovenantTestType,
    RawDocument,
)


class _CovenantItem(BaseModel):
    clause: str
    test_type: CovenantTestType
    threshold: float
    currency: str | None = None
    raw_text: str
    numerator: AmountFilter | None = None
    denominator: AmountFilter | None = None
    aggregate: AmountFilter | None = None


class _LoanAgreementOutput(BaseModel):
    account_id: str | None = None
    covenants: list[_CovenantItem] = Field(default_factory=list)


def extract(
    raw: RawDocument,
    classified: ClassifiedDocument,
    provider: LLMProvider,
    prompt: str,
) -> list[CovenantDefinition]:
    raw_result = provider.extract(
        prompt=prompt,
        schema=schema_for(_LoanAgreementOutput),
        document_text=raw.text,
    )
    parsed = _LoanAgreementOutput.model_validate(raw_result)

    account_id = classified.account_id or parsed.account_id
    if account_id is None:
        raise ValueError(f"Не удалось определить account_id для договора (doc_id={raw.doc_id})")

    return [
        CovenantDefinition(
            account_id=account_id,
            clause=item.clause,
            test_type=item.test_type,
            threshold=item.threshold,
            currency=item.currency,
            source_doc_id=raw.doc_id,
            raw_text=item.raw_text,
            numerator=item.numerator,
            denominator=item.denominator,
            aggregate=item.aggregate,
        )
        for item in parsed.covenants
    ]
