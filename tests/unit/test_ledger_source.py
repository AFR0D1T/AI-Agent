"""Чтение CSV-леджера в Transaction[] — чистый код, без сети."""

from pathlib import Path

from bank_ai_agent.ingestion.ledger_source import load_ledger

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_load_ledger_parses_rows(tmp_path: Path) -> None:
    csv_path = tmp_path / "ledger.csv"
    csv_path.write_text(
        "txn_id,date,account_id,counterparty,description,amount,currency\n"
        "TXN-P1-0001,2025-01-01,ACC-7801,Acme LLP,Rent payment,-1234.56,USD\n"
        "TXN-P1-0002,2025-01-02,ACC-7801,Acme LLP,Refund,789.10,EUR\n",
        encoding="utf-8",
    )

    transactions = load_ledger(csv_path)

    assert len(transactions) == 2
    first = transactions[0]
    assert first.txn_id == "TXN-P1-0001"
    assert first.account_id == "ACC-7801"
    assert first.amount == -1234.56
    assert first.currency == "USD"
    assert str(first.date) == "2025-01-01"


def test_load_ledger_treats_empty_amount_as_none(tmp_path: Path) -> None:
    """Реальный датасет содержит строки с пустым amount (напр. TXN-P7-0033) —
    это часть намеренной "грязности", а не ошибка парсинга; загрузка не должна
    падать, пустая сумма должна стать None, а не 0."""
    csv_path = tmp_path / "ledger.csv"
    csv_path.write_text(
        "txn_id,date,account_id,counterparty,description,amount,currency\n"
        "TXN-P7-0033,2025-11-18,ACC-7807,State Revenue Committee,Tax assessment,,USD\n",
        encoding="utf-8",
    )

    transactions = load_ledger(csv_path)

    assert transactions[0].amount is None
