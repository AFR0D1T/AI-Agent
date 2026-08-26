"""Выбор актуальной версии документа-источника факта (договор, KYC-досье).

Ловушка (см. PLAN.md): в архиве встречаются просроченные редакции —
использовать нужно только текущую. Логика — код, а не LLM: сравнение
effective_date/is_superseded, проставленных classifier-ом (extraction/
classifier.py) на документе-источнике каждого факта.

`_pick_latest_by_key` — общая часть для любого типа факта, у которого есть
`source_doc_id` и некий ключ группировки; `pick_current_covenant_definitions`
и `pick_current_related_party_info` — её применение к конкретным типам,
чтобы не дублировать сравнение дат в двух местах.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from bank_ai_agent.core.models import (
    ClassifiedDocument,
    CovenantDefinition,
    RelatedPartyInfo,
)

T = TypeVar("T")
Key = TypeVar("Key")


def _is_newer(candidate: ClassifiedDocument, current: ClassifiedDocument) -> bool:
    if candidate.effective_date is None:
        return False
    if current.effective_date is None:
        return True
    return candidate.effective_date > current.effective_date


def _pick_latest_by_key(
    items: list[T],
    *,
    key_fn: Callable[[T], Key],
    source_doc_id_fn: Callable[[T], str],
    classified_by_doc_id: dict[str, ClassifiedDocument],
) -> list[T]:
    best: dict[Key, tuple[T, ClassifiedDocument]] = {}

    for item in items:
        doc = classified_by_doc_id.get(source_doc_id_fn(item))
        if doc is None or doc.is_superseded:
            continue

        key = key_fn(item)
        current = best.get(key)
        if current is None or _is_newer(doc, current[1]):
            best[key] = (item, doc)

    return [item for item, _ in best.values()]


def pick_current_covenant_definitions(
    candidates: list[CovenantDefinition],
    classified_by_doc_id: dict[str, ClassifiedDocument],
) -> list[CovenantDefinition]:
    """Оставляет по каждой паре (account_id, clause) одно определение — из
    самого свежего документа, не помеченного как is_superseded."""
    return _pick_latest_by_key(
        candidates,
        key_fn=lambda c: (c.account_id, c.clause),
        source_doc_id_fn=lambda c: c.source_doc_id,
        classified_by_doc_id=classified_by_doc_id,
    )


def pick_current_related_party_info(
    candidates: list[RelatedPartyInfo],
    classified_by_doc_id: dict[str, ClassifiedDocument],
) -> dict[str, RelatedPartyInfo]:
    """Оставляет по каждому account_id одно (самое свежее, не superseded)
    KYC-досье, возвращает как словарь для быстрого поиска по счёту."""
    picked = _pick_latest_by_key(
        candidates,
        key_fn=lambda c: c.account_id,
        source_doc_id_fn=lambda c: c.source_doc_id,
        classified_by_doc_id=classified_by_doc_id,
    )
    return {item.account_id: item for item in picked}
