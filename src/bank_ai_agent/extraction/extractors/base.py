"""Порт (интерфейс) для экстракторов структурированных фактов из документа.

Один класс/функция на DocumentType (loan_agreement / kyc_dossier / audit_note).
Добавить новый тип документа = добавить один модуль по этому протоколу и
зарегистрировать его в extraction-стадии пайплайна — остальной пайплайн не
меняется. Промпт передаётся явно (загружается вызывающим кодом), чтобы сам
экстрактор оставался чистой функцией без файлового I/O.
"""

from __future__ import annotations

from typing import Protocol

from bank_ai_agent.core.llm.client import LLMProvider
from bank_ai_agent.core.models import ClassifiedDocument, RawDocument


class Extractor(Protocol):
    def __call__(
        self,
        raw: RawDocument,
        classified: ClassifiedDocument,
        provider: LLMProvider,
        prompt: str,
    ) -> object:
        """Возвращает типизированный факт (CovenantDefinition / RelatedPartyInfo /
        Reclassification и т.п. из core.models, либо список таких фактов) с
        проставленным source_doc_id."""
        ...
