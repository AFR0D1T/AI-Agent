"""Ковенант-коэффициент: numerator / denominator <= threshold
(например (Налоги+Коммуналка)/EBITDA)."""

from __future__ import annotations

from bank_ai_agent.core.models import (
    CovenantDefinition,
    CovenantResult,
    CovenantStatus,
    Transaction,
)
from bank_ai_agent.evaluation.amount import sum_amount


class RatioTestStrategy:
    def evaluate(
        self, definition: CovenantDefinition, transactions: list[Transaction]
    ) -> CovenantResult:
        if definition.numerator is None or definition.denominator is None:
            raise ValueError(
                f"ratio-ковенант {definition.clause} требует numerator и denominator"
            )

        numerator = sum_amount(transactions, definition.numerator)
        denominator = sum_amount(transactions, definition.denominator)
        if denominator == 0:
            raise ValueError(
                f"Знаменатель ковенанта {definition.clause} равен нулю — проверка невозможна"
            )

        actual = numerator / denominator
        status = (
            CovenantStatus.COMPLIANT if actual <= definition.threshold else CovenantStatus.BREACH
        )
        return CovenantResult(status=status, actual=round(actual, 2))
