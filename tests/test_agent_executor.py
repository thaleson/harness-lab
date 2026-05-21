"""Tests for harness/agent_executor.py."""

from harness.agent_executor import AgentExecutor
from harness.task_loader import Task


def make_task(**kwargs):
    defaults = {
        "name": "Feature 001 - Test",
        "objetivo": "Implementar algo.",
        "regras": ["Usar pathlib"],
        "arquivos_permitidos": ["src/app.py", "tests/test_app.py"],
        "criterios": ["Testes passam"],
    }
    defaults.update(kwargs)
    return Task(**defaults)


def test_plan_ready_for_valid_task():
    executor = AgentExecutor()
    task = make_task()
    plan = executor.generate_plan(task)
    assert plan.status == "READY"
    assert plan.task_name == "Feature 001 - Test"
    assert plan.objetivo == "Implementar algo."


def test_plan_blocked_for_invalid_task():
    executor = AgentExecutor()
    task = make_task(name="Unnamed Task", objetivo="", regras=[])
    plan = executor.generate_plan(task)
    assert plan.status == "BLOCKED"
    assert plan.steps == []


def test_plan_includes_validate_step():
    executor = AgentExecutor()
    task = make_task()
    plan = executor.generate_plan(task)
    validate_steps = [s for s in plan.steps if s.action == "validate"]
    assert len(validate_steps) == 1
    assert validate_steps[0].order == 1


def test_plan_includes_read_steps_for_files():
    executor = AgentExecutor()
    task = make_task(arquivos_permitidos=["a.py", "b.py", "c.py"])
    plan = executor.generate_plan(task)
    read_steps = [s for s in plan.steps if s.action == "read"]
    assert len(read_steps) == 3
    targets = [s.target for s in read_steps]
    assert targets == ["a.py", "b.py", "c.py"]


def test_plan_includes_check_steps():
    executor = AgentExecutor()
    task = make_task()
    plan = executor.generate_plan(task)
    check_steps = [s for s in plan.steps if s.action == "check"]
    assert len(check_steps) == 4
    targets = [s.target for s in check_steps]
    assert targets == ["pytest", "black", "isort", "flake8"]


def test_plan_includes_summarize_step():
    executor = AgentExecutor()
    task = make_task()
    plan = executor.generate_plan(task)
    summarize_steps = [s for s in plan.steps if s.action == "summarize"]
    assert len(summarize_steps) == 1


def test_plan_step_order():
    executor = AgentExecutor()
    task = make_task(arquivos_permitidos=["a.py"])
    plan = executor.generate_plan(task)
    orders = [s.order for s in plan.steps]
    assert orders == list(range(1, len(plan.steps) + 1))


def test_plan_preserves_task_data():
    executor = AgentExecutor()
    task = make_task(
        regras=["R1", "R2"],
        arquivos_permitidos=["x.py"],
    )
    plan = executor.generate_plan(task)
    assert plan.regras == ["R1", "R2"]
    assert plan.arquivos == ["x.py"]


def test_plan_total_steps():
    executor = AgentExecutor()
    task = make_task(arquivos_permitidos=["a.py", "b.py"])
    plan = executor.generate_plan(task)
    # 1 validate + 2 read + 4 checks + 1 summarize = 8
    assert len(plan.steps) == 8
