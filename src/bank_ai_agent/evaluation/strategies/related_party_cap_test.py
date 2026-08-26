"""Ковенант на связанные стороны: сумма платежей related-party контрагентам
(помеченных в resolution/ledger_adjuster.py по данным KYC) <= порог.
"""

from __future__ import annotations

from bank_ai_agent.core.models import CovenantDefinition, CovenantResult, Transaction


class RelatedPartyCapTestStrategy:
    def evaluate(
        self, definition: CovenantDefinition, transactions: list[Transaction]
    ) -> CovenantResult:
        raise NotImplementedError("TODO")
