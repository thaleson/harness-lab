"""CLI entry point for Harness Lab."""

from pathlib import Path

import click

from harness.contracts_loader import ContractLoader
from harness.evaluator import Evaluator
from harness.reporter import Reporter
from harness.runner import CheckRunner
from harness.task_loader import TaskLoader

CONTRACT_PATH = Path("contracts/sprint-1.md")
REPORT_PATH = Path("reports/report.md")


@click.group()
def main():
    """Harness Lab - Quality gate runner based on Markdown contracts."""


@main.command()
@click.option(
    "--contract",
    default=str(CONTRACT_PATH),
    help="Path to the sprint contract Markdown file.",
)
@click.option(
    "--output",
    default=str(REPORT_PATH),
    help="Path to write the report.",
)
def run(contract: str, output: str):
    """Run all checks defined in the contract and generate a report."""
    click.echo(f"Loading contract: {contract}")

    # 1. Load contract
    loader = ContractLoader()
    sprint = loader.load(contract)
    click.echo(f"Contract: {sprint.name}")
    click.echo(f"Checks: {[c.tool for c in sprint.checks]}")

    # 2. Run checks
    runner = CheckRunner()
    check_names = [c.tool for c in sprint.checks]
    click.echo("\nRunning checks...")
    results = runner.run(check_names)

    for r in results:
        status = "PASS" if r.passed else "FAIL"
        click.echo(f"  [{status}] {r.name}")

    # 3. Evaluate
    evaluator = Evaluator()
    evaluation = evaluator.evaluate(sprint, results)
    click.echo(f"\nOverall: {evaluation.overall_status}")

    # 4. Generate report
    reporter = Reporter()
    report_path = reporter.generate(evaluation, output)
    click.echo(f"\nReport written to: {report_path}")


@main.command()
@click.argument("path", type=click.Path(exists=True))
def task(path: str):
    """Load and display a task summary from a Markdown file."""
    loader = TaskLoader()
    t = loader.load(path)

    click.echo(f"Task: {t.name}")
    click.echo("")
    click.echo(f"Objetivo: {t.objetivo}")
    click.echo("")
    click.echo(f"Regras ({len(t.regras)}):")
    for r in t.regras:
        click.echo(f"  - {r}")
    click.echo("")
    click.echo(f"Arquivos Permitidos ({len(t.arquivos_permitidos)}):")
    for f in t.arquivos_permitidos:
        click.echo(f"  - {f}")
    click.echo("")
    click.echo(f"Critérios de Aceite ({len(t.criterios)}):")
    for c in t.criterios:
        click.echo(f"  - {c}")


if __name__ == "__main__":
    main()
