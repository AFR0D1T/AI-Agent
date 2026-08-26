"""Интеграционный тест: весь core.pipeline.run() от сырых файлов до
submission.json, без сети — LLM подменён фейком, отвечающим по маркеру в
тексте документа (имитирует и классификацию, и экстракцию по порядку
вызовов). Ловит ошибки стыковки стадий, которые unit-тесты отдельных
модулей не видят.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from bank_ai_agent.core.pipeline import PipelineConfig, run


class RoutingFakeProvider:
    """Каждому "маркеру", встречающемуся в document_text, соответствует
    очередь canned-ответов: первый extract() для этого документа — это
    классификация, второй (если есть) — экстракция."""

    def __init__(self, responses_by_marker: dict[str, list[dict]]) -> None:
        self._responses = responses_by_marker
        self._call_index: dict[str, int] = {}

    def extract(self, *, prompt: str, schema: dict, document_text: str) -> dict:
        marker = next(m for m in self._responses if m in document_text)
        idx = self._call_index.get(marker, 0)
        self._call_index[marker] = idx + 1
        return self._responses[marker][idx]


def _write_case(tmp_path: Path) -> tuple[PipelineConfig, Path]:
    case_dir = tmp_path / "config" / "cases" / "test_case"
    prompts_dir = tmp_path / "config" / "prompts"
    data_dir = tmp_path / "data"
    documents_dir = data_dir / "documents"
    artifacts_dir = tmp_path / "artifacts"

    for d in (case_dir, prompts_dir, documents_dir, artifacts_dir):
        d.mkdir(parents=True, exist_ok=True)

    for name in (
        "classify_document.md",
        "extract_loan_agreement.md",
        "extract_kyc_dossier.md",
        "extract_audit_note.md",
    ):
        (prompts_dir / name).write_text("# stub prompt\n", encoding="utf-8")

    ledger_path = data_dir / "ledger.csv"
    ledger_path.write_text(
        "txn_id,date,account_id,counterparty,description,amount,currency\n"
        "TXN-P1-0001,2025-01-01,ACC-1,Tax Office,Corporate tax payment,-30.0,USD\n"
        "TXN-P1-0002,2025-01-02,ACC-1,Big Client,EBITDA proxy revenue,100.0,USD\n"
        "TXN-P1-0003,2025-01-03,ACC-1,Bridgeport Consulting Group,Consulting fee,-20.0,USD\n",
        encoding="utf-8",
    )

    template_path = data_dir / "submission_template.json"
    template_path.write_text(
        json.dumps(
            {
                "team": "",
                "contact_email": "",
                "model": "",
                "answers": {"P1": {"6.1": {"status": None, "actual": None, "evidence_txn_id": None}}},
            }
        ),
        encoding="utf-8",
    )

    (documents_dir / "loan.txt").write_text("LOAN_DOC Статья 6 ковенанты", encoding="utf-8")
    (documents_dir / "kyc.txt").write_text("KYC_DOC досье комплаенс", encoding="utf-8")
    (documents_dir / "noise.txt").write_text("NOISE_DOC внутренняя переписка", encoding="utf-8")

    case_yaml = {
        "data": {
            "ledger_csv": str(ledger_path),
            "documents_dir": str(documents_dir),
            "submission_template": str(template_path),
        },
        "llm": {"provider": "gemini", "model": "test-model", "api_key_env": "GEMINI_API_KEY"},
        "submission": {"team": "test-team", "contact_email": "test@example.com", "model": "test-model"},
    }
    (case_dir / "case.yaml").write_text(yaml.safe_dump(case_yaml), encoding="utf-8")

    config = PipelineConfig(case_name="test_case", case_dir=case_dir, artifacts_dir=artifacts_dir)
    return config, template_path


def test_pipeline_end_to_end(tmp_path: Path) -> None:
    config, _template_path = _write_case(tmp_path)

    provider = RoutingFakeProvider(
        {
            "LOAN_DOC": [
                {
                    "doc_type": "loan_agreement",
                    "account_id": "ACC-1",
                    "company_name": "Acme",
                    "effective_date": "2025-01-01",
                    "is_superseded": False,
                    "confidence": 0.9,
                },
                {
                    "account_id": "ACC-1",
                    "covenants": [
                        {
                            "clause": "6.1",
                            "test_type": "ratio",
                            "threshold": 0.5,
                            "currency": None,
                            "raw_text": "Tax/EBITDA <= 0.5",
                            "numerator": {
                                "description_keywords": ["tax"],
                                "exclude_keywords": [],
                                "related_party_only": False,
                                "sign": "debit",
                            },
                            "denominator": {
                                "description_keywords": ["ebitda"],
                                "exclude_keywords": [],
                                "related_party_only": False,
                                "sign": "credit",
                            },
                            "aggregate": None,
                        }
                    ],
                },
            ],
            "KYC_DOC": [
                {
                    "doc_type": "kyc_dossier",
                    "account_id": "ACC-1",
                    "company_name": "Acme",
                    "effective_date": "2025-01-01",
                    "is_superseded": False,
                    "confidence": 0.9,
                },
                {
                    "account_id": "ACC-1",
                    "ownership_threshold_pct": 25.0,
                    "related_counterparties": ["Bridgeport Consulting Group"],
                },
            ],
            "NOISE_DOC": [
                {
                    "doc_type": "noise",
                    "account_id": None,
                    "company_name": None,
                    "effective_date": None,
                    "is_superseded": False,
                    "confidence": 0.99,
                }
            ],
        }
    )

    output_path = run(config, provider=provider)

    assert output_path == config.artifacts_dir / "submission.json"
    submission = json.loads(output_path.read_text(encoding="utf-8"))

    assert submission["team"] == "test-team"
    cell = submission["answers"]["P1"]["6.1"]
    assert cell["status"] == "COMPLIANT"  # 30/100 = 0.3 <= 0.5
    assert cell["actual"] == 0.3
    assert cell["evidence_txn_id"] is None  # ratio-тест — ни одна транзакция не ломает вердикт
