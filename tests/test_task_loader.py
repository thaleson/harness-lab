"""Tests for harness/task_loader.py."""

import pytest

from harness.task_loader import Task, TaskLoader


@pytest.fixture
def loader():
    return TaskLoader()


def test_load_full_task(tmp_path, loader):
    task_file = tmp_path / "task.md"
    task_file.write_text(
        "# Feature 001 - Test\n"
        "\n"
        "## Objetivo\n"
        "Implementar algo.\n"
        "\n"
        "## Regras\n"
        "- Usar pathlib\n"
        "- Manter SOLID\n"
        "\n"
        "## Arquivos Permitidos\n"
        "- src/app.py\n"
        "- tests/test_app.py\n"
        "\n"
        "## Critérios de Aceite\n"
        "- Testes passam\n"
        "- Código formatado\n"
    )

    task = loader.load(task_file)

    assert task.name == "Feature 001 - Test"
    assert task.objetivo == "Implementar algo."
    assert task.regras == ["Usar pathlib", "Manter SOLID"]
    assert task.arquivos_permitidos == ["src/app.py", "tests/test_app.py"]
    assert task.criterios == ["Testes passam", "Código formatado"]


def test_load_task_missing_sections(tmp_path, loader):
    task_file = tmp_path / "minimal.md"
    task_file.write_text(
        "# Minimal Task\n" "\n" "## Objetivo\n" "Apenas um objetivo.\n"
    )

    task = loader.load(task_file)

    assert task.name == "Minimal Task"
    assert task.objetivo == "Apenas um objetivo."
    assert task.regras == []
    assert task.arquivos_permitidos == []
    assert task.criterios == []


def test_load_task_no_title(tmp_path, loader):
    task_file = tmp_path / "notitle.md"
    task_file.write_text("## Objetivo\n" "Algo sem título.\n")

    task = loader.load(task_file)

    assert task.name == "Unnamed Task"
    assert task.objetivo == "Algo sem título."


def test_load_file_not_found(loader):
    with pytest.raises(FileNotFoundError):
        loader.load("/nonexistent/task.md")


def test_task_dataclass_defaults():
    task = Task(name="Test")
    assert task.objetivo == ""
    assert task.regras == []
    assert task.arquivos_permitidos == []
    assert task.criterios == []
