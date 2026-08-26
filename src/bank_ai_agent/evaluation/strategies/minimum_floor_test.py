"""Ковенант-минимум: сумма аггрегата >= threshold (например минимальная выручка)."""

from __future__ import annotations

from bank_ai_agent.core.models import (
    CovenantDefinition,
    CovenantResult,
    CovenantStatus,
    Transaction,
)
from bank_ai_agent.evaluation.amount import sum_amount


class MinimumFloorTestStrategy:
    def evaluate(
        self, definition: CovenantDefinition, transactions: list[Transaction]
    ) -> CovenantResult:
        if definition.aggregate is None:
            raise ValueError(f"minimum_floor-ковенант {definition.clause} требует aggregate")

        actual = sum_amount(transactions, definition.aggregate)
        status = (
            CovenantStatus.COMPLIANT if actual >= definition.threshold else CovenantStatus.BREACH
        )
        return CovenantResult(status=status, actual=round(actual, 2))
