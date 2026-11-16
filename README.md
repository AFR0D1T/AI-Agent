# bank-ai-agent

An agent that reads messy financial documents (loan agreements, KYC dossiers, audit notes) together with a transaction ledger, and determines whether each borrower complies with its financial covenants.

## What it does

The agent takes three inputs for a case:

- a transaction ledger in CSV form,
- a folder of documents (PDF, `.txt`, `.csv`), mixed with a large amount of irrelevant material,
- a submission template that lists which scenarios and covenant clauses must be answered.

For every covenant clause in the template it produces a verdict (`COMPLIANT` or `BREACH`), the measured `actual` value, and an `evidence_txn_id` when a single transaction decides the verdict. The result is written as `submission.json`.

An LLM is used only for two steps: classifying each document and extracting structured facts from it. Everything else (ledger parsing, version selection, ledger adjustments, covenant arithmetic, evidence selection, and validation) is deterministic Python code.

## How it works

The pipeline is defined in `src/bank_ai_agent/core/pipeline.py` and runs five stages in order:

1. **Ingestion** (`ingestion/`). Reads the ledger (`ledger_source.py`; empty amounts become `None`), all documents (`document_source.py`; PDFs are read with PyMuPDF, and each document gets a `doc_id` derived from a hash of its file contents), and the answer cells from the submission template (`template_loader.py`).
2. **Extraction** (`extraction/`). `classifier.py` sends each document to the LLM to determine its type. Documents typed as `loan_agreement`, `kyc_dossier`, or `audit_note` are then passed to the matching extractor in `extraction/extractors/`, which returns covenant definitions, related-party information, or transaction reclassifications. Documents typed `noise` or `unknown` are skipped.
3. **Resolution** (`resolution/`). Groups ledger transactions into scenarios using the `TXN-<scenario_id>-<seq>` pattern and keeps only the scenarios named in the template (`account_scenario_linker.py`). `version_resolver.py` drops superseded documents and keeps the most recent effective version of each covenant and related-party record. `ledger_adjuster.py` applies final (non-draft) auditor reclassifications and flags transactions with related counterparties.
4. **Evaluation** (`evaluation/`). Each covenant is checked by the strategy registered for its test type in `registry.py`: `ratio`, `absolute_cap`, `minimum_floor`, or `related_party_cap`. `evidence_selector.py` then recalculates the verdict with each transaction removed in turn; if exactly one removal changes the verdict, that transaction becomes the evidence.
5. **Assembly** (`assembly/`). `answer_writer.py` fills the template with the results and the team, contact, and model values from the case configuration. `validator.py` then checks that the keys match the template exactly, that statuses are valid, and that `actual` is rounded to two decimals. Validation failures stop the run.

Transactions are matched to covenant components by keyword. The ledger has no category column, so a covenant such as "taxes plus utilities" is defined by description and counterparty keywords that the LLM extracts from the agreement text, and these keywords are applied case-insensitively.

LLM calls go through a provider-neutral port (`core/llm/client.py`). The only provider currently implemented is Gemini (`core/llm/providers/gemini.py`, default model `gemini-2.5-flash`). Responses are cached on disk by `core/cache.py` in `artifacts/<case>/.cache/`, so re-running a case does not repeat LLM calls for documents that were already processed.

## Project structure

```
bank-ai-agent/
├── config/
│   ├── cases/
│   │   └── halyk_2025/
│   │       └── case.yaml          # data paths, LLM settings, submission metadata
│   └── prompts/
│       ├── classify_document.md   # document classification prompt
│       ├── extract_loan_agreement.md
│       ├── extract_kyc_dossier.md
│       └── extract_audit_note.md
├── src/bank_ai_agent/
│   ├── __main__.py                # enables `python -m bank_ai_agent`
│   ├── cli.py                     # click command group: `run --case <name>`
│   ├── core/                      # domain models, pipeline orchestrator, LLM port, cache
│   │   ├── llm/                   # LLM client port, JSON schemas, providers/gemini.py
│   │   ├── cache.py
│   │   ├── models.py
│   │   └── pipeline.py
│   ├── ingestion/                 # ledger, document, and template loaders
│   ├── extraction/                # classifier and extractors/ (one per document type)
│   ├── resolution/                # scenario linking, version selection, ledger adjustments
│   ├── evaluation/                # amount filters, evidence selection, strategies/
│   └── assembly/                  # submission writer and validator
├── tests/
│   ├── unit/                      # deterministic logic, no network
│   ├── integration/               # full pipeline with a fake LLM provider
│   └── fixtures/
├── artifacts/                     # run outputs (ignored by git)
├── .env.example
├── pyproject.toml
└── README.md
```

## Getting started

### Requirements

- Python 3.11 or newer (the code uses `StrEnum` and `X | Y` type unions).
- A Google AI Studio API key for Gemini.
- The case dataset. It is not included in this repository. `config/cases/halyk_2025/case.yaml` expects a directory named `agentic-bank-public` next to the repository folder, containing `master_ledger_2025.csv`, a `documents/` folder, and `submission_template.json`.

### Install

```bash
git clone <repository-url> bank-ai-agent
cd bank-ai-agent
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

The runtime dependencies declared in `pyproject.toml` are `pydantic`, `pyyaml`, `click`, `pymupdf`, `google-genai`, `python-dotenv`, and `tenacity`. The `dev` extra adds `pytest`, `pytest-cov`, and `ruff`.

### Configuration

The API key is read from the environment variable named in `config/cases/halyk_2025/case.yaml` (`llm.api_key_env`, which is `GEMINI_API_KEY` by default). `.env.example` documents this variable:

```bash
GEMINI_API_KEY=
```

Export the variable in your shell before running the agent:

```bash
export GEMINI_API_KEY=your-key-here
```

The code does not read a `.env` file. `python-dotenv` is listed as a dependency but is not imported anywhere, so copying `.env.example` to `.env` has no effect on its own.

Before producing a real submission, set `submission.team` and `submission.contact_email` in `case.yaml`. Both are currently the placeholder `TODO`.

### Run

Run the command from the repository root, because the case paths are resolved relative to the current directory:

```bash
python -m bank_ai_agent run --case halyk_2025
```

The equivalent console script installed by the package is:

```bash
bank-ai-agent run --case halyk_2025
```

On success the command prints the path to the result, `artifacts/halyk_2025/submission.json`.

## Running tests

```bash
pytest
ruff check src tests
```

The tests need no network access. The unit tests in `tests/unit/` cover the deterministic stages (ledger and document loading, version selection, adjustments, strategies, evidence selection, submission writing, and validation). `tests/integration/test_pipeline_end_to_end.py` runs the full pipeline on a small synthetic case, with the LLM replaced by a fake provider that returns canned responses.

## Configuration reference

- `config/cases/<case>/case.yaml` defines:
  - `data.ledger_csv`, `data.documents_dir`, and `data.submission_template`, resolved relative to the case directory;
  - `llm.provider` (currently only `gemini`), `llm.model`, and `llm.api_key_env`;
  - `submission.team`, `submission.contact_email`, and `submission.model`.
- `config/prompts/*.md` holds the four prompts. The classification prompt defines the document types, and the loan agreement prompt defines how covenant tests and keyword filters are extracted. The pipeline loads these files by name, so renaming a file requires updating `_PROMPT_FILES` in `core/pipeline.py`.
- Adding a new case means adding a directory under `config/cases/` with its own `case.yaml`. The prompts are shared across cases.

## Known limitations

- The LLM cache key is built from the prompt and the document text only. Changing `llm.model` does not invalidate cached answers. To force a fresh extraction, delete `artifacts/<case>/.cache/`.
- A ratio covenant whose denominator is zero raises an error that is not caught, so the run stops.
- A covenant clause that cannot be extracted leaves its cell empty. The validator then rejects the submission.

## Status

The pipeline is implemented end to end (ingestion, extraction, resolution, evaluation, assembly). The unit and integration tests run without network access. Running the agent against real documents requires a `GEMINI_API_KEY` and the external dataset described above.
