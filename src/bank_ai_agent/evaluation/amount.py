"""Общая арифметика для стратегий проверки ковенантов: отбор и суммирование
транзакций по AmountFilter. Один модуль, чтобы логика фильтрации не
дублировалась в каждой стратегии (ratio/absolute_cap/minimum_floor/...).
"""

from __future__ import annotations

from bank_ai_agent.core.models import AmountFilter, Transaction


def _searchable_text(txn: Transaction) -> str:
    parts = [txn.description, txn.counterparty]
    if txn.category:
        parts.append(txn.category)
    return " ".join(parts).lower()


def matches(txn: Transaction, filt: AmountFilter) -> bool:
    if txn.amount is None:
        return False  # без суммы транзакцию нельзя учесть ни в одном агрегате

    if filt.related_party_only and not txn.is_related_party:
        return False

    if filt.sign == "debit" and txn.amount >= 0:
        return False
    if filt.sign == "credit" and txn.amount <= 0:
        return False

    text = _searchable_text(txn)

    if filt.exclude_keywords and any(kw.lower() in text for kw in filt.exclude_keywords):
        return False

    return not (filt.description_keywords and not any(kw.lower() in text for kw in filt.description_keywords))


def matching_transactions(transactions: list[Transaction], filt: AmountFilter) -> list[Transaction]:
    return [txn for txn in transactions if matches(txn, filt)]


def sum_amount(transactions: list[Transaction], filt: AmountFilter) -> float:
    return sum(abs(txn.amount) for txn in transactions if matches(txn, filt))  # type: ignore[arg-type]
