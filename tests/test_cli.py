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
