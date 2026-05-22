"""Diff patch engine with safe string replacement."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path


class SecurityError(Exception):
    """Raised when a security validation fails."""


@dataclass
class DiffPatch:
    """A diff patch to apply to a file."""

    target: str
    search: str
    replace: str
    description: str = ""


@dataclass
class PatchApplyResult:
    """Result of applying a single diff patch."""

    target: str
    status: str  # "SUCCESS", "NOT_FOUND", "BLOCKED", "ERROR"
    message: str
    backup_path: str = ""


@dataclass
class DiffEngineResult:
    """Result of applying multiple diff patches."""

    overall_status: str  # "COMPLETED", "BLOCKED"
    results: list[PatchApplyResult] = field(default_factory=list)
    logs: list[str] = field(default_factory=list)


class DiffPatchEngine:
    """Applies diff patches with security validation and rollback support."""

    def __init__(self, workspace: Path, allowed_files: list[str]) -> None:
        self._workspace = workspace.resolve()
        self._allowed_files = set(allowed_files)
        self._backups: dict[str, str] = {}

    def apply(self, patch: DiffPatch, dry_run: bool = False) -> PatchApplyResult:
        """Apply a single diff patch with security validation."""
        try:
            resolved = self._validate_path(patch.target)
        except SecurityError as e:
            return PatchApplyResult(
                target=patch.target,
                status="BLOCKED",
                message=str(e),
            )

        if not resolved.exists():
            return PatchApplyResult(
                target=patch.target,
                status="NOT_FOUND",
                message=f"File not found: {patch.target}",
            )

        try:
            content = resolved.read_text(encoding="utf-8")
        except Exception as e:
            return PatchApplyResult(
                target=patch.target,
                status="ERROR",
                message=str(e),
            )

        if patch.search not in content:
            return PatchApplyResult(
                target=patch.target,
                status="NOT_FOUND",
                message=f"Search text not found in {patch.target}",
            )

        if dry_run:
            return PatchApplyResult(
                target=patch.target,
                status="SUCCESS",
                message=(
                    f"[DRY-RUN] Would replace in {patch.target}: "
                    f"{patch.description}"
                ),
            )

        # Apply: backup + replace
        backup_path = str(resolved) + ".bak"
        shutil.copy2(resolved, backup_path)
        self._backups[patch.target] = backup_path

        new_content = content.replace(patch.search, patch.replace)
        resolved.write_text(new_content, encoding="utf-8")

        return PatchApplyResult(
            target=patch.target,
            status="SUCCESS",
            message=f"[APPLY] Replaced in {patch.target}: {patch.description}",
            backup_path=backup_path,
        )

    def apply_patches(
        self, patches: list[DiffPatch], dry_run: bool = False
    ) -> DiffEngineResult:
        """Apply multiple diff patches sequentially."""
        logs: list[str] = []
        results: list[PatchApplyResult] = []

        for patch in patches:
            result = self.apply(patch, dry_run=dry_run)
            results.append(result)
            logs.append(f"[{result.status}] {result.target}: {result.message}")

        overall = (
            "COMPLETED" if all(r.status == "SUCCESS" for r in results) else "BLOCKED"
        )

        return DiffEngineResult(
            overall_status=overall,
            results=results,
            logs=logs,
        )

    def rollback(self) -> DiffEngineResult:
        """Restore all files from backups."""
        logs: list[str] = []
        results: list[PatchApplyResult] = []

        if not self._backups:
            return DiffEngineResult(
                overall_status="COMPLETED",
                results=[],
                logs=["No backups to restore."],
            )

        for target, backup_path in self._backups.items():
            try:
                resolved = self._workspace / target
                shutil.copy2(backup_path, resolved)
                results.append(
                    PatchApplyResult(
                        target=target,
                        status="SUCCESS",
                        message=f"Restored from {backup_path}",
                    )
                )
                logs.append(f"[SUCCESS] {target}: Restored from backup")
            except Exception as e:
                results.append(
                    PatchApplyResult(
                        target=target,
                        status="ERROR",
                        message=str(e),
                    )
                )
                logs.append(f"[ERROR] {target}: {e}")

        self._backups.clear()

        overall = (
            "COMPLETED" if all(r.status == "SUCCESS" for r in results) else "BLOCKED"
        )

        return DiffEngineResult(
            overall_status=overall,
            results=results,
            logs=logs,
        )

    def _validate_path(self, target: str) -> Path:
        """Validate path security: allowed files + workspace boundary."""
        if target not in self._allowed_files:
            raise SecurityError(f"File not allowed: {target}")

        resolved = (self._workspace / target).resolve()
        workspace_str = str(self._workspace)
        resolved_str = str(resolved)

        if not resolved_str.startswith(workspace_str):
            raise SecurityError(f"Path traversal detected: {target}")

        return resolved
