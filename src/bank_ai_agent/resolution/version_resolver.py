"""Выбор актуальной версии документа (договор/аудиторское заключение) на сценарий.

Ловушка (см. PLAN.md): в архиве встречаются просроченные редакции договоров и
черновики аудиторских заключений — использовать нужно только текущую/финальную.
Логика — код, а не LLM: сравнение effective_date / is_superseded / is_final,
проставленных экстракторами на предыдущем шаге.
"""

from __future__ import annotations

from bank_ai_agent.core.models import CovenantDefinition


def pick_current_covenant_definitions(
    candidates: list[CovenantDefinition],
) -> list[CovenantDefinition]:
    raise NotImplementedError("TODO: по scenario_id+clause оставить самую свежую не-superseded")
