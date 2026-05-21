"""Run quality checks via subprocess."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Protocol


class Checker(Protocol):
    """Protocol for individual check implementations."""

    name: str

    def run(self, target: str) -> CheckResult:
        ...


@dataclass
class CheckResult:
    """Result of running a single check."""

    name: str
    passed: bool
    output: str
    errors: int = 0
    warnings: int = 0


class PytestChecker:
    """Run pytest."""

    name = "pytest"

    def run(self, target: str = "tests") -> CheckResult:
        result = subprocess.run(
            ["python", "-m", "pytest", target, "-v", "--tb=short"],
            capture_output=True,
            text=True,
        )
        output = result.stdout + result.stderr
        passed = result.returncode == 0
        return CheckResult(
            name=self.name, passed=passed, output=output
        )


class BlackChecker:
    """Run Black in check mode."""

    name = "black"

    def run(self, target: str = "src") -> CheckResult:
        result = subprocess.run(
            ["python", "-m", "black", "--check", "--diff", target],
            capture_output=True,
            text=True,
        )
        output = result.stdout + result.stderr
        passed = result.returncode == 0
        errors = output.lower().count("would reformat")
        return CheckResult(
            name=self.name, passed=passed, output=output, errors=errors
        )


class IsortChecker:
    """Run isort in check mode."""

    name = "isort"

    def run(self, target: str = "src") -> CheckResult:
        result = subprocess.run(
            ["python", "-m", "isort", "--check-only", "--diff", target],
            capture_output=True,
            text=True,
        )
        output = result.stdout + result.stderr
        passed = result.returncode == 0
        errors = output.lower().count("incorrectly sorted")
        return CheckResult(
            name=self.name, passed=passed, output=output, errors=errors
        )


class Flake8Checker:
    """Run flake8 linter."""

    name = "flake8"

    def run(self, target: str = "src") -> CheckResult:
        result = subprocess.run(
            ["python", "-m", "flake8", target],
            capture_output=True,
            text=True,
        )
        output = result.stdout + result.stderr
        passed = result.returncode == 0
        warnings = len(output.strip().splitlines()) if output.strip() else 0
        return CheckResult(
            name=self.name, passed=passed, output=output, warnings=warnings
        )


# Registry of available checkers
CHECKERS: dict[str, Checker] = {
    "pytest": PytestChecker(),
    "black": BlackChecker(),
    "isort": IsortChecker(),
    "flake8": Flake8Checker(),
}


class CheckRunner:
    """Runs a list of checks and returns results."""

    def __init__(self, checkers: dict[str, Checker] | None = None):
        self.checkers = checkers or CHECKERS

    def run(self, check_names: list[str]) -> list[CheckResult]:
        """Run the specified checks and return results."""
        results: list[CheckResult] = []

        for name in check_names:
            checker = self.checkers.get(name)
            if checker is None:
                results.append(
                    CheckResult(
                        name=name,
                        passed=False,
                        output=f"Unknown checker: {name}",
                    )
                )
                continue

            results.append(checker.run())

        return results
