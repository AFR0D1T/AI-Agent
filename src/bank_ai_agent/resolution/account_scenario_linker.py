"""Связка account_id <-> scenario_id через префикс txn_id. Чистый код, без LLM.

Правило (см. CASE.ru.md): scenario_id — это часть txn_id между "TXN-" и
следующим "-", например TXN-P1-0039 -> scenario_id "P1". Каждый account_id
соответствует ровно одному scenario_id.
"""

from __future__ import annotations

from bank_ai_agent.core.models import Scenario, Transaction


def scenario_id_from_txn_id(txn_id: str) -> str:
    raise NotImplementedError("TODO: txn_id.split('-')[1]")


def build_scenarios(
    transactions: list[Transaction], target_scenario_ids: list[str]
) -> dict[str, Scenario]:
    """Группирует транзакции по scenario_id, оставляя только целевые сценарии
    из шаблона ответа (остальные account_id — шумовые, отбрасываются)."""
    raise NotImplementedError("TODO")
