"""CLI entry point for Harness Lab."""

from pathlib import Path

import click

from harness.agent_executor import AgentExecutor
from harness.agent_runtime import AgentRuntime
from harness.contracts_loader import ContractLoader
from harness.diff_engine import DiffPatch, DiffPatchEngine
from harness.evaluator import Evaluator
from harness.execution_reporter import ExecutionReporter
from harness.file_runtime import FilePatch, SafeFileRuntime
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


@main.command()
@click.argument("path", type=click.Path(exists=True))
def runtime_spec(path: str):
    """Load a spec, generate plan, and execute it in the runtime."""
    loader = OpenSpecLoader()
    t = loader.load(path)

    click.echo(f"Spec: {t.name}")
    click.echo(f"Objetivo: {t.objetivo}")
    click.echo("")

    # Validate
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

    # Execute in runtime
    runtime = AgentRuntime()
    result = runtime.execute(plan)

    click.echo("Runtime Execution")
    click.echo("=" * 40)

    for sr in result.step_results:
        click.echo(
            f"  [{sr.step.order:>2}] {sr.step.action.upper():<10} "
            f"... {sr.status} ({sr.duration_ms}ms)"
        )

    click.echo("")
    click.echo(f"Status: {result.overall_status}")
    click.echo(f"Duration: {result.total_duration_ms}ms")

    success_count = sum(1 for sr in result.step_results if sr.status == "SUCCESS")
    total = len(result.step_results)
    click.echo(f"Steps: {success_count}/{total} SUCCESS")


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--apply",
    is_flag=True,
    default=False,
    help="Apply patches for real. Without this flag, runs in dry-run mode.",
)
def runtime_apply(path: str, apply: bool):
    """Load a spec, validate, and apply file patches (dry-run by default)."""
    loader = OpenSpecLoader()
    t = loader.load(path)

    mode = "APPLY" if apply else "DRY-RUN"
    click.echo(f"Spec: {t.name}")
    click.echo(f"Objetivo: {t.objetivo}")
    click.echo(f"Mode: {mode}")
    click.echo("")

    # Validate
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

    # Create patches for each allowed file
    patches = [
        FilePatch(
            target=arquivo,
            content=f"\n# [harness-lab] Patch from spec: {t.name}\n",
        )
        for arquivo in t.arquivos_permitidos
    ]

    # Apply patches
    workspace = Path(".")
    runtime = SafeFileRuntime(workspace=workspace, allowed_files=t.arquivos_permitidos)
    result = runtime.apply_patches(patches, dry_run=not apply)

    click.echo("Safe File Runtime")
    click.echo("=" * 40)

    for r in result.results:
        click.echo(f"  [{r.status}] {r.target}: {r.message}")

    click.echo("")
    click.echo(f"Status: {result.overall_status}")

    success_count = sum(1 for r in result.results if r.status == "SUCCESS")
    total = len(result.results)
    click.echo(f"Files: {success_count}/{total} SUCCESS")


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--apply",
    is_flag=True,
    default=False,
    help="Apply diff patches for real. Without this flag, runs in dry-run mode.",
)
def runtime_diff(path: str, apply: bool):
    """Load a spec, validate, and apply diff patches (dry-run by default)."""
    loader = OpenSpecLoader()
    t = loader.load(path)

    mode = "APPLY" if apply else "DRY-RUN"
    click.echo(f"Spec: {t.name}")
    click.echo(f"Objetivo: {t.objetivo}")
    click.echo(f"Mode: {mode}")
    click.echo("")

    # Validate
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

    # Create example diff patches for allowed files
    patches = [
        DiffPatch(
            target=arquivo,
            search="# TODO",
            replace=f"# DONE: {t.name}",
            description=f"Mark as done in {arquivo}",
        )
        for arquivo in t.arquivos_permitidos
    ]

    # Apply patches
    workspace = Path(".")
    engine = DiffPatchEngine(workspace=workspace, allowed_files=t.arquivos_permitidos)
    result = engine.apply_patches(patches, dry_run=not apply)

    click.echo("Diff Patch Engine")
    click.echo("=" * 40)

    for r in result.results:
        click.echo(f"  [{r.status}] {r.target}: {r.message}")

    click.echo("")
    click.echo(f"Status: {result.overall_status}")

    success_count = sum(1 for r in result.results if r.status == "SUCCESS")
    total = len(result.results)
    click.echo(f"Files: {success_count}/{total} SUCCESS")


if __name__ == "__main__":
    main()
