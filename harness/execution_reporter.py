"""Generate Markdown execution plan reports."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from harness.agent_executor import ExecutionPlan


class ExecutionReporter:
    """Generates Markdown reports from execution plans."""

    def generate(self, plan: ExecutionPlan, output_path: str | Path) -> Path:
        """Generate an execution plan report and write it to output_path."""
        content = self._render(plan)
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def _render(self, plan: ExecutionPlan) -> str:
        lines: list[str] = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines.append("# Execution Plan Report")
        lines.append("")
        lines.append(f"**Task:** {plan.task_name}")
        lines.append(f"**Objetivo:** {plan.objetivo}")
        lines.append(f"**Status:** {plan.status}")
        lines.append(f"**Date:** {timestamp}")
        lines.append("")

        # Steps table
        lines.append("## Steps")
        lines.append("")
        lines.append("| # | Action | Target | Description |")
        lines.append("|---|--------|--------|-------------|")

        for step in plan.steps:
            lines.append(
                f"| {step.order} | {step.action.upper()} "
                f"| {step.target} | {step.description} |"
            )

        lines.append("")

        # Arquivos
        lines.append("## Arquivos Envolvidos")
        lines.append("")
        if plan.arquivos:
            for arquivo in plan.arquivos:
                lines.append(f"- {arquivo}")
        else:
            lines.append("- Nenhum arquivo definido")
        lines.append("")

        # Regras
        lines.append("## Regras")
        lines.append("")
        if plan.regras:
            for regra in plan.regras:
                lines.append(f"- {regra}")
        else:
            lines.append("- Nenhuma regra definida")
        lines.append("")

        return "\n".join(lines)
