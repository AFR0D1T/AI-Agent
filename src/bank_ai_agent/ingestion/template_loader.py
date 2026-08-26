"""Загрузка шаблона ответа (submission_template.json) в список ячеек,
которые нужно заполнить.

TODO: реализовать парсинг шаблона -> list[AnswerCellKey], сохранив исходную
структуру шаблона для последующей строгой сверки в assembly/validator.py.
"""

from __future__ import annotations

from pathlib import Path

from bank_ai_agent.core.models import AnswerCellKey


def load_answer_cells(template_path: Path) -> list[AnswerCellKey]:
    raise NotImplementedError("TODO: json.load -> обойти answers[scenario_id][clause]")
