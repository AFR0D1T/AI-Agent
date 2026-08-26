"""Ковенант-потолок: сумма X <= порог в валюте (например максимум связанным сторонам)."""

from __future__ import annotations

from bank_ai_agent.core.models import CovenantDefinition, CovenantResult, Transaction


class AbsoluteCapTestStrategy:
    def evaluate(
        self, definition: CovenantDefinition, transactions: list[Transaction]
    ) -> CovenantResult:
        raise NotImplementedError("TODO")
