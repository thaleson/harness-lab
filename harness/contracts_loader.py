"""Load and parse Markdown contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Check:
    """A single check defined in a contract."""

    name: str
    tool: str
    threshold: str


@dataclass
class Contract:
    """Parsed representation of a sprint contract."""

    name: str
    checks: list[Check] = field(default_factory=list)
    rules: list[str] = field(default_factory=list)


class ContractLoader:
    """Loads and parses Markdown contract files."""

    def load(self, path: str | Path) -> Contract:
        """Load a contract from a Markdown file."""
        text = Path(path).read_text(encoding="utf-8")
        return self._parse(text)

    def _parse(self, text: str) -> Contract:
        lines = text.strip().splitlines()
        name = self._extract_title(lines)
        checks = self._extract_checks(lines)
        rules = self._extract_rules(lines)
        return Contract(name=name, checks=checks, rules=rules)

    def _extract_title(self, lines: list[str]) -> str:
        for line in lines:
            if line.startswith("# "):
                return line[2:].strip()
        return "Unnamed Contract"

    def _extract_checks(self, lines: list[str]) -> list[Check]:
        checks: list[Check] = []
        in_table = False
        header_seen = False

        for line in lines:
            stripped = line.strip()
            if not stripped.startswith("|"):
                if in_table and header_seen:
                    break
                continue

            cells = [c.strip() for c in stripped.split("|") if c.strip()]

            if not in_table:
                in_table = True
                header_seen = False
                continue

            if not header_seen:
                header_seen = True
                continue

            if len(cells) >= 3:
                checks.append(Check(name=cells[0], tool=cells[1], threshold=cells[2]))

        return checks

    def _extract_rules(self, lines: list[str]) -> list[str]:
        rules: list[str] = []
        in_rules = False

        for line in lines:
            stripped = line.strip()
            if stripped.lower().startswith("## rules"):
                in_rules = True
                continue
            if in_rules and stripped.startswith("## "):
                break
            if in_rules and stripped.startswith("- "):
                rules.append(stripped[2:])

        return rules
