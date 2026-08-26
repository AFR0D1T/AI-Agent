import json
from pathlib import Path

import pytest

from bank_ai_agent.assembly.validator import ValidationError, validate_submission


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


def _write_submission(tmp_path: Path, answers: dict) -> Path:
    path = tmp_path / "submission.json"
    path.write_text(
        json.dumps(
            {
                "team": "t",
                "contact_email": "e@example.com",
                "model": "m",
                "answers": answers,
            }
        ),
        encoding="utf-8",
    )
    return path


def _valid_cell(**overrides) -> dict:
    cell = {"status": "COMPLIANT", "actual": 100.0, "evidence_txn_id": None}
    cell.update(overrides)
    return cell


def test_valid_submission_passes(tmp_path: Path) -> None:
    template_path = _template(tmp_path)
    submission_path = _write_submission(
        tmp_path,
        {"P1": {"6.1": _valid_cell(), "6.2": _valid_cell(actual=50.5, evidence_txn_id="TXN-P1-0001")}},
    )

    validate_submission(template_path, submission_path)  # не должно бросить исключение


def test_missing_scenario_fails(tmp_path: Path) -> None:
    template_path = _template(tmp_path)
    submission_path = _write_submission(tmp_path, {})

    with pytest.raises(ValidationError):
        validate_submission(template_path, submission_path)


def test_extra_clause_fails(tmp_path: Path) -> None:
    template_path = _template(tmp_path)
    submission_path = _write_submission(
        tmp_path,
        {
            "P1": {
                "6.1": _valid_cell(),
                "6.2": _valid_cell(),
                "6.3": _valid_cell(),  # не было в шаблоне
            }
        },
    )

    with pytest.raises(ValidationError):
        validate_submission(template_path, submission_path)


def test_invalid_status_fails(tmp_path: Path) -> None:
    template_path = _template(tmp_path)
    submission_path = _write_submission(
        tmp_path,
        {"P1": {"6.1": _valid_cell(status="compliant"), "6.2": _valid_cell()}},
    )

    with pytest.raises(ValidationError):
        validate_submission(template_path, submission_path)


def test_negative_actual_fails(tmp_path: Path) -> None:
    template_path = _template(tmp_path)
    submission_path = _write_submission(
        tmp_path,
        {"P1": {"6.1": _valid_cell(actual=-5.0), "6.2": _valid_cell()}},
    )

    with pytest.raises(ValidationError):
        validate_submission(template_path, submission_path)


def test_non_numeric_actual_fails(tmp_path: Path) -> None:
    template_path = _template(tmp_path)
    submission_path = _write_submission(
        tmp_path,
        {"P1": {"6.1": _valid_cell(actual="100"), "6.2": _valid_cell()}},
    )

    with pytest.raises(ValidationError):
        validate_submission(template_path, submission_path)


def test_actual_with_too_many_decimals_fails(tmp_path: Path) -> None:
    template_path = _template(tmp_path)
    submission_path = _write_submission(
        tmp_path,
        {"P1": {"6.1": _valid_cell(actual=100.12345), "6.2": _valid_cell()}},
    )

    with pytest.raises(ValidationError):
        validate_submission(template_path, submission_path)


def test_non_string_evidence_fails(tmp_path: Path) -> None:
    template_path = _template(tmp_path)
    submission_path = _write_submission(
        tmp_path,
        {"P1": {"6.1": _valid_cell(evidence_txn_id=123), "6.2": _valid_cell()}},
    )

    with pytest.raises(ValidationError):
        validate_submission(template_path, submission_path)


def test_missing_top_level_key_fails(tmp_path: Path) -> None:
    template_path = _template(tmp_path)
    submission_path = tmp_path / "submission.json"
    submission_path.write_text(
        json.dumps({"team": "t", "contact_email": "e", "answers": {}}), encoding="utf-8"
    )

    with pytest.raises(ValidationError):
        validate_submission(template_path, submission_path)
