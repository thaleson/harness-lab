"""Load and parse Markdown task files."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Task:
    """Parsed representation of a task."""

    name: str
    objetivo: str = ""
    regras: list[str] = field(default_factory=list)
    arquivos_permitidos: list[str] = field(default_factory=list)
    criterios: list[str] = field(default_factory=list)


class TaskLoader:
    """Loads and parses Markdown task files."""

    SECTIONS = {"objetivo", "regras", "arquivos permitidos", "critérios de aceite"}

    def load(self, path: str | Path) -> Task:
        """Load a task from a Markdown file."""
        filepath = Path(path)
        if not filepath.exists():
            raise FileNotFoundError(f"Task file not found: {path}")
        text = filepath.read_text(encoding="utf-8")
        return self._parse(text)

    def _parse(self, text: str) -> Task:
        lines = text.strip().splitlines()
        name = self._extract_title(lines)
        sections = self._extract_sections(lines)

        return Task(
            name=name,
            objetivo=sections.get("objetivo", ""),
            regras=sections.get("regras", []),
            arquivos_permitidos=sections.get("arquivos permitidos", []),
            criterios=sections.get("critérios de aceite", []),
        )

    def _extract_title(self, lines: list[str]) -> str:
        for line in lines:
            if line.startswith("# "):
                return line[2:].strip()
        return "Unnamed Task"

    def _extract_sections(self, lines: list[str]) -> dict[str, str | list[str]]:
        sections: dict[str, str | list[str]] = {}
        current_section: str | None = None
        current_lines: list[str] = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("## "):
                if current_section is not None:
                    sections[current_section] = self._build_value(
                        current_section, current_lines
                    )
                heading = stripped[3:].strip().lower()
                current_section = heading if heading in self.SECTIONS else None
                current_lines = []
                continue

            if current_section is not None:
                current_lines.append(stripped)

        if current_section is not None:
            sections[current_section] = self._build_value(
                current_section, current_lines
            )

        return sections

    def _build_value(self, section: str, lines: list[str]) -> str | list[str]:
        if section == "objetivo":
            return " ".join(line for line in lines if line).strip()
        return [line[2:].strip() for line in lines if line.startswith("- ")]
