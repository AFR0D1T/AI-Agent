"""Связка account_id <-> scenario_id через префикс txn_id. Чистый код, без LLM.

Правило (см. CASE.ru.md): scenario_id — это часть txn_id между "TXN-" и
следующим "-", например TXN-P1-0039 -> scenario_id "P1". Каждый account_id
соответствует ровно одному scenario_id.
"""

from __future__ import annotations

from bank_ai_agent.core.models import Scenario, Transaction


def scenario_id_from_txn_id(txn_id: str) -> str:
    parts = txn_id.split("-")
    if len(parts) < 3 or parts[0] != "TXN":
        raise ValueError(f"Некорректный формат txn_id: {txn_id!r}, ожидался TXN-<scenario_id>-<seq>")
    return parts[1]


def build_scenarios(
    transactions: list[Transaction], target_scenario_ids: list[str]
) -> dict[str, Scenario]:
    """Группирует транзакции по scenario_id, оставляя только целевые сценарии
    из шаблона ответа (остальные account_id — шумовые, отбрасываются)."""
    target = set(target_scenario_ids)
    scenarios: dict[str, Scenario] = {}

    for txn in transactions:
        scenario_id = scenario_id_from_txn_id(txn.txn_id)
        if scenario_id not in target:
            continue

        scenario = scenarios.get(scenario_id)
        if scenario is None:
            scenario = Scenario(scenario_id=scenario_id)
            scenarios[scenario_id] = scenario

        if txn.account_id not in scenario.account_ids:
            scenario.account_ids.append(txn.account_id)
        scenario.transactions.append(txn)

    return scenarios
