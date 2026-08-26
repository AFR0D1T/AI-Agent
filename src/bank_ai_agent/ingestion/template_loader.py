"""Загрузка шаблона ответа (submission_template.json) в список ячеек,
которые нужно заполнить.

Исходная структура шаблона (порядок ключей, top-level поля team/contact_email/
model) сверяется отдельно на этапе assembly/validator.py — здесь только список
ячеек для остального пайплайна.
"""

from __future__ import annotations

import json
from pathlib import Path

from bank_ai_agent.core.models import AnswerCellKey


def load_answer_cells(template_path: Path) -> list[AnswerCellKey]:
    data = json.loads(template_path.read_text(encoding="utf-8"))
    answers = data.get("answers", {})
    return [
        AnswerCellKey(scenario_id=scenario_id, clause=clause)
        for scenario_id, clauses in answers.items()
        for clause in clauses
    ]
