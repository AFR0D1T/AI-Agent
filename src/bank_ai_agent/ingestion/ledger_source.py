"""Чтение реестра транзакций (CSV) в список Transaction.

Чистый код, без LLM — формат леджера структурирован (см. PLAN.md).
TODO: реализовать чтение CSV -> list[Transaction] (пути к файлу — из case.yaml).
"""

from __future__ import annotations

from pathlib import Path

from bank_ai_agent.core.models import Transaction


def load_ledger(csv_path: Path) -> list[Transaction]:
    raise NotImplementedError("TODO: csv.DictReader -> [Transaction(**row) for row in ...]")
