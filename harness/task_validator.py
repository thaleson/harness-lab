"""Validate task structure before agent execution."""

from __future__ import annotations

from dataclasses import dataclass, field

from harness.task_loader import Task


@dataclass
class ValidationResult:
    """Result of a single validation rule."""

    rule: str
    passed: bool
    details: str


@dataclass
class TaskValidation:
    """Overall validation result for a task."""

    task_name: str
    overall_status: str  # PASS, FAIL
    results: list[ValidationResult] = field(default_factory=list)


class TaskValidator:
    """Validates task structure against required rules."""

    def validate(self, task: Task) -> TaskValidation:
        """Validate a task and return results."""
        results = [
            self._validate_name(task),
            self._validate_objetivo(task),
            self._validate_regras(task),
            self._validate_arquivos(task),
            self._validate_criterios(task),
        ]

        overall = "PASS" if all(r.passed for r in results) else "FAIL"

        return TaskValidation(
            task_name=task.name,
            overall_status=overall,
            results=results,
        )

    def _validate_name(self, task: Task) -> ValidationResult:
        passed = task.name != "Unnamed Task" and bool(task.name.strip())
        return ValidationResult(
            rule="Nome definido",
            passed=passed,
            details=task.name if passed else "Task sem título definido",
        )

    def _validate_objetivo(self, task: Task) -> ValidationResult:
        passed = bool(task.objetivo.strip())
        return ValidationResult(
            rule="Objetivo preenchido",
            passed=passed,
            details=task.objetivo if passed else "Objetivo vazio",
        )

    def _validate_regras(self, task: Task) -> ValidationResult:
        count = len(task.regras)
        passed = count > 0
        return ValidationResult(
            rule="Regras definidas",
            passed=passed,
            details=f"{count} regras" if passed else "Nenhuma regra definida",
        )

    def _validate_arquivos(self, task: Task) -> ValidationResult:
        count = len(task.arquivos_permitidos)
        passed = count > 0
        return ValidationResult(
            rule="Arquivos definidos",
            passed=passed,
            details=(f"{count} arquivos" if passed else "Nenhum arquivo definido"),
        )

    def _validate_criterios(self, task: Task) -> ValidationResult:
        count = len(task.criterios)
        passed = count > 0
        return ValidationResult(
            rule="Critérios definidos",
            passed=passed,
            details=(f"{count} critérios" if passed else "Nenhum critério definido"),
        )
