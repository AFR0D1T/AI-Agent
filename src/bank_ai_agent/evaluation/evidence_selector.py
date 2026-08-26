"""Выбор evidence_txn_id: единственная транзакция, удаление которой меняет вердикт.

Детерминированная проверка (не LLM, см. PLAN.md и CASE.ru.md): для каждой
транзакции скорректированного леджера пересчитывается результат без неё; если
status меняется ровно на одной транзакции — это и есть evidence_txn_id,
иначе None (что и требуется для коэффициентных/агрегатных тестов). Работает
одинаково для любой стратегии — вызывает CovenantStrategy.evaluate как чёрный
ящик, не заглядывая в её внутреннюю логику.
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
    flipping: list[str] = []

    for i, txn in enumerate(transactions):
        remaining = transactions[:i] + transactions[i + 1 :]
        try:
            without_txn = strategy.evaluate(definition, remaining)
        except ValueError:
            continue  # например знаменатель обнулился без этой транзакции — не кандидат

        if without_txn.status != result.status:
            flipping.append(txn.txn_id)

    if len(flipping) == 1:
        return flipping[0]
    return None
