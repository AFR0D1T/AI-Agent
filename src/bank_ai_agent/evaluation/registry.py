"""Реестр: CovenantTestType -> CovenantStrategy.

Единственное место, которое нужно поправить при добавлении/удалении типа
проверки ковенанта — сам пайплайн (evaluation-стадия) обращается только сюда.
"""

from __future__ import annotations

from bank_ai_agent.core.models import CovenantTestType
from bank_ai_agent.evaluation.strategies.absolute_cap_test import AbsoluteCapTestStrategy
from bank_ai_agent.evaluation.strategies.base import CovenantStrategy
from bank_ai_agent.evaluation.strategies.minimum_floor_test import MinimumFloorTestStrategy
from bank_ai_agent.evaluation.strategies.ratio_test import RatioTestStrategy
from bank_ai_agent.evaluation.strategies.related_party_cap_test import (
    RelatedPartyCapTestStrategy,
)

_REGISTRY: dict[CovenantTestType, CovenantStrategy] = {
    CovenantTestType.RATIO: RatioTestStrategy(),
    CovenantTestType.ABSOLUTE_CAP: AbsoluteCapTestStrategy(),
    CovenantTestType.MINIMUM_FLOOR: MinimumFloorTestStrategy(),
    CovenantTestType.RELATED_PARTY_CAP: RelatedPartyCapTestStrategy(),
}


def get_strategy(test_type: CovenantTestType) -> CovenantStrategy:
    try:
        return _REGISTRY[test_type]
    except KeyError as exc:
        raise ValueError(f"Нет стратегии для test_type={test_type!r}") from exc
