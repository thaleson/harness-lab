"""Tests for harness/execution_reporter.py."""

from harness.agent_executor import ExecutionPlan, ExecutionStep
from harness.execution_reporter import ExecutionReporter


def make_plan(**kwargs):
    defaults = {
        "task_name": "Feature 001 - Test",
        "objetivo": "Implementar algo.",
        "steps": [
            ExecutionStep(
                order=1, action="validate", target="task", description="Validar task"
            ),
            ExecutionStep(
                order=2,
                action="read",
                target="src/app.py",
                description="Ler src/app.py",
            ),
        ],
        "status": "READY",
        "arquivos": ["src/app.py"],
        "regras": ["Usar pathlib"],
    }
    defaults.update(kwargs)
    return ExecutionPlan(**defaults)


def test_report_creates_file(tmp_path):
    reporter = ExecutionReporter()
    plan = make_plan()
    output = tmp_path / "report.md"
    result = reporter.generate(plan, output)
    assert result.exists()
    assert result == output


def test_report_contains_task_name(tmp_path):
    reporter = ExecutionReporter()
    plan = make_plan()
    output = tmp_path / "report.md"
    reporter.generate(plan, output)
    content = output.read_text()
    assert "Feature 001 - Test" in content


def test_report_contains_objetivo(tmp_path):
    reporter = ExecutionReporter()
    plan = make_plan()
    output = tmp_path / "report.md"
    reporter.generate(plan, output)
    content = output.read_text()
    assert "Implementar algo." in content


def test_report_contains_status(tmp_path):
    reporter = ExecutionReporter()
    plan = make_plan()
    output = tmp_path / "report.md"
    reporter.generate(plan, output)
    content = output.read_text()
    assert "**Status:** READY" in content


def test_report_contains_steps(tmp_path):
    reporter = ExecutionReporter()
    plan = make_plan()
    output = tmp_path / "report.md"
    reporter.generate(plan, output)
    content = output.read_text()
    assert "VALIDATE" in content
    assert "READ" in content
    assert "src/app.py" in content
    assert "Validar task" in content


def test_report_contains_arquivos(tmp_path):
    reporter = ExecutionReporter()
    plan = make_plan()
    output = tmp_path / "report.md"
    reporter.generate(plan, output)
    content = output.read_text()
    assert "## Arquivos Envolvidos" in content
    assert "- src/app.py" in content


def test_report_contains_regras(tmp_path):
    reporter = ExecutionReporter()
    plan = make_plan()
    output = tmp_path / "report.md"
    reporter.generate(plan, output)
    content = output.read_text()
    assert "## Regras" in content
    assert "- Usar pathlib" in content


def test_report_contains_timestamp(tmp_path):
    reporter = ExecutionReporter()
    plan = make_plan()
    output = tmp_path / "report.md"
    reporter.generate(plan, output)
    content = output.read_text()
    assert "**Date:**" in content


def test_report_creates_parent_dirs(tmp_path):
    reporter = ExecutionReporter()
    plan = make_plan()
    output = tmp_path / "sub" / "dir" / "report.md"
    result = reporter.generate(plan, output)
    assert result.exists()


def test_report_blocked_status(tmp_path):
    reporter = ExecutionReporter()
    plan = make_plan(status="BLOCKED", steps=[])
    output = tmp_path / "report.md"
    reporter.generate(plan, output)
    content = output.read_text()
    assert "**Status:** BLOCKED" in content


def test_report_empty_arquivos(tmp_path):
    reporter = ExecutionReporter()
    plan = make_plan(arquivos=[])
    output = tmp_path / "report.md"
    reporter.generate(plan, output)
    content = output.read_text()
    assert "Nenhum arquivo definido" in content


def test_report_empty_regras(tmp_path):
    reporter = ExecutionReporter()
    plan = make_plan(regras=[])
    output = tmp_path / "report.md"
    reporter.generate(plan, output)
    content = output.read_text()
    assert "Nenhuma regra definida" in content
