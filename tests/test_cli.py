"""Tests for cli.py."""

import pytest
from click.testing import CliRunner

from cli import main


@pytest.fixture
def runner():
    return CliRunner()


def test_task_command(runner, tmp_path):
    task_file = tmp_path / "task.md"
    task_file.write_text(
        "# Feature 001 - Test\n"
        "\n"
        "## Objetivo\n"
        "Testar o CLI.\n"
        "\n"
        "## Regras\n"
        "- Regra 1\n"
        "\n"
        "## Arquivos Permitidos\n"
        "- cli.py\n"
        "\n"
        "## Critérios de Aceite\n"
        "- Funciona\n"
    )

    result = runner.invoke(main, ["task", str(task_file)])

    assert result.exit_code == 0
    assert "Feature 001 - Test" in result.output
    assert "Testar o CLI." in result.output
    assert "Regra 1" in result.output
    assert "cli.py" in result.output
    assert "Funciona" in result.output


def test_task_command_missing_file(runner):
    result = runner.invoke(main, ["task", "/nonexistent/task.md"])

    assert result.exit_code != 0


def test_task_command_shows_counts(runner, tmp_path):
    task_file = tmp_path / "task.md"
    task_file.write_text(
        "# Task\n"
        "\n"
        "## Objetivo\n"
        "Algo.\n"
        "\n"
        "## Regras\n"
        "- R1\n"
        "- R2\n"
        "\n"
        "## Arquivos Permitidos\n"
        "- f1.py\n"
        "- f2.py\n"
        "- f3.py\n"
        "\n"
        "## Critérios de Aceite\n"
        "- C1\n"
    )

    result = runner.invoke(main, ["task", str(task_file)])

    assert result.exit_code == 0
    assert "Regras (2)" in result.output
    assert "Arquivos Permitidos (3)" in result.output
    assert "Critérios de Aceite (1)" in result.output


def test_validate_task_pass(runner, tmp_path):
    task_file = tmp_path / "task.md"
    task_file.write_text(
        "# Feature 001 - Test\n"
        "\n"
        "## Objetivo\n"
        "Testar.\n"
        "\n"
        "## Regras\n"
        "- Regra 1\n"
        "\n"
        "## Arquivos Permitidos\n"
        "- cli.py\n"
        "\n"
        "## Critérios de Aceite\n"
        "- Funciona\n"
    )

    result = runner.invoke(main, ["validate-task", str(task_file)])

    assert result.exit_code == 0
    assert "Feature 001 - Test" in result.output
    assert "[PASS]" in result.output
    assert "Status: PASS" in result.output


def test_validate_task_fail(runner, tmp_path):
    task_file = tmp_path / "task.md"
    task_file.write_text("# Task\n" "\n" "## Objetivo\n" "Algo.\n")

    result = runner.invoke(main, ["validate-task", str(task_file)])

    assert result.exit_code == 0
    assert "[FAIL]" in result.output
    assert "Status: FAIL" in result.output


def test_validate_task_missing_file(runner):
    result = runner.invoke(main, ["validate-task", "/nonexistent/task.md"])

    assert result.exit_code != 0


def test_execute_task_ready(runner, tmp_path):
    task_file = tmp_path / "task.md"
    task_file.write_text(
        "# Feature 001 - Test\n"
        "\n"
        "## Objetivo\n"
        "Testar.\n"
        "\n"
        "## Regras\n"
        "- Regra 1\n"
        "\n"
        "## Arquivos Permitidos\n"
        "- cli.py\n"
        "\n"
        "## Critérios de Aceite\n"
        "- Funciona\n"
    )

    result = runner.invoke(main, ["execute-task", str(task_file)])

    assert result.exit_code == 0
    assert "Feature 001 - Test" in result.output
    assert "VALIDATE" in result.output
    assert "READ" in result.output
    assert "CHECK" in result.output
    assert "SUMMARIZE" in result.output
    assert "Status: READY" in result.output
    assert "Execution report written to" in result.output


def test_execute_task_generates_report(runner, tmp_path):
    task_file = tmp_path / "task.md"
    task_file.write_text(
        "# Feature 001 - Test\n"
        "\n"
        "## Objetivo\n"
        "Testar.\n"
        "\n"
        "## Regras\n"
        "- Regra 1\n"
        "\n"
        "## Arquivos Permitidos\n"
        "- cli.py\n"
        "\n"
        "## Critérios de Aceite\n"
        "- Funciona\n"
    )
    report_file = tmp_path / "report.md"

    result = runner.invoke(
        main,
        ["execute-task", str(task_file), "--output", str(report_file)],
    )

    assert result.exit_code == 0
    assert report_file.exists()
    content = report_file.read_text()
    assert "Feature 001 - Test" in content
    assert "READY" in content
    assert "VALIDATE" in content


def test_execute_task_blocked(runner, tmp_path):
    task_file = tmp_path / "task.md"
    task_file.write_text("# Task\n" "\n" "## Objetivo\n" "Algo.\n")

    result = runner.invoke(main, ["execute-task", str(task_file)])

    assert result.exit_code == 0
    assert "Validation FAILED" in result.output
    assert "Status: BLOCKED" in result.output


def test_execute_task_missing_file(runner):
    result = runner.invoke(main, ["execute-task", "/nonexistent/task.md"])

    assert result.exit_code != 0


def test_execute_spec_ready(runner, tmp_path):
    spec_file = tmp_path / "spec.md"
    spec_file.write_text(
        "# Auth Refactor\n"
        "\n"
        "## Description\n"
        "Refatorar auth.\n"
        "\n"
        "## Requirements\n"
        "- Usar pathlib\n"
        "\n"
        "## Constraints\n"
        "- Não quebrar API\n"
        "\n"
        "## Files\n"
        "- src/auth.py\n"
        "\n"
        "## Acceptance Criteria\n"
        "- Testes passam\n"
    )

    result = runner.invoke(main, ["execute-spec", str(spec_file)])

    assert result.exit_code == 0
    assert "Auth Refactor" in result.output
    assert "VALIDATE" in result.output
    assert "READ" in result.output
    assert "CHECK" in result.output
    assert "Status: READY" in result.output
    assert "Execution report written to" in result.output


def test_execute_spec_blocked(runner, tmp_path):
    spec_file = tmp_path / "spec.md"
    spec_file.write_text("# Spec\n" "\n" "## Description\n" "Algo.\n")

    result = runner.invoke(main, ["execute-spec", str(spec_file)])

    assert result.exit_code == 0
    assert "Validation FAILED" in result.output
    assert "Status: BLOCKED" in result.output


def test_execute_spec_missing_file(runner):
    result = runner.invoke(main, ["execute-spec", "/nonexistent/spec.md"])

    assert result.exit_code != 0


def test_execute_spec_generates_report(runner, tmp_path):
    spec_file = tmp_path / "spec.md"
    spec_file.write_text(
        "# Test Spec\n"
        "\n"
        "## Description\n"
        "Testar.\n"
        "\n"
        "## Requirements\n"
        "- Req 1\n"
        "\n"
        "## Constraints\n"
        "- C1\n"
        "\n"
        "## Files\n"
        "- src/app.py\n"
        "\n"
        "## Acceptance Criteria\n"
        "- Works\n"
    )
    report_file = tmp_path / "report.md"

    result = runner.invoke(
        main,
        ["execute-spec", str(spec_file), "--output", str(report_file)],
    )

    assert result.exit_code == 0
    assert report_file.exists()
    content = report_file.read_text()
    assert "Test Spec" in content
    assert "READY" in content
