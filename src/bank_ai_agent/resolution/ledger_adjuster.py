"""Применение реклассификаций и меток related-party к транзакциям сценария.

Собирает "скорректированный леджер": транзакции с применёнными финальными
(is_final=True; черновики отбрасываются) переклассификациями аудиторов и
флагом is_related_party там, где контрагент входит в related_counterparties
из KYC-досье. Чистый код, без LLM — факты уже извлечены на предыдущих шагах.
"""

from __future__ import annotations

from bank_ai_agent.core.models import Reclassification, RelatedPartyInfo, Transaction


def adjust(
    transactions: list[Transaction],
    reclassifications: list[Reclassification],
    related_party_info: RelatedPartyInfo | None,
) -> list[Transaction]:
    final_category_by_txn_id = {
        reclass.txn_id: reclass.new_category for reclass in reclassifications if reclass.is_final
    }
    related_counterparties = (
        set(related_party_info.related_counterparties) if related_party_info else set()
    )

    adjusted: list[Transaction] = []
    for txn in transactions:
        data = txn.model_dump()
        if txn.txn_id in final_category_by_txn_id:
            data["category"] = final_category_by_txn_id[txn.txn_id]
        if txn.counterparty in related_counterparties:
            data["is_related_party"] = True
        adjusted.append(Transaction.model_validate(data))

    return adjusted
