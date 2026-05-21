"""Generate Markdown reports from evaluations."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from harness.evaluator import Evaluation


class Reporter:
    """Generates Markdown reports from evaluation results."""

    def generate(self, evaluation: Evaluation, output_path: str | Path) -> Path:
        """Generate a Markdown report and write it to output_path."""
        content = self._render(evaluation)
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def _render(self, evaluation: Evaluation) -> str:
        lines: list[str] = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines.append(f"# Harness Report")
        lines.append("")
        lines.append(f"**Contract:** {evaluation.contract_name}")
        lines.append(f"**Date:** {timestamp}")
        lines.append(f"**Status:** {evaluation.overall_status}")
        lines.append("")

        lines.append("## Check Results")
        lines.append("")
        lines.append("| Check | Status | Details |")
        lines.append("|-------|--------|---------|")

        for check_eval in evaluation.check_evaluations:
            status_icon = self._status_icon(check_eval.status)
            details = check_eval.details.replace("\n", " ")
            if len(details) > 100:
                details = details[:97] + "..."
            lines.append(
                f"| {check_eval.name} | {status_icon} {check_eval.status} | {details} |"
            )

        lines.append("")
        lines.append("## Summary")
        lines.append("")
        total = len(evaluation.check_evaluations)
        passed = sum(1 for e in evaluation.check_evaluations if e.passed)
        failed = total - passed
        lines.append(f"- **Total checks:** {total}")
        lines.append(f"- **Passed:** {passed}")
        lines.append(f"- **Failed:** {failed}")
        lines.append("")

        if evaluation.overall_status == "PASS":
            lines.append("> **Result:** Sprint approved. All quality gates passed.")
        else:
            lines.append("> **Result:** Sprint blocked. Fix failing checks before merging.")

        lines.append("")
        return "\n".join(lines)

    def _status_icon(self, status: str) -> str:
        if status == "PASS":
            return ":white_check_mark:"
        if status == "BLOCKED":
            return ":no_entry:"
        return ":x:"
