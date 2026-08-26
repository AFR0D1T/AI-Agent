"""Порт (интерфейс) для экстракторов структурированных фактов из документа.

Один класс на DocumentType (loan_agreement / kyc_dossier / audit_note).
Добавить новый тип документа = добавить один класс по этому протоколу и
зарегистрировать его — остальной пайплайн не меняется.
"""

from __future__ import annotations

from typing import Protocol

from bank_ai_agent.core.llm.client import LLMProvider
from bank_ai_agent.core.models import ClassifiedDocument, RawDocument


class Extractor(Protocol):
    def extract(
        self,
        raw: RawDocument,
        classified: ClassifiedDocument,
        provider: LLMProvider,
    ) -> object:
        """Возвращает типизированный факт (CovenantDefinition / RelatedPartyInfo /
        Reclassification и т.п. из core.models) с проставленным source_doc_id."""
        ...
