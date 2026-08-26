from bank_ai_agent.core.models import DocumentType, RawDocument
from bank_ai_agent.extraction.classifier import classify


def test_classify_builds_classified_document_from_llm_output(fake_provider) -> None:
    provider = fake_provider(
        {
            "doc_type": "loan_agreement",
            "account_id": "ACC-7801",
            "company_name": "Acme LLP",
            "effective_date": "2025-01-01",
            "is_superseded": False,
            "confidence": 0.95,
        }
    )
    raw = RawDocument(doc_id="doc-1", source_path="a.pdf", text="Статья 6. Ковенанты...")

    result = classify(raw, provider, prompt="classify this")

    assert result.doc_id == "doc-1"
    assert result.doc_type == DocumentType.LOAN_AGREEMENT
    assert result.account_id == "ACC-7801"
    assert result.is_superseded is False
    assert result.confidence == 0.95
    assert provider.calls[0]["document_text"] == raw.text
