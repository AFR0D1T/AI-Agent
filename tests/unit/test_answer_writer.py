import json
from pathlib import Path

from bank_ai_agent.assembly.answer_writer import write_submission
from bank_ai_agent.core.models import AnswerCellKey, CovenantResult


def _template(tmp_path: Path) -> Path:
    path = tmp_path / "submission_template.json"
    path.write_text(
        json.dumps(
            {
                "team": "",
                "contact_email": "",
                "model": "",
                "answers": {
                    "P1": {
                        "6.1": {"status": None, "actual": None, "evidence_txn_id": None},
                        "6.2": {"status": None, "actual": None, "evidence_txn_id": None},
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    return path


def test_write_submission_fills_known_cells_and_leaves_missing_as_null(tmp_path: Path) -> None:
    template_path = _template(tmp_path)
    output_path = tmp_path / "submission.json"

    results = {
        AnswerCellKey(scenario_id="P1", clause="6.1"): CovenantResult(
            status="COMPLIANT", actual=1850000.0, evidence_txn_id=None
        ),
        # 6.2 намеренно не посчитан — должен остаться null, а не отсутствовать
    }

    write_submission(
        template_path,
        output_path,
        results,
        team="my-team",
        contact_email="me@example.com",
        model="gemini-2.5-flash",
    )

    written = json.loads(output_path.read_text(encoding="utf-8"))
    assert written["team"] == "my-team"
    assert written["contact_email"] == "me@example.com"
    assert written["model"] == "gemini-2.5-flash"
    assert written["answers"]["P1"]["6.1"] == {
        "status": "COMPLIANT",
        "actual": 1850000.0,
        "evidence_txn_id": None,
    }
    assert written["answers"]["P1"]["6.2"] == {
        "status": None,
        "actual": None,
        "evidence_txn_id": None,
    }
