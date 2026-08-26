"""Заполнение submission.json по структуре submission_template.json.

Загружает исходный шаблон как есть (сохраняя его структуру и порядок ключей),
подставляет CovenantResult в соответствующие answers[scenario_id][clause] и
записывает team/contact_email/model. Ячейки, для которых нет результата,
остаются как в шаблоне (null) — их отловит assembly/validator.py.
"""

from __future__ import annotations

import json
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
    template = json.loads(template_path.read_text(encoding="utf-8"))

    for scenario_id, clauses in template.get("answers", {}).items():
        for clause in clauses:
            result = results.get(AnswerCellKey(scenario_id=scenario_id, clause=clause))
            if result is None:
                continue
            clauses[clause] = {
                "status": result.status.value,
                "actual": result.actual,
                "evidence_txn_id": result.evidence_txn_id,
            }

    template["team"] = team
    template["contact_email"] = contact_email
    template["model"] = model

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")
