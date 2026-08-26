"""Ковенант-минимум: сумма X >= порог в валюте (например минимальная выручка)."""

from __future__ import annotations

from bank_ai_agent.core.models import CovenantDefinition, CovenantResult, Transaction


class MinimumFloorTestStrategy:
    def evaluate(
        self, definition: CovenantDefinition, transactions: list[Transaction]
    ) -> CovenantResult:
        raise NotImplementedError("TODO")
