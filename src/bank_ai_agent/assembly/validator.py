"""Строгая валидация submission.json перед отправкой.

Обязательный гейт (см. PLAN.md/CASE.ru.md): ключи должны совпадать 1-в-1 с
submission_template.json (ничего не добавлено/переименовано/пропущено),
status ровно "COMPLIANT"/"BREACH", actual — положительное число (округлённое
до 2 знаков после запятой), evidence_txn_id — строка или null. Нарушение
любого из этих правил обнуляет соответствующую ячейку при оценке — лучше
поймать это здесь, чем на приёмке.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_TOP_LEVEL_KEYS = {"team", "contact_email", "model", "answers"}
_CELL_KEYS = {"status", "actual", "evidence_txn_id"}
_VALID_STATUSES = {"COMPLIANT", "BREACH"}


class ValidationError(Exception):
    pass


def validate_submission(template_path: Path, submission_path: Path) -> None:
    template = json.loads(template_path.read_text(encoding="utf-8"))
    submission = json.loads(submission_path.read_text(encoding="utf-8"))

    if set(submission.keys()) != _TOP_LEVEL_KEYS:
        raise ValidationError(
            f"Верхнеуровневые ключи submission не совпадают с шаблоном: {sorted(submission.keys())}"
        )

    template_answers = template.get("answers", {})
    submission_answers = submission.get("answers", {})

    if set(submission_answers) != set(template_answers):
        raise ValidationError(
            "Набор scenario_id в submission.answers не совпадает с шаблоном "
            f"(шаблон: {sorted(template_answers)}, submission: {sorted(submission_answers)})"
        )

    for scenario_id, template_clauses in template_answers.items():
        submission_clauses = submission_answers[scenario_id]
        if set(submission_clauses) != set(template_clauses):
            raise ValidationError(
                f"{scenario_id}: набор пунктов ковенанта не совпадает с шаблоном "
                f"(шаблон: {sorted(template_clauses)}, submission: {sorted(submission_clauses)})"
            )

        for clause, cell in submission_clauses.items():
            _validate_cell(scenario_id, clause, cell)


def _validate_cell(scenario_id: str, clause: str, cell: Any) -> None:
    label = f"{scenario_id}/{clause}"

    if not isinstance(cell, dict) or set(cell.keys()) != _CELL_KEYS:
        raise ValidationError(f"{label}: неверный набор полей ячейки: {cell!r}")

    status = cell["status"]
    if status not in _VALID_STATUSES:
        raise ValidationError(f"{label}: status должен быть COMPLIANT/BREACH, получено {status!r}")

    actual = cell["actual"]
    if isinstance(actual, bool) or not isinstance(actual, int | float):
        raise ValidationError(f"{label}: actual должен быть числом, получено {actual!r}")
    if actual < 0:
        raise ValidationError(f"{label}: actual должен быть положительным, получено {actual!r}")
    if round(actual, 2) != actual:
        raise ValidationError(f"{label}: actual должен быть округлён до 2 знаков, получено {actual!r}")

    evidence = cell["evidence_txn_id"]
    if evidence is not None and not isinstance(evidence, str):
        raise ValidationError(
            f"{label}: evidence_txn_id должен быть строкой или null, получено {evidence!r}"
        )
