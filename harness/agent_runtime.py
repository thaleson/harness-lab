"""Execute execution plans in a controlled, simulated manner."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from harness.agent_executor import ExecutionPlan, ExecutionStep


@dataclass
class RuntimeAction:
    """Configuration for how to execute an action type."""

    action: str
    handler: Callable[[ExecutionStep], tuple[str, str]]  # (status, log)


@dataclass
class StepResult:
    """Result of executing a single step."""

    step: ExecutionStep
    status: str  # "SUCCESS", "SKIPPED"
    duration_ms: float
    log: str


@dataclass
class RuntimeResult:
    """Complete result of executing a plan."""

    plan: ExecutionPlan
    overall_status: str  # "COMPLETED", "BLOCKED"
    step_results: list[StepResult] = field(default_factory=list)
    total_duration_ms: float = 0.0
    logs: list[str] = field(default_factory=list)


class AgentRuntime:
    """Executes execution plans in a controlled, simulated manner."""

    def __init__(self) -> None:
        self._actions = self._default_actions()

    def execute(self, plan: ExecutionPlan) -> RuntimeResult:
        """Execute all steps in the plan."""
        if plan.status == "BLOCKED":
            return RuntimeResult(
                plan=plan,
                overall_status="BLOCKED",
                step_results=[],
                total_duration_ms=0.0,
                logs=["Plan is BLOCKED. No steps executed."],
            )

        logs: list[str] = []
        step_results: list[StepResult] = []
        start_time = time.perf_counter()

        for step in plan.steps:
            result = self._execute_step(step)
            step_results.append(result)
            logs.append(result.log)

        total_duration = (time.perf_counter() - start_time) * 1000

        return RuntimeResult(
            plan=plan,
            overall_status="COMPLETED",
            step_results=step_results,
            total_duration_ms=round(total_duration, 2),
            logs=logs,
        )

    def _execute_step(self, step: ExecutionStep) -> StepResult:
        """Execute a single step and measure duration."""
        action = self._actions.get(step.action)

        if action is None:
            start = time.perf_counter()
            duration = (time.perf_counter() - start) * 1000
            return StepResult(
                step=step,
                status="SKIPPED",
                duration_ms=round(duration, 2),
                log=f"Unknown action: {step.action}",
            )

        start = time.perf_counter()
        status, log = action.handler(step)
        duration = (time.perf_counter() - start) * 1000

        return StepResult(
            step=step,
            status=status,
            duration_ms=round(duration, 2),
            log=log,
        )

    def _default_actions(self) -> dict[str, RuntimeAction]:
        """Define default simulated action handlers."""
        return {
            "validate": RuntimeAction(
                action="validate",
                handler=self._handle_validate,
            ),
            "read": RuntimeAction(
                action="read",
                handler=self._handle_read,
            ),
            "check": RuntimeAction(
                action="check",
                handler=self._handle_check,
            ),
            "summarize": RuntimeAction(
                action="summarize",
                handler=self._handle_summarize,
            ),
        }

    @staticmethod
    def _handle_validate(step: ExecutionStep) -> tuple[str, str]:
        return "SUCCESS", f"Validando: {step.description}"

    @staticmethod
    def _handle_read(step: ExecutionStep) -> tuple[str, str]:
        filepath = Path(step.target)
        if filepath.exists():
            return "SUCCESS", f"Lendo: {step.target}"
        return "SUCCESS", f"Lendo: {step.target} (arquivo não encontrado, simulado)"

    @staticmethod
    def _handle_check(step: ExecutionStep) -> tuple[str, str]:
        return "SUCCESS", f"Executando check: {step.target}"

    @staticmethod
    def _handle_summarize(step: ExecutionStep) -> tuple[str, str]:
        return "SUCCESS", f"Gerando: {step.description}"
