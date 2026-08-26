from bank_ai_agent.core.models import (
    ClassifiedDocument,
    CovenantDefinition,
    DocumentType,
)
from bank_ai_agent.resolution.version_resolver import pick_current_covenant_definitions


def _covenant(source_doc_id: str, threshold: float) -> CovenantDefinition:
    return CovenantDefinition(
        account_id="ACC-7801",
        clause="6.1",
        test_type="ratio",
        threshold=threshold,
        currency=None,
        source_doc_id=source_doc_id,
        raw_text="...",
    )


def _doc(doc_id: str, *, effective_date: str | None, is_superseded: bool) -> ClassifiedDocument:
    return ClassifiedDocument(
        doc_id=doc_id,
        doc_type=DocumentType.LOAN_AGREEMENT,
        account_id="ACC-7801",
        effective_date=effective_date,
        is_superseded=is_superseded,
    )


def test_picks_newest_non_superseded_version() -> None:
    old = _covenant("doc-old", threshold=1.05)
    new = _covenant("doc-new", threshold=0.30)
    classified = {
        "doc-old": _doc("doc-old", effective_date="2024-01-01", is_superseded=True),
        "doc-new": _doc("doc-new", effective_date="2025-01-01", is_superseded=False),
    }

    result = pick_current_covenant_definitions([old, new], classified)

    assert len(result) == 1
    assert result[0].threshold == 0.30


def test_ignores_superseded_even_if_dated_later() -> None:
    stale_but_newer_date = _covenant("doc-a", threshold=999)
    current = _covenant("doc-b", threshold=0.30)
    classified = {
        "doc-a": _doc("doc-a", effective_date="2026-01-01", is_superseded=True),
        "doc-b": _doc("doc-b", effective_date="2025-01-01", is_superseded=False),
    }

    result = pick_current_covenant_definitions([stale_but_newer_date, current], classified)

    assert len(result) == 1
    assert result[0].threshold == 0.30


def test_missing_classified_document_is_skipped() -> None:
    orphan = _covenant("doc-missing", threshold=1.0)

    result = pick_current_covenant_definitions([orphan], classified_by_doc_id={})

    assert result == []
