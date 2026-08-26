"""Оркестратор стадий: ingest -> extract -> resolve -> evaluate -> assemble.

Каждая стадия — чистая функция от входа к выходу (см. PLAN.md, "Поток данных").
Оркестратор только вызывает стадии по порядку и сохраняет промежуточные
артефакты — сам не содержит бизнес-логики какого-либо конкретного кейса.

TODO: реализовать после того, как определены конкретные сигнатуры стадий в
ingestion/extraction/resolution/evaluation/assembly.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class PipelineConfig:
    case_name: str
    case_dir: Path
    artifacts_dir: Path


def run(config: PipelineConfig) -> Path:
    """Прогоняет весь пайплайн для указанного кейса, возвращает путь к submission.json.

    TODO:
      1. ingestion: leger_source + document_source + template_loader
      2. extraction: classifier -> extractors.*
      3. resolution: account_scenario_linker -> version_resolver -> ledger_adjuster
      4. evaluation: registry.dispatch -> strategies.* -> evidence_selector
      5. assembly: answer_writer -> validator
    """
    raise NotImplementedError("TODO: собрать стадии пайплайна")
