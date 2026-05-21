"""Bridge between OpenSpec specs and Harness tasks."""

from __future__ import annotations

from pathlib import Path

from harness.task_loader import Task


class OpenSpecLoader:
    """Loads OpenSpec specs and converts them to Harness Tasks."""

    SECTIONS = {
        "description",
        "requirements",
        "constraints",
        "files",
        "acceptance criteria",
    }

    def load(self, path: str | Path) -> Task:
        """Load an OpenSpec spec and convert it to a Task."""
        filepath = Path(path)
        if not filepath.exists():
            raise FileNotFoundError(f"Spec file not found: {path}")
        text = filepath.read_text(encoding="utf-8")
        return self._parse(text)

    def _parse(self, text: str) -> Task:
        lines = text.strip().splitlines()
        name = self._extract_title(lines)
        sections = self._extract_sections(lines)

        # Merge requirements and constraints into regras
        regras: list[str] = []
        regras.extend(sections.get("requirements", []))
        regras.extend(sections.get("constraints", []))

        return Task(
            name=name,
            objetivo=sections.get("description", ""),
            regras=regras,
            arquivos_permitidos=sections.get("files", []),
            criterios=sections.get("acceptance criteria", []),
        )

    def _extract_title(self, lines: list[str]) -> str:
        for line in lines:
            if line.startswith("# "):
                return line[2:].strip()
        return "Unnamed Spec"

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
        if section == "description":
            return " ".join(line for line in lines if line).strip()
        return [line[2:].strip() for line in lines if line.startswith("- ")]
