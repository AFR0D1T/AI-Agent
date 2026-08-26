"""Извлечение RelatedPartyInfo (порог владения + связанные контрагенты) из KYC-досье.

TODO: промпт extract_kyc_dossier.md -> RelatedPartyInfo.
"""

from __future__ import annotations

from bank_ai_agent.core.llm.client import LLMProvider
from bank_ai_agent.core.models import ClassifiedDocument, RawDocument, RelatedPartyInfo


def extract(
    raw: RawDocument, classified: ClassifiedDocument, provider: LLMProvider
) -> RelatedPartyInfo:
    raise NotImplementedError("TODO")
