from bank_ai_agent.core.models import ClassifiedDocument, DocumentType, RawDocument
from bank_ai_agent.extraction.extractors import audit_note, kyc_dossier, loan_agreement


def _classified(**overrides) -> ClassifiedDocument:
    base = {"doc_id": "doc-1", "doc_type": DocumentType.UNKNOWN, "account_id": "ACC-7801"}
    base.update(overrides)
    return ClassifiedDocument(**base)


def _raw(text: str = "some text") -> RawDocument:
    return RawDocument(doc_id="doc-1", source_path="a.pdf", text=text)


def test_loan_agreement_extract_maps_covenants(fake_provider) -> None:
    provider = fake_provider(
        {
            "account_id": "ACC-7801",
            "covenants": [
                {
                    "clause": "6.1",
                    "test_type": "ratio",
                    "threshold": 0.3,
                    "currency": None,
                    "raw_text": "Отношение налогов к EBITDA не должно превышать 0.30",
                },
                {
                    "clause": "6.2",
                    "test_type": "minimum_floor",
                    "threshold": 1500000,
                    "currency": "USD",
                    "raw_text": "Минимальная выручка 1,500,000 USD",
                },
            ],
        }
    )

    result = loan_agreement.extract(_raw(), _classified(), provider, prompt="p")

    assert len(result) == 2
    assert result[0].account_id == "ACC-7801"
    assert result[0].clause == "6.1"
    assert result[0].test_type.value == "ratio"
    assert result[1].currency == "USD"
    assert all(c.source_doc_id == "doc-1" for c in result)


def test_loan_agreement_extract_uses_classified_account_id_when_llm_omits_it(fake_provider) -> None:
    provider = fake_provider({"account_id": None, "covenants": []})

    result = loan_agreement.extract(_raw(), _classified(account_id="ACC-9"), provider, prompt="p")

    assert result == []  # пустой список ковенантов — не падаем на account_id=None у LLM


def test_kyc_dossier_extract(fake_provider) -> None:
    provider = fake_provider(
        {
            "account_id": None,
            "ownership_threshold_pct": 25.0,
            "related_counterparties": ["Bridgeport Consulting Group"],
        }
    )

    result = kyc_dossier.extract(_raw(), _classified(account_id="ACC-7801"), provider, prompt="p")

    assert result.account_id == "ACC-7801"  # взят из classified, раз LLM не назвал
    assert result.ownership_threshold_pct == 25.0
    assert result.related_counterparties == ["Bridgeport Consulting Group"]


def test_audit_note_extract_preserves_is_final(fake_provider) -> None:
    provider = fake_provider(
        {
            "reclassifications": [
                {"txn_id": "TXN-P3-0001", "new_category": "Operating Expenses", "is_final": True},
                {"txn_id": "TXN-P3-0002", "new_category": "Draft Category", "is_final": False},
            ]
        }
    )

    result = audit_note.extract(_raw(), _classified(), provider, prompt="p")

    assert len(result) == 2
    assert result[0].is_final is True
    assert result[1].is_final is False
    assert all(r.source_doc_id == "doc-1" for r in result)
