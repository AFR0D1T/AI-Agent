"""Строгая валидация submission.json перед отправкой.

Обязательный гейт (см. PLAN.md/CASE.ru.md): ключи должны совпадать 1-в-1 с
submission_template.json (ничего не добавлено/переименовано/пропущено),
status ровно "COMPLIANT"/"BREACH", actual — положительное число с 2 знаками
после запятой, evidence_txn_id — строка или null.
"""

from __future__ import annotations

from pathlib import Path


class ValidationError(Exception):
    pass


def validate_submission(template_path: Path, submission_path: Path) -> None:
    raise NotImplementedError("TODO")
