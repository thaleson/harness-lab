"""Evaluate check results against contract thresholds."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from harness.contracts_loader import Contract
from harness.runner import CheckResult


@dataclass
class CheckEvaluation:
    """Evaluation of a single check against its contract threshold."""

    name: str
    passed: bool
    status: str  # PASS, FAIL, BLOCKED
    details: str


@dataclass
class Evaluation:
    """Overall evaluation of all checks against the contract."""

    contract_name: str
    overall_status: str  # PASS, FAIL
    check_evaluations: list[CheckEvaluation] = field(default_factory=list)


class Evaluator:
    """Evaluates check results against contract thresholds."""

    def evaluate(
        self, contract: Contract, results: list[CheckResult]
    ) -> Evaluation:
        """Evaluate results against the contract."""
        result_map = {r.name: r for r in results}
        check_evals: list[CheckEvaluation] = []

        for check in contract.checks:
            result = result_map.get(check.tool)
            if result is None:
                check_evals.append(
                    CheckEvaluation(
                        name=check.name,
                        passed=False,
                        status="BLOCKED",
                        details=f"Check '{check.tool}' was not executed",
                    )
                )
                continue

            eval_result = self._evaluate_check(check, result)
            check_evals.append(eval_result)

        overall = (
            "PASS"
            if all(e.passed for e in check_evals)
            else "FAIL"
        )

        return Evaluation(
            contract_name=contract.name,
            overall_status=overall,
            check_evaluations=check_evals,
        )

    def _evaluate_check(self, check, result: CheckResult) -> CheckEvaluation:
        threshold = check.threshold.lower()

        # "all pass" threshold
        if "all pass" in threshold:
            passed = result.passed
            status = "PASS" if passed else "FAIL"
            return CheckEvaluation(
                name=check.name,
                passed=passed,
                status=status,
                details=result.output[:500] if not passed else "All passed",
            )

        # "0 errors" threshold
        if "0 errors" in threshold:
            passed = result.errors == 0
            status = "PASS" if passed else "FAIL"
            return CheckEvaluation(
                name=check.name,
                passed=passed,
                status=status,
                details=f"{result.errors} errors found" if not passed else "No errors",
            )

        # "max N warnings" threshold
        match = re.search(r"max\s+(\d+)\s+warnings?", threshold)
        if match:
            max_warnings = int(match.group(1))
            passed = result.warnings <= max_warnings
            status = "PASS" if passed else "FAIL"
            return CheckEvaluation(
                name=check.name,
                passed=passed,
                status=status,
                details=(
                    f"{result.warnings} warnings (max: {max_warnings})"
                    if not passed
                    else f"{result.warnings} warnings (within limit)"
                ),
            )

        # Fallback: just check if the tool passed
        passed = result.passed
        return CheckEvaluation(
            name=check.name,
            passed=passed,
            status="PASS" if passed else "FAIL",
            details="Check passed" if passed else result.output[:500],
        )
