from bank_ai_agent.core.models import AmountFilter, Transaction
from bank_ai_agent.evaluation.amount import matches, sum_amount


def _txn(
    txn_id: str = "T1",
    description: str = "",
    counterparty: str = "",
    amount: float | None = -100.0,
    category: str | None = None,
    is_related_party: bool = False,
) -> Transaction:
    return Transaction(
        txn_id=txn_id,
        date="2025-01-01",
        account_id="ACC-1",
        counterparty=counterparty,
        description=description,
        amount=amount,
        currency="USD",
        category=category,
        is_related_party=is_related_party,
    )


def test_transaction_without_amount_never_matches() -> None:
    txn = _txn(amount=None)
    assert matches(txn, AmountFilter()) is False


def test_sign_filter() -> None:
    debit = _txn(amount=-50.0)
    credit = _txn(amount=50.0)

    assert matches(debit, AmountFilter(sign="debit")) is True
    assert matches(debit, AmountFilter(sign="credit")) is False
    assert matches(credit, AmountFilter(sign="credit")) is True
    assert matches(credit, AmountFilter(sign="debit")) is False


def test_description_keywords_match_description_or_counterparty_case_insensitive() -> None:
    txn = _txn(description="Electricity bill Q4", counterparty="City Utility Co")
    assert matches(txn, AmountFilter(description_keywords=["TAX"])) is False
    assert matches(txn, AmountFilter(description_keywords=["electricity"])) is True
    assert matches(txn, AmountFilter(description_keywords=["utility"])) is True  # из counterparty


def test_category_from_reclassification_is_searchable() -> None:
    txn = _txn(description="misc payment", counterparty="Foo", category="Operating Expenses")
    assert matches(txn, AmountFilter(description_keywords=["operating expense"])) is True


def test_exclude_keywords_override_description_match() -> None:
    txn = _txn(description="tax refund adjustment")
    filt = AmountFilter(description_keywords=["tax"], exclude_keywords=["refund"])
    assert matches(txn, filt) is False


def test_related_party_only() -> None:
    related = _txn(is_related_party=True)
    unrelated = _txn(is_related_party=False)
    filt = AmountFilter(related_party_only=True)

    assert matches(related, filt) is True
    assert matches(unrelated, filt) is False


def test_sum_amount_uses_absolute_value() -> None:
    transactions = [_txn("T1", amount=-100.0), _txn("T2", amount=50.0), _txn("T3", amount=None)]
    assert sum_amount(transactions, AmountFilter()) == 150.0
