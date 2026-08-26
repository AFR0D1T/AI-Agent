"""Применение реклассификаций и меток related-party к транзакциям сценария.

Собирает "скорректированный леджер" на сценарий: транзакции с применёнными
финальными (is_final=True) переклассификациями аудиторов и флагом
is_related_party там, где контрагент входит в related_counterparties из KYC.
"""

from __future__ import annotations

from bank_ai_agent.core.models import Reclassification, RelatedPartyInfo, Transaction


def adjust(
    transactions: list[Transaction],
    reclassifications: list[Reclassification],
    related_party_info: RelatedPartyInfo | None,
) -> list[Transaction]:
    raise NotImplementedError("TODO")
