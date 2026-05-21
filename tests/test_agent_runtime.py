"""Tests for harness/agent_runtime.py."""

from harness.agent_executor import ExecutionPlan, ExecutionStep
from harness.agent_runtime import AgentRuntime


def make_plan(status="READY", steps=None):
    if steps is None:
        steps = [
            ExecutionStep(
                order=1,
                action="validate",
                target="task",
                description="Validar task",
            ),
            ExecutionStep(
                order=2,
                action="read",
                target="src/app.py",
                description="Ler src/app.py",
            ),
            ExecutionStep(
                order=3,
                action="check",
                target="pytest",
                description="Rodar pytest",
            ),
            ExecutionStep(
                order=4,
                action="summarize",
                target="report",
                description="Gerar resumo",
            ),
        ]
    return ExecutionPlan(
        task_name="Test",
        objetivo="Testar runtime.",
        steps=steps,
        status=status,
        arquivos=["src/app.py"],
        regras=["Rule 1"],
    )


def test_execute_ready_plan():
    runtime = AgentRuntime()
    plan = make_plan()
    result = runtime.execute(plan)
    assert result.overall_status == "COMPLETED"
    assert len(result.step_results) == 4


def test_execute_blocked_plan():
    runtime = AgentRuntime()
    plan = make_plan(status="BLOCKED", steps=[])
    result = runtime.execute(plan)
    assert result.overall_status == "BLOCKED"
    assert result.step_results == []
    assert result.total_duration_ms == 0.0


def test_step_results_have_status():
    runtime = AgentRuntime()
    plan = make_plan()
    result = runtime.execute(plan)
    for sr in result.step_results:
        assert sr.status in ("SUCCESS", "SKIPPED")


def test_step_results_have_duration():
    runtime = AgentRuntime()
    plan = make_plan()
    result = runtime.execute(plan)
    for sr in result.step_results:
        assert sr.duration_ms >= 0


def test_total_duration_positive():
    runtime = AgentRuntime()
    plan = make_plan()
    result = runtime.execute(plan)
    assert result.total_duration_ms >= 0


def test_logs_not_empty():
    runtime = AgentRuntime()
    plan = make_plan()
    result = runtime.execute(plan)
    assert len(result.logs) > 0
    assert all(isinstance(log, str) for log in result.logs)


def test_validate_step_log():
    runtime = AgentRuntime()
    plan = make_plan()
    result = runtime.execute(plan)
    validate_result = result.step_results[0]
    assert "Validando" in validate_result.log


def test_read_step_log():
    runtime = AgentRuntime()
    plan = make_plan()
    result = runtime.execute(plan)
    read_result = result.step_results[1]
    assert "Lendo" in read_result.log


def test_check_step_log():
    runtime = AgentRuntime()
    plan = make_plan()
    result = runtime.execute(plan)
    check_result = result.step_results[2]
    assert "Executando check" in check_result.log


def test_summarize_step_log():
    runtime = AgentRuntime()
    plan = make_plan()
    result = runtime.execute(plan)
    summarize_result = result.step_results[3]
    assert "Gerando" in summarize_result.log


def test_unknown_action_skipped():
    runtime = AgentRuntime()
    steps = [
        ExecutionStep(
            order=1,
            action="unknown",
            target="x",
            description="Something",
        ),
    ]
    plan = make_plan(steps=steps)
    result = runtime.execute(plan)
    assert result.step_results[0].status == "SKIPPED"


def test_step_results_match_plan_steps():
    runtime = AgentRuntime()
    plan = make_plan()
    result = runtime.execute(plan)
    assert len(result.step_results) == len(plan.steps)
    for sr, step in zip(result.step_results, plan.steps):
        assert sr.step is step


def test_plan_preserved_in_result():
    runtime = AgentRuntime()
    plan = make_plan()
    result = runtime.execute(plan)
    assert result.plan is plan
