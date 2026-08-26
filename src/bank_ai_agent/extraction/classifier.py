"""Дешёвый проход классификации: тип документа + кандидат account_id/company.

Отсеивает ~60-70% шумовых документов (см. PLAN.md) до дорогого извлечения.
TODO: промпт classify_document.md + LLMProvider.extract -> ClassifiedDocument.
"""

from __future__ import annotations

from bank_ai_agent.core.llm.client import LLMProvider
from bank_ai_agent.core.models import ClassifiedDocument, RawDocument


def classify(document: RawDocument, provider: LLMProvider) -> ClassifiedDocument:
    raise NotImplementedError("TODO: LLM-классификация по config/prompts/classify_document.md")
