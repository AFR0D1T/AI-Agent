"""Ковенант-коэффициент: X / Y <= порог (например (Налоги+Коммуналка)/EBITDA).

TODO: реализовать конкретную формулу(-ы) после того, как зафиксируем полный
набор формулировок из договоров (может понадобиться несколько under-strategies
или параметризация через definition.raw_text/test_type).
"""

from __future__ import annotations

from bank_ai_agent.core.models import CovenantDefinition, CovenantResult, Transaction


class RatioTestStrategy:
    def evaluate(
        self, definition: CovenantDefinition, transactions: list[Transaction]
    ) -> CovenantResult:
        raise NotImplementedError("TODO")
