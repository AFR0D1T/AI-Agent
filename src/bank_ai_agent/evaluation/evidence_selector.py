"""Выбор evidence_txn_id: единственная транзакция, удаление которой меняет вердикт.

Детерминированная проверка (не LLM, см. PLAN.md): для каждой транзакции-
кандидата пересчитывается CovenantResult.status без неё; если status меняется
ровно на одной транзакции — это и есть evidence_txn_id, иначе None (ratio- и
агрегатные тесты по правилам оценки принимают null).
"""

from __future__ import annotations

from bank_ai_agent.core.models import CovenantDefinition, CovenantResult, Transaction
from bank_ai_agent.evaluation.strategies.base import CovenantStrategy


def select_evidence(
    definition: CovenantDefinition,
    transactions: list[Transaction],
    result: CovenantResult,
    strategy: CovenantStrategy,
) -> str | None:
    raise NotImplementedError("TODO")
