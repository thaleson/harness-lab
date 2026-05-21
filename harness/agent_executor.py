"""Generate execution plans for tasks."""

from __future__ import annotations

from dataclasses import dataclass, field

from harness.task_loader import Task
from harness.task_validator import TaskValidator


@dataclass
class ExecutionStep:
    """A single step in an execution plan."""

    order: int
    action: str  # "validate", "read", "check", "summarize"
    target: str
    description: str


@dataclass
class ExecutionPlan:
    """Execution plan for a task."""

    task_name: str
    objetivo: str
    steps: list[ExecutionStep] = field(default_factory=list)
    status: str = "READY"  # READY, BLOCKED
    arquivos: list[str] = field(default_factory=list)
    regras: list[str] = field(default_factory=list)


class AgentExecutor:
    """Generates execution plans for tasks."""

    CHECKS = ["pytest", "black", "isort", "flake8"]

    def __init__(self, validator: TaskValidator | None = None):
        self.validator = validator or TaskValidator()

    def generate_plan(self, task: Task) -> ExecutionPlan:
        """Generate an execution plan from a task."""
        validation = self.validator.validate(task)

        if validation.overall_status == "FAIL":
            return ExecutionPlan(
                task_name=task.name,
                objetivo=task.objetivo,
                steps=[],
                status="BLOCKED",
                arquivos=task.arquivos_permitidos,
                regras=task.regras,
            )

        steps: list[ExecutionStep] = []
        order = 1

        # Step 1: Validate
        steps.append(
            ExecutionStep(
                order=order,
                action="validate",
                target="task",
                description="Validar estrutura da task",
            )
        )
        order += 1

        # Steps for each allowed file
        for arquivo in task.arquivos_permitidos:
            steps.append(
                ExecutionStep(
                    order=order,
                    action="read",
                    target=arquivo,
                    description=f"Ler {arquivo}",
                )
            )
            order += 1

        # Steps for quality checks
        for check in self.CHECKS:
            steps.append(
                ExecutionStep(
                    order=order,
                    action="check",
                    target=check,
                    description=f"Rodar {check}",
                )
            )
            order += 1

        # Final step: summarize
        steps.append(
            ExecutionStep(
                order=order,
                action="summarize",
                target="report",
                description="Gerar resumo da execução",
            )
        )

        return ExecutionPlan(
            task_name=task.name,
            objetivo=task.objetivo,
            steps=steps,
            status="READY",
            arquivos=task.arquivos_permitidos,
            regras=task.regras,
        )
