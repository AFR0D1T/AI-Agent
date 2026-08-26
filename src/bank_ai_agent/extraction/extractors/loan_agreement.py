"""Извлечение CovenantDefinition из текста кредитного договора (Статья 6).

TODO: промпт extract_loan_agreement.md -> list[CovenantDefinition] (по одному
на пункт 6.1/6.2/6.3), включая test_type, threshold, currency, is_superseded
(признак устаревшей редакции остаётся на стороне classifier/version_resolver).
"""

from __future__ import annotations

from bank_ai_agent.core.llm.client import LLMProvider
from bank_ai_agent.core.models import ClassifiedDocument, CovenantDefinition, RawDocument


def extract(
    raw: RawDocument, classified: ClassifiedDocument, provider: LLMProvider
) -> list[CovenantDefinition]:
    raise NotImplementedError("TODO")
