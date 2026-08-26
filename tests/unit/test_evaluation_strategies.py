import pytest

from bank_ai_agent.core.models import (
    AmountFilter,
    CovenantDefinition,
    CovenantStatus,
    Transaction,
)
from bank_ai_agent.evaluation.strategies.absolute_cap_test import (
    AbsoluteCapTestStrategy,
)
from bank_ai_agent.evaluation.strategies.minimum_floor_test import (
    MinimumFloorTestStrategy,
)
from bank_ai_agent.evaluation.strategies.ratio_test import RatioTestStrategy
from bank_ai_agent.evaluation.strategies.related_party_cap_test import (
    RelatedPartyCapTestStrategy,
)


def _txn(
    txn_id: str, amount: float, description: str = "", counterparty: str = "", is_related_party: bool = False
) -> Transaction:
    return Transaction(
        txn_id=txn_id,
        date="2025-01-01",
        account_id="ACC-1",
        counterparty=counterparty,
        description=description,
        amount=amount,
        currency="USD",
        is_related_party=is_related_party,
    )


def _definition(**overrides) -> CovenantDefinition:
    base = {
        "account_id": "ACC-1",
        "clause": "6.1",
        "test_type": "absolute_cap",
        "threshold": 100.0,
        "source_doc_id": "doc-1",
        "raw_text": "...",
    }
    base.update(overrides)
    return CovenantDefinition(**base)


class TestRatioTestStrategy:
    def test_compliant_when_ratio_at_or_below_threshold(self) -> None:
        definition = _definition(
            test_type="ratio",
            threshold=0.5,
            numerator=AmountFilter(description_keywords=["tax"], sign="debit"),
            denominator=AmountFilter(description_keywords=["ebitda"], sign="credit"),
        )
        transactions = [
            _txn("T1", -50.0, description="tax payment"),
            _txn("T2", 100.0, description="ebitda proxy revenue"),
        ]

        result = RatioTestStrategy().evaluate(definition, transactions)

        assert result.status == CovenantStatus.COMPLIANT
        assert result.actual == 0.5

    def test_breach_when_ratio_above_threshold(self) -> None:
        definition = _definition(
            test_type="ratio",
            threshold=0.3,
            numerator=AmountFilter(description_keywords=["tax"], sign="debit"),
            denominator=AmountFilter(description_keywords=["ebitda"], sign="credit"),
        )
        transactions = [
            _txn("T1", -50.0, description="tax payment"),
            _txn("T2", 100.0, description="ebitda proxy revenue"),
        ]

        result = RatioTestStrategy().evaluate(definition, transactions)

        assert result.status == CovenantStatus.BREACH

    def test_missing_numerator_denominator_raises(self) -> None:
        definition = _definition(test_type="ratio", threshold=0.3)
        with pytest.raises(ValueError):
            RatioTestStrategy().evaluate(definition, [])

    def test_zero_denominator_raises(self) -> None:
        definition = _definition(
            test_type="ratio",
            threshold=0.3,
            numerator=AmountFilter(description_keywords=["tax"]),
            denominator=AmountFilter(description_keywords=["nonexistent"]),
        )
        with pytest.raises(ValueError):
            RatioTestStrategy().evaluate(definition, [_txn("T1", -50.0, description="tax")])


class TestAbsoluteCapTestStrategy:
    def test_compliant_at_or_below_threshold(self) -> None:
        definition = _definition(
            test_type="absolute_cap", threshold=100.0, aggregate=AmountFilter(sign="debit")
        )
        result = AbsoluteCapTestStrategy().evaluate(definition, [_txn("T1", -100.0)])
        assert result.status == CovenantStatus.COMPLIANT
        assert result.actual == 100.0

    def test_breach_above_threshold(self) -> None:
        definition = _definition(
            test_type="absolute_cap", threshold=100.0, aggregate=AmountFilter(sign="debit")
        )
        result = AbsoluteCapTestStrategy().evaluate(definition, [_txn("T1", -150.0)])
        assert result.status == CovenantStatus.BREACH

    def test_missing_aggregate_raises(self) -> None:
        definition = _definition(test_type="absolute_cap", threshold=100.0)
        with pytest.raises(ValueError):
            AbsoluteCapTestStrategy().evaluate(definition, [])


class TestMinimumFloorTestStrategy:
    def test_compliant_at_or_above_threshold(self) -> None:
        definition = _definition(
            test_type="minimum_floor", threshold=100.0, aggregate=AmountFilter(sign="credit")
        )
        result = MinimumFloorTestStrategy().evaluate(definition, [_txn("T1", 150.0)])
        assert result.status == CovenantStatus.COMPLIANT

    def test_breach_below_threshold(self) -> None:
        definition = _definition(
            test_type="minimum_floor", threshold=100.0, aggregate=AmountFilter(sign="credit")
        )
        result = MinimumFloorTestStrategy().evaluate(definition, [_txn("T1", 50.0)])
        assert result.status == CovenantStatus.BREACH


class TestRelatedPartyCapTestStrategy:
    def test_forces_related_party_filter_even_if_aggregate_did_not_set_it(self) -> None:
        definition = _definition(
            test_type="related_party_cap", threshold=100.0, aggregate=AmountFilter()
        )
        transactions = [
            _txn("T1", -80.0, is_related_party=True),
            _txn("T2", -500.0, is_related_party=False),  # не связанная сторона — не должна учитываться
        ]

        result = RelatedPartyCapTestStrategy().evaluate(definition, transactions)

        assert result.actual == 80.0
        assert result.status == CovenantStatus.COMPLIANT
