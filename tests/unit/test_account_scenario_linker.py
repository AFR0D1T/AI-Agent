"""Заготовка теста: правило scenario_id из txn_id — чистый код, без сети.

TODO: раскрыть после реализации resolution/account_scenario_linker.py.
"""

import pytest

from bank_ai_agent.resolution.account_scenario_linker import scenario_id_from_txn_id


@pytest.mark.skip(reason="TODO: реализовать scenario_id_from_txn_id")
def test_scenario_id_from_txn_id() -> None:
    assert scenario_id_from_txn_id("TXN-P1-0039") == "P1"
    assert scenario_id_from_txn_id("TXN-B4-0001") == "B4"
