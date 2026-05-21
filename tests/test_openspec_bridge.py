"""Tests for harness/openspec_bridge.py."""

import pytest

from harness.openspec_bridge import OpenSpecLoader
from harness.task_loader import Task


@pytest.fixture
def loader():
    return OpenSpecLoader()


def test_load_full_spec(tmp_path, loader):
    spec_file = tmp_path / "spec.md"
    spec_file.write_text(
        "# Auth Refactor\n"
        "\n"
        "## Description\n"
        "Refatorar auth.\n"
        "\n"
        "## Requirements\n"
        "- Usar pathlib\n"
        "- Type hints\n"
        "\n"
        "## Constraints\n"
        "- Não quebrar API\n"
        "\n"
        "## Files\n"
        "- src/auth.py\n"
        "- tests/test_auth.py\n"
        "\n"
        "## Acceptance Criteria\n"
        "- Testes passam\n"
        "- Código formatado\n"
    )

    task = loader.load(spec_file)

    assert task.name == "Auth Refactor"
    assert task.objetivo == "Refatorar auth."
    assert "Usar pathlib" in task.regras
    assert "Type hints" in task.regras
    assert "Não quebrar API" in task.regras
    assert task.arquivos_permitidos == ["src/auth.py", "tests/test_auth.py"]
    assert task.criterios == ["Testes passam", "Código formatado"]


def test_load_spec_missing_sections(tmp_path, loader):
    spec_file = tmp_path / "minimal.md"
    spec_file.write_text("# Minimal Spec\n" "\n" "## Description\n" "Algo simples.\n")

    task = loader.load(spec_file)

    assert task.name == "Minimal Spec"
    assert task.objetivo == "Algo simples."
    assert task.regras == []
    assert task.arquivos_permitidos == []
    assert task.criterios == []


def test_load_spec_no_title(tmp_path, loader):
    spec_file = tmp_path / "notitle.md"
    spec_file.write_text("## Description\n" "Algo sem título.\n")

    task = loader.load(spec_file)

    assert task.name == "Unnamed Spec"
    assert task.objetivo == "Algo sem título."


def test_load_file_not_found(loader):
    with pytest.raises(FileNotFoundError):
        loader.load("/nonexistent/spec.md")


def test_requirements_and_constraints_merged(tmp_path, loader):
    spec_file = tmp_path / "spec.md"
    spec_file.write_text(
        "# Test\n"
        "\n"
        "## Description\n"
        "Algo.\n"
        "\n"
        "## Requirements\n"
        "- Req 1\n"
        "- Req 2\n"
        "\n"
        "## Constraints\n"
        "- Constraint 1\n"
    )

    task = loader.load(spec_file)

    assert len(task.regras) == 3
    assert task.regras[0] == "Req 1"
    assert task.regras[1] == "Req 2"
    assert task.regras[2] == "Constraint 1"


def test_task_dataclass_compatibility():
    """Verify OpenSpec produces valid Task for TaskValidator."""
    from harness.task_validator import TaskValidator

    task = Task(
        name="Test Spec",
        objetivo="Do something.",
        regras=["Rule 1"],
        arquivos_permitidos=["src/app.py"],
        criterios=["Works"],
    )
    validator = TaskValidator()
    result = validator.validate(task)
    assert result.overall_status == "PASS"
