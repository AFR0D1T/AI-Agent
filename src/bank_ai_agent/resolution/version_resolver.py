"""Выбор актуальной версии кредитного договора на (account_id, пункт ковенанта).

Ловушка (см. PLAN.md): в архиве встречаются просроченные редакции договоров —
использовать нужно только текущую. Логика — код, а не LLM: сравнение
effective_date/is_superseded, проставленных classifier-ом (extraction/
classifier.py) на документе-источнике каждого CovenantDefinition.
"""

from __future__ import annotations

from bank_ai_agent.core.models import ClassifiedDocument, CovenantDefinition


def _is_newer(candidate: ClassifiedDocument, current: ClassifiedDocument) -> bool:
    if candidate.effective_date is None:
        return False
    if current.effective_date is None:
        return True
    return candidate.effective_date > current.effective_date


def pick_current_covenant_definitions(
    candidates: list[CovenantDefinition],
    classified_by_doc_id: dict[str, ClassifiedDocument],
) -> list[CovenantDefinition]:
    """Оставляет по каждой паре (account_id, clause) одно определение — из
    самого свежего документа, не помеченного как is_superseded."""
    best: dict[tuple[str, str], tuple[CovenantDefinition, ClassifiedDocument]] = {}

    for covenant in candidates:
        doc = classified_by_doc_id.get(covenant.source_doc_id)
        if doc is None or doc.is_superseded:
            continue

        key = (covenant.account_id, covenant.clause)
        current = best.get(key)
        if current is None or _is_newer(doc, current[1]):
            best[key] = (covenant, doc)

    return [covenant for covenant, _ in best.values()]
