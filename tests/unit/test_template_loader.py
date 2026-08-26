"""Загрузка submission_template.json в список ячеек — чистый код, без сети."""

import json
from pathlib import Path

from bank_ai_agent.ingestion.template_loader import load_answer_cells


def test_load_answer_cells(tmp_path: Path) -> None:
    template_path = tmp_path / "submission_template.json"
    template_path.write_text(
        json.dumps(
            {
                "team": "",
                "contact_email": "",
                "model": "",
                "answers": {
                    "P1": {
                        "6.1": {"status": None, "actual": None, "evidence_txn_id": None},
                        "6.2": {"status": None, "actual": None, "evidence_txn_id": None},
                    },
                    "B1": {
                        "6.1": {"status": None, "actual": None, "evidence_txn_id": None},
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    cells = load_answer_cells(template_path)

    assert len(cells) == 3
    pairs = {(cell.scenario_id, cell.clause) for cell in cells}
    assert pairs == {("P1", "6.1"), ("P1", "6.2"), ("B1", "6.1")}
