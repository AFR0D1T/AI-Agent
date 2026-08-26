"""Заполнение submission.json по структуре submission_template.json.

TODO: загрузить исходный шаблон, подставить CovenantResult в соответствующие
answers[scenario_id][clause], записать team/contact_email/model, сохранить файл.
"""

from __future__ import annotations

from pathlib import Path

from bank_ai_agent.core.models import AnswerCellKey, CovenantResult


def write_submission(
    template_path: Path,
    output_path: Path,
    results: dict[AnswerCellKey, CovenantResult],
    *,
    team: str,
    contact_email: str,
    model: str,
) -> None:
    raise NotImplementedError("TODO")
