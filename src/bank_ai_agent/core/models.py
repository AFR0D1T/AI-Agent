"""Кейс-агностичные доменные модели.

Ничего в этом модуле не должно знать о конкретном кейсе (Halyk, PDF-хеши,
пункты 6.1-6.3) — только общие понятия: транзакция, документ, ковенант,
сценарий, ответ.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class Transaction(BaseModel):
    """Одна строка реестра транзакций.

    `amount` может быть `None` — в леджере встречаются строки с пустой суммой
    (часть намеренной "грязности" датасета, не ошибка парсинга). Решение, как
    их трактовать (исключить из агрегатов, искать сумму в документах и т.п.),
    принимается на уровне evaluation-стратегий, а не здесь.
    """

    txn_id: str
    date: date
    account_id: str
    counterparty: str
    description: str
    amount: float | None
    currency: str

    # Проставляются resolution/ledger_adjuster.py поверх сырых данных леджера
    # (не приходят из CSV) — переклассификация аудитора и статус связанной
    # стороны по данным KYC-досье.
    category: str | None = None
    is_related_party: bool = False


class DocumentType(StrEnum):
    """Результат классификации документа. Расширяется под новые кейсы."""

    LOAN_AGREEMENT = "loan_agreement"
    KYC_DOSSIER = "kyc_dossier"
    AUDIT_NOTE = "audit_note"
    NOISE = "noise"
    UNKNOWN = "unknown"


class RawDocument(BaseModel):
    """Сырой документ до классификации/извлечения."""

    doc_id: str  # обычно = хеш содержимого или имя файла
    source_path: str
    text: str


class ClassifiedDocument(BaseModel):
    """Документ после дешёвого прохода классификации."""

    doc_id: str
    doc_type: DocumentType
    account_id: str | None = None
    company_name: str | None = None
    effective_date: date | None = None
    is_superseded: bool = False
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)


class CovenantTestType(StrEnum):
    """Тип проверки ковенанта — определяет, какая стратегия из реестра применяется."""

    RATIO = "ratio"
    ABSOLUTE_CAP = "absolute_cap"
    MINIMUM_FLOOR = "minimum_floor"
    RELATED_PARTY_CAP = "related_party_cap"


class AmountFilter(BaseModel):
    """Критерий отбора транзакций для одного агрегата (числитель/знаменатель/сумма).

    В леджере нет колонки категории — состав "Налоги+Коммуналка", "Выручка" и
    т.п. определяется по вхождению ключевых слов в description/counterparty
    (без учёта регистра), плюс category, если она проставлена реклассификацией
    аудитора (resolution/ledger_adjuster.py). Извлекается LLM из текста
    договора (extraction/extractors/loan_agreement.py) — состав ключевых слов
    для каждого пункта индивидуален, поэтому не зашит в код.
    """

    description_keywords: list[str] = Field(default_factory=list)
    exclude_keywords: list[str] = Field(default_factory=list)
    related_party_only: bool = False
    sign: Literal["debit", "credit", "any"] = "any"


class CovenantDefinition(BaseModel):
    """Структурированное условие ковенанта, извлечённое из кредитного договора.

    `account_id` — то, что реально написано в тексте документа (ACC-XXXX).
    `scenario_id` документ не знает и знать не может — связку account_id ->
    scenario_id даёт леджер (см. resolution/account_scenario_linker.py), она
    проставляется отдельным шагом резолюции, а не на этапе извлечения.

    `numerator`/`denominator` заполняются для test_type=ratio, `aggregate` —
    для остальных трёх типов (см. evaluation/strategies/*).
    """

    account_id: str
    clause: str  # например "6.1"
    test_type: CovenantTestType
    threshold: float
    currency: str | None = None
    source_doc_id: str
    numerator: AmountFilter | None = None
    denominator: AmountFilter | None = None
    aggregate: AmountFilter | None = None
    raw_text: str


class RelatedPartyInfo(BaseModel):
    """Факты о связанных сторонах заёмщика из KYC-досье.

    `account_id` — как и в CovenantDefinition, это то, что написано в
    документе; связка с scenario_id — на этапе резолюции.
    """

    account_id: str
    ownership_threshold_pct: float
    related_counterparties: list[str] = Field(default_factory=list)
    source_doc_id: str


class Reclassification(BaseModel):
    """Инструкция аудитора о переклассификации конкретной транзакции."""

    txn_id: str
    new_category: str
    source_doc_id: str
    is_final: bool


class CovenantStatus(StrEnum):
    COMPLIANT = "COMPLIANT"
    BREACH = "BREACH"


class CovenantResult(BaseModel):
    """Итог проверки одного ковенанта — то, что ляжет в ячейку submission.json."""

    status: CovenantStatus
    actual: float
    evidence_txn_id: str | None = None


class Scenario(BaseModel):
    """Заёмщик: сценарий + связанные с ним счета/транзакции."""

    scenario_id: str
    account_ids: list[str] = Field(default_factory=list)
    transactions: list[Transaction] = Field(default_factory=list)


class AnswerCellKey(BaseModel):
    """Идентификатор ячейки, которую нужно заполнить (из шаблона ответа)."""

    scenario_id: str
    clause: str
