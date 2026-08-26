"""Оркестратор стадий: ingest -> extract -> resolve -> evaluate -> assemble.

Каждая стадия сама по себе — чистая функция (см. PLAN.md, "Поток данных").
Этот модуль только вызывает их по порядку и передаёт данные между ними; сам
не содержит бизнес-логики конкретного кейса — она в config/cases/<case>/ и в
модулях ingestion/extraction/resolution/evaluation/assembly.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

from bank_ai_agent.assembly.answer_writer import write_submission
from bank_ai_agent.assembly.validator import validate_submission
from bank_ai_agent.core.cache import FileCache
from bank_ai_agent.core.llm.client import CachingLLMProvider, LLMProvider, get_provider
from bank_ai_agent.core.models import (
    AnswerCellKey,
    ClassifiedDocument,
    CovenantDefinition,
    CovenantResult,
    DocumentType,
    Reclassification,
    RelatedPartyInfo,
)
from bank_ai_agent.evaluation.evidence_selector import select_evidence
from bank_ai_agent.evaluation.registry import get_strategy
from bank_ai_agent.extraction.classifier import classify
from bank_ai_agent.extraction.extractors import audit_note, kyc_dossier, loan_agreement
from bank_ai_agent.ingestion.document_source import load_documents
from bank_ai_agent.ingestion.ledger_source import load_ledger
from bank_ai_agent.ingestion.template_loader import load_answer_cells
from bank_ai_agent.resolution.account_scenario_linker import (
    account_to_scenario_map,
    build_scenarios,
)
from bank_ai_agent.resolution.ledger_adjuster import adjust
from bank_ai_agent.resolution.version_resolver import (
    pick_current_covenant_definitions,
    pick_current_related_party_info,
)

_PROMPT_FILES = {
    "classify": "classify_document.md",
    "loan_agreement": "extract_loan_agreement.md",
    "kyc_dossier": "extract_kyc_dossier.md",
    "audit_note": "extract_audit_note.md",
}


@dataclass
class PipelineConfig:
    case_name: str
    case_dir: Path
    artifacts_dir: Path


def _repo_root(case_dir: Path) -> Path:
    # case_dir = <repo_root>/config/cases/<case_name>
    return case_dir.resolve().parents[2]


def _load_case_config(case_dir: Path) -> dict:
    return yaml.safe_load((case_dir / "case.yaml").read_text(encoding="utf-8"))


def _load_prompts(repo_root: Path) -> dict[str, str]:
    prompts_dir = repo_root / "config" / "prompts"
    return {
        key: (prompts_dir / filename).read_text(encoding="utf-8")
        for key, filename in _PROMPT_FILES.items()
    }


def _build_provider(case_config: dict, artifacts_dir: Path) -> LLMProvider:
    llm_cfg = case_config["llm"]
    api_key = os.environ.get(llm_cfg.get("api_key_env", "GEMINI_API_KEY"))
    provider = get_provider(llm_cfg["provider"], model=llm_cfg["model"], api_key=api_key)
    cache = FileCache(artifacts_dir / ".cache")
    return CachingLLMProvider(provider, cache)


def run(config: PipelineConfig, *, provider: LLMProvider | None = None) -> Path:
    """Прогоняет весь пайплайн для указанного кейса, возвращает путь к submission.json.

    `provider` можно передать явно (например фейковый в тестах) — если не
    передан, строится из config/cases/<case>/case.yaml.
    """
    case_config = _load_case_config(config.case_dir)
    repo_root = _repo_root(config.case_dir)
    prompts = _load_prompts(repo_root)

    data_cfg = case_config["data"]
    ledger_path = (config.case_dir / data_cfg["ledger_csv"]).resolve()
    documents_dir = (config.case_dir / data_cfg["documents_dir"]).resolve()
    template_path = (config.case_dir / data_cfg["submission_template"]).resolve()

    if provider is None:
        provider = _build_provider(case_config, config.artifacts_dir)

    # --- 1. ingestion ---
    transactions = load_ledger(ledger_path)
    raw_documents = load_documents(documents_dir)
    answer_cells = load_answer_cells(template_path)
    target_scenario_ids = sorted({cell.scenario_id for cell in answer_cells})

    # --- 2. extraction ---
    classified_by_doc_id: dict[str, ClassifiedDocument] = {}
    covenant_candidates: list[CovenantDefinition] = []
    related_party_candidates: list[RelatedPartyInfo] = []
    reclassifications: list[Reclassification] = []

    for raw in raw_documents:
        classified = classify(raw, provider, prompts["classify"])
        classified_by_doc_id[raw.doc_id] = classified

        if classified.doc_type == DocumentType.LOAN_AGREEMENT:
            covenant_candidates.extend(
                loan_agreement.extract(raw, classified, provider, prompts["loan_agreement"])
            )
        elif classified.doc_type == DocumentType.KYC_DOSSIER:
            related_party_candidates.append(
                kyc_dossier.extract(raw, classified, provider, prompts["kyc_dossier"])
            )
        elif classified.doc_type == DocumentType.AUDIT_NOTE:
            reclassifications.extend(
                audit_note.extract(raw, classified, provider, prompts["audit_note"])
            )
        # noise/unknown -> не несут фактов, пропускаем

    # --- 3. resolution ---
    scenarios = build_scenarios(transactions, target_scenario_ids)
    account_to_scenario = account_to_scenario_map(scenarios)

    current_covenants = pick_current_covenant_definitions(covenant_candidates, classified_by_doc_id)
    related_party_by_account = pick_current_related_party_info(
        related_party_candidates, classified_by_doc_id
    )

    covenants_by_scenario: dict[str, list[CovenantDefinition]] = {}
    for covenant in current_covenants:
        scenario_id = account_to_scenario.get(covenant.account_id)
        if scenario_id is None:
            continue  # ковенант на счёт вне целевых сценариев — не наш случай
        covenants_by_scenario.setdefault(scenario_id, []).append(covenant)

    # --- 4. evaluation ---
    results: dict[AnswerCellKey, CovenantResult] = {}

    for scenario_id, scenario in scenarios.items():
        related_party_info = next(
            (
                related_party_by_account[account_id]
                for account_id in scenario.account_ids
                if account_id in related_party_by_account
            ),
            None,
        )

        scenario_txn_ids = {txn.txn_id for txn in scenario.transactions}
        scenario_reclassifications = [r for r in reclassifications if r.txn_id in scenario_txn_ids]
        adjusted_transactions = adjust(
            scenario.transactions, scenario_reclassifications, related_party_info
        )

        for covenant in covenants_by_scenario.get(scenario_id, []):
            strategy = get_strategy(covenant.test_type)
            result = strategy.evaluate(covenant, adjusted_transactions)
            evidence = select_evidence(covenant, adjusted_transactions, result, strategy)
            result = result.model_copy(update={"evidence_txn_id": evidence})
            results[AnswerCellKey(scenario_id=scenario_id, clause=covenant.clause)] = result

    # --- 5. assembly ---
    submission_cfg = case_config.get("submission", {})
    output_path = config.artifacts_dir / "submission.json"
    write_submission(
        template_path,
        output_path,
        results,
        team=submission_cfg.get("team", ""),
        contact_email=submission_cfg.get("contact_email", ""),
        model=submission_cfg.get("model", case_config["llm"]["model"]),
    )
    validate_submission(template_path, output_path)

    return output_path
