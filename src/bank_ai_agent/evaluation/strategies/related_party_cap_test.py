"""Ковенант на связанные стороны: сумма платежей related-party контрагентам
(помеченных в resolution/ledger_adjuster.py по данным KYC) <= threshold.

related_party_only форсируется в true независимо от того, что вернул LLM в
definition.aggregate — сам тип ковенанта уже подразумевает эту фильтрацию,
дублировать её в промпте не нужно.
"""

from __future__ import annotations

from bank_ai_agent.core.models import (
    AmountFilter,
    CovenantDefinition,
    CovenantResult,
    CovenantStatus,
    Transaction,
)
from bank_ai_agent.evaluation.amount import sum_amount


class RelatedPartyCapTestStrategy:
    def evaluate(
        self, definition: CovenantDefinition, transactions: list[Transaction]
    ) -> CovenantResult:
        base = definition.aggregate or AmountFilter()
        filt = base.model_copy(update={"related_party_only": True})

        actual = sum_amount(transactions, filt)
        status = (
            CovenantStatus.COMPLIANT if actual <= definition.threshold else CovenantStatus.BREACH
        )
        return CovenantResult(status=status, actual=round(actual, 2))
