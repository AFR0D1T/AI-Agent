from bank_ai_agent.core.models import Reclassification, RelatedPartyInfo, Transaction
from bank_ai_agent.resolution.ledger_adjuster import adjust


def _txn(txn_id: str, counterparty: str, amount: float = -100.0) -> Transaction:
    return Transaction(
        txn_id=txn_id,
        date="2025-01-01",
        account_id="ACC-7801",
        counterparty=counterparty,
        description="desc",
        amount=amount,
        currency="USD",
    )


def test_applies_only_final_reclassifications() -> None:
    transactions = [_txn("TXN-P3-0001", "Foo"), _txn("TXN-P3-0002", "Bar")]
    reclassifications = [
        Reclassification(
            txn_id="TXN-P3-0001", new_category="Operating Expenses", source_doc_id="d1", is_final=True
        ),
        Reclassification(
            txn_id="TXN-P3-0002", new_category="Draft Category", source_doc_id="d2", is_final=False
        ),
    ]

    result = adjust(transactions, reclassifications, related_party_info=None)

    by_id = {t.txn_id: t for t in result}
    assert by_id["TXN-P3-0001"].category == "Operating Expenses"
    assert by_id["TXN-P3-0002"].category is None  # черновик не применён


def test_flags_related_party_counterparties() -> None:
    transactions = [_txn("TXN-1", "Bridgeport Consulting Group"), _txn("TXN-2", "Unrelated Co")]
    related_party_info = RelatedPartyInfo(
        account_id="ACC-7801",
        ownership_threshold_pct=25.0,
        related_counterparties=["Bridgeport Consulting Group"],
        source_doc_id="kyc-1",
    )

    result = adjust(transactions, reclassifications=[], related_party_info=related_party_info)

    by_id = {t.txn_id: t for t in result}
    assert by_id["TXN-1"].is_related_party is True
    assert by_id["TXN-2"].is_related_party is False


def test_does_not_mutate_original_transactions() -> None:
    original = _txn("TXN-1", "Bridgeport Consulting Group")
    related_party_info = RelatedPartyInfo(
        account_id="ACC-7801",
        ownership_threshold_pct=25.0,
        related_counterparties=["Bridgeport Consulting Group"],
        source_doc_id="kyc-1",
    )

    adjust([original], reclassifications=[], related_party_info=related_party_info)

    assert original.is_related_party is False
