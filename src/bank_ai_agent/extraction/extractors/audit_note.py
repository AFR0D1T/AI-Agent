"""Извлечение Reclassification (переклассификация транзакций) из аудиторских записок.

TODO: промпт extract_audit_note.md -> list[Reclassification], включая признак
is_final (черновик vs финальное заключение — см. PLAN.md, ловушка версий).
"""

from __future__ import annotations

from bank_ai_agent.core.llm.client import LLMProvider
from bank_ai_agent.core.models import ClassifiedDocument, RawDocument, Reclassification


def extract(
    raw: RawDocument, classified: ClassifiedDocument, provider: LLMProvider
) -> list[Reclassification]:
    raise NotImplementedError("TODO")
