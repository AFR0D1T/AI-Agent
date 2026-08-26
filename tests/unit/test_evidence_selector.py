from bank_ai_agent.core.models import AmountFilter, CovenantDefinition, Transaction
from bank_ai_agent.evaluation.evidence_selector import select_evidence
from bank_ai_agent.evaluation.strategies.absolute_cap_test import (
    AbsoluteCapTestStrategy,
)


def _txn(txn_id: str, amount: float) -> Transaction:
    return Transaction(
        txn_id=txn_id,
        date="2025-01-01",
        account_id="ACC-1",
        counterparty="Foo",
        description="payment",
        amount=amount,
        currency="USD",
    )


def _definition(threshold: float) -> CovenantDefinition:
    return CovenantDefinition(
        account_id="ACC-1",
        clause="6.3",
        test_type="absolute_cap",
        threshold=threshold,
        source_doc_id="doc-1",
        raw_text="...",
        aggregate=AmountFilter(sign="debit"),
    )


def test_single_dominant_transaction_is_identified_as_evidence() -> None:
    # Порог 100: без T2 (-80) сумма = 20 (compliant), с T2 = 100 -> ровно на
    # границе (compliant), сделаем T2 достаточно большим, чтобы реально пробить.
    definition = _definition(threshold=50.0)
    transactions = [_txn("T1", -20.0), _txn("T2", -80.0)]  # сумма = 100 > 50 -> BREACH
    strategy = AbsoluteCapTestStrategy()
    result = strategy.evaluate(definition, transactions)

    evidence = select_evidence(definition, transactions, result, strategy)

    assert evidence == "T2"  # без T2 сумма = 20 <= 50 -> COMPLIANT, вердикт меняется


def test_no_single_transaction_flips_verdict_returns_none() -> None:
    definition = _definition(threshold=1000.0)
    transactions = [_txn("T1", -20.0), _txn("T2", -30.0)]  # сумма = 50, далеко от порога
    strategy = AbsoluteCapTestStrategy()
    result = strategy.evaluate(definition, transactions)

    evidence = select_evidence(definition, transactions, result, strategy)

    assert evidence is None


def test_multiple_transactions_each_individually_flip_returns_none() -> None:
    # Порог 50: сумма = 60 (BREACH). Удаление T1 (-40) -> 20 (COMPLIANT).
    # Удаление T2 (-20) -> 40 (COMPLIANT). Обе меняют вердикт -> неоднозначно -> None.
    definition = _definition(threshold=50.0)
    transactions = [_txn("T1", -40.0), _txn("T2", -20.0)]
    strategy = AbsoluteCapTestStrategy()
    result = strategy.evaluate(definition, transactions)

    evidence = select_evidence(definition, transactions, result, strategy)

    assert evidence is None
