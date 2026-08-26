"""Точка входа: `python -m bank_ai_agent run --case halyk_2025`.

TODO: реализовать после того, как core.pipeline.run перестанет быть заглушкой.
"""

from __future__ import annotations

from pathlib import Path

import click

from bank_ai_agent.core.pipeline import PipelineConfig, run


@click.group()
def main() -> None:
    pass


@main.command("run")
@click.option("--case", "case_name", required=True, help="Имя кейса из config/cases/")
def run_case(case_name: str) -> None:
    config = PipelineConfig(
        case_name=case_name,
        case_dir=Path("config/cases") / case_name,
        artifacts_dir=Path("artifacts") / case_name,
    )
    output_path = run(config)
    click.echo(f"submission.json готов: {output_path}")


if __name__ == "__main__":
    main()
