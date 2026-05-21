"""CLI entry point for Harness Lab."""

from pathlib import Path

import click

from harness.agent_executor import AgentExecutor
from harness.contracts_loader import ContractLoader
from harness.evaluator import Evaluator
from harness.execution_reporter import ExecutionReporter
from harness.openspec_bridge import OpenSpecLoader
from harness.reporter import Reporter
from harness.runner import CheckRunner
from harness.task_loader import TaskLoader
from harness.task_validator import TaskValidator

CONTRACT_PATH = Path("contracts/sprint-1.md")
REPORT_PATH = Path("reports/report.md")
EXECUTION_REPORT_PATH = Path("reports/execution-plan.md")


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


@main.command()
@click.argument("path", type=click.Path(exists=True))
def validate_task(path: str):
    """Validate a task structure before execution."""
    loader = TaskLoader()
    t = loader.load(path)

    validator = TaskValidator()
    validation = validator.validate(t)

    click.echo(f"Task: {t.name}")
    click.echo("")

    for r in validation.results:
        status = "PASS" if r.passed else "FAIL"
        click.echo(f"  [{status}] {r.rule}: {r.details}")

    click.echo("")
    click.echo(f"Status: {validation.overall_status}")


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--output",
    default=str(EXECUTION_REPORT_PATH),
    help="Path to write the execution plan report.",
)
def execute_task(path: str, output: str):
    """Load, validate, and generate an execution plan for a task."""
    loader = TaskLoader()
    t = loader.load(path)

    click.echo(f"Task: {t.name}")
    click.echo(f"Objetivo: {t.objetivo}")
    click.echo("")

    # Validate first
    validator = TaskValidator()
    validation = validator.validate(t)

    if validation.overall_status == "FAIL":
        click.echo("Validation FAILED:")
        for r in validation.results:
            if not r.passed:
                click.echo(f"  [FAIL] {r.rule}: {r.details}")
        click.echo("")
        click.echo("Status: BLOCKED")
        return

    # Generate plan
    executor = AgentExecutor(validator=validator)
    plan = executor.generate_plan(t)

    click.echo("Execution Plan:")
    for step in plan.steps:
        click.echo(
            f"  [{step.order:>2}] {step.action.upper():<10} - " f"{step.description}"
        )

    click.echo("")
    click.echo(f"Status: {plan.status}")

    # Generate report
    reporter = ExecutionReporter()
    report_path = reporter.generate(plan, output)
    click.echo(f"\nExecution report written to: {report_path}")


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--output",
    default=str(EXECUTION_REPORT_PATH),
    help="Path to write the execution plan report.",
)
def execute_spec(path: str, output: str):
    """Load an OpenSpec spec and generate an execution plan."""
    loader = OpenSpecLoader()
    t = loader.load(path)

    click.echo(f"Spec: {t.name}")
    click.echo(f"Objetivo: {t.objetivo}")
    click.echo("")

    # Validate first
    validator = TaskValidator()
    validation = validator.validate(t)

    if validation.overall_status == "FAIL":
        click.echo("Validation FAILED:")
        for r in validation.results:
            if not r.passed:
                click.echo(f"  [FAIL] {r.rule}: {r.details}")
        click.echo("")
        click.echo("Status: BLOCKED")
        return

    # Generate plan
    executor = AgentExecutor(validator=validator)
    plan = executor.generate_plan(t)

    click.echo("Execution Plan:")
    for step in plan.steps:
        click.echo(
            f"  [{step.order:>2}] {step.action.upper():<10} - " f"{step.description}"
        )

    click.echo("")
    click.echo(f"Status: {plan.status}")

    # Generate report
    reporter = ExecutionReporter()
    report_path = reporter.generate(plan, output)
    click.echo(f"\nExecution report written to: {report_path}")


if __name__ == "__main__":
    main()
