"""Чтение реестра транзакций (CSV) в список Transaction.

Чистый код, без LLM — формат леджера структурирован (см. PLAN.md).
"""

from __future__ import annotations

import csv
from pathlib import Path

from bank_ai_agent.core.models import Transaction


def load_ledger(csv_path: Path) -> list[Transaction]:
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        transactions = []
        for row in reader:
            row = dict(row)
            row["amount"] = row["amount"] or None  # пустая строка -> None, не 0
            transactions.append(Transaction.model_validate(row))
        return transactions
