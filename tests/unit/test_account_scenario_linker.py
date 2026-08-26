"""Правило scenario_id из txn_id и группировка транзакций по сценарию — чистый
код, без сети."""

import pytest

from bank_ai_agent.core.models import Transaction
from bank_ai_agent.resolution.account_scenario_linker import (
    account_to_scenario_map,
    build_scenarios,
    scenario_id_from_txn_id,
)


def test_scenario_id_from_txn_id() -> None:
    assert scenario_id_from_txn_id("TXN-P1-0039") == "P1"
    assert scenario_id_from_txn_id("TXN-B4-0001") == "B4"
    assert scenario_id_from_txn_id("TXN-9001-0036") == "9001"


def test_scenario_id_from_txn_id_rejects_bad_format() -> None:
    with pytest.raises(ValueError):
        scenario_id_from_txn_id("not-a-txn-id")


def _txn(txn_id: str, account_id: str, amount: float = -100.0) -> Transaction:
    return Transaction(
        txn_id=txn_id,
        date="2025-01-01",
        account_id=account_id,
        counterparty="Someone",
        description="desc",
        amount=amount,
        currency="USD",
    )


def test_build_scenarios_keeps_only_target_ids_and_groups_by_scenario() -> None:
    transactions = [
        _txn("TXN-P1-0001", "ACC-1"),
        _txn("TXN-P1-0002", "ACC-1"),
        _txn("TXN-9001-0001", "ACC-9001"),  # шумовой сценарий, не в target
        _txn("TXN-B4-0001", "ACC-2"),
    ]

    scenarios = build_scenarios(transactions, target_scenario_ids=["P1", "B4"])

    assert set(scenarios) == {"P1", "B4"}
    assert scenarios["P1"].account_ids == ["ACC-1"]
    assert len(scenarios["P1"].transactions) == 2
    assert scenarios["B4"].account_ids == ["ACC-2"]
    assert len(scenarios["B4"].transactions) == 1


def test_account_to_scenario_map() -> None:
    transactions = [_txn("TXN-P1-0001", "ACC-1"), _txn("TXN-B4-0001", "ACC-2")]
    scenarios = build_scenarios(transactions, target_scenario_ids=["P1", "B4"])

    mapping = account_to_scenario_map(scenarios)

    assert mapping == {"ACC-1": "P1", "ACC-2": "B4"}
