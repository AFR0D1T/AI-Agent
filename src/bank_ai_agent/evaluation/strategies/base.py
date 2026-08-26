"""Порт (интерфейс) для стратегий проверки ковенанта.

Один класс на CovenantTestType. Добавить новый тип проверки = добавить один
класс по этому протоколу + одну строку в evaluation/registry.py — ничего в
остальном пайплайне не меняется (см. PLAN.md, принцип №4).
"""

from __future__ import annotations

from typing import Protocol

from bank_ai_agent.core.models import CovenantDefinition, CovenantResult, Transaction


class CovenantStrategy(Protocol):
    def evaluate(
        self,
        definition: CovenantDefinition,
        transactions: list[Transaction],
    ) -> CovenantResult:
        """Считает status/actual по скорректированному леджеру сценария.
        evidence_txn_id здесь не определяется — это отдельный шаг
        (evaluation/evidence_selector.py), применяемый уже к результату."""
        ...
