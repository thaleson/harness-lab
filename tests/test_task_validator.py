"""Tests for harness/task_validator.py."""

from harness.task_loader import Task
from harness.task_validator import TaskValidator


def make_task(**kwargs):
    defaults = {
        "name": "Feature 001 - Test",
        "objetivo": "Implementar algo.",
        "regras": ["Usar pathlib"],
        "arquivos_permitidos": ["src/app.py"],
        "criterios": ["Testes passam"],
    }
    defaults.update(kwargs)
    return Task(**defaults)


def test_valid_task():
    validator = TaskValidator()
    task = make_task()
    result = validator.validate(task)
    assert result.overall_status == "PASS"
    assert all(r.passed for r in result.results)


def test_missing_name():
    validator = TaskValidator()
    task = make_task(name="Unnamed Task")
    result = validator.validate(task)
    assert result.overall_status == "FAIL"
    assert result.results[0].passed is False


def test_empty_name():
    validator = TaskValidator()
    task = make_task(name="   ")
    result = validator.validate(task)
    assert result.overall_status == "FAIL"
    assert result.results[0].passed is False


def test_empty_objetivo():
    validator = TaskValidator()
    task = make_task(objetivo="")
    result = validator.validate(task)
    assert result.overall_status == "FAIL"
    assert result.results[1].passed is False


def test_empty_regras():
    validator = TaskValidator()
    task = make_task(regras=[])
    result = validator.validate(task)
    assert result.overall_status == "FAIL"
    assert result.results[2].passed is False


def test_empty_arquivos():
    validator = TaskValidator()
    task = make_task(arquivos_permitidos=[])
    result = validator.validate(task)
    assert result.overall_status == "FAIL"
    assert result.results[3].passed is False


def test_empty_criterios():
    validator = TaskValidator()
    task = make_task(criterios=[])
    result = validator.validate(task)
    assert result.overall_status == "FAIL"
    assert result.results[4].passed is False


def test_validation_details_valid():
    validator = TaskValidator()
    task = make_task()
    result = validator.validate(task)
    assert result.results[0].details == "Feature 001 - Test"
    assert result.results[1].details == "Implementar algo."
    assert result.results[2].details == "1 regras"
    assert result.results[3].details == "1 arquivos"
    assert result.results[4].details == "1 critérios"


def test_validation_details_invalid():
    validator = TaskValidator()
    task = make_task(regras=[], arquivos_permitidos=[], criterios=[])
    result = validator.validate(task)
    assert result.results[2].details == "Nenhuma regra definida"
    assert result.results[3].details == "Nenhum arquivo definido"
    assert result.results[4].details == "Nenhum critério definido"
