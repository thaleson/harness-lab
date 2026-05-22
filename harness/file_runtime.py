"""Safe file runtime with sandboxed file modifications."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path


class SecurityError(Exception):
    """Raised when a security validation fails."""


@dataclass
class FilePatch:
    """A patch to apply to a file."""

    target: str
    content: str
    operation: str = "append"  # future: "write", "diff"


@dataclass
class FileOperationResult:
    """Result of applying a single file patch."""

    target: str
    status: str  # "SUCCESS", "BLOCKED", "ERROR"
    message: str
    backup_path: str = ""


@dataclass
class FileRuntimeResult:
    """Result of applying multiple patches."""

    overall_status: str  # "COMPLETED", "BLOCKED"
    results: list[FileOperationResult] = field(default_factory=list)
    logs: list[str] = field(default_factory=list)


class SafeFileRuntime:
    """Executes file modifications in a sandboxed manner."""

    def __init__(self, workspace: Path, allowed_files: list[str]) -> None:
        self._workspace = workspace.resolve()
        self._allowed_files = set(allowed_files)

    def apply_patch(
        self, patch: FilePatch, dry_run: bool = False
    ) -> FileOperationResult:
        """Apply a single patch with security validation."""
        try:
            resolved = self._validate_path(patch.target)
        except SecurityError as e:
            return FileOperationResult(
                target=patch.target,
                status="BLOCKED",
                message=str(e),
            )

        # Dry-run: validate only, no modifications
        if dry_run:
            return FileOperationResult(
                target=patch.target,
                status="SUCCESS",
                message=f"[DRY-RUN] Would apply {patch.operation} to {patch.target}",
            )

        backup_path = ""

        try:
            # Create backup if file exists
            if resolved.exists():
                backup_path = str(resolved) + ".bak"
                shutil.copy2(resolved, backup_path)

            # Apply operation
            if patch.operation == "append":
                self._apply_append(resolved, patch.content)
            else:
                return FileOperationResult(
                    target=patch.target,
                    status="ERROR",
                    message=f"Unknown operation: {patch.operation}",
                    backup_path=backup_path,
                )

            return FileOperationResult(
                target=patch.target,
                status="SUCCESS",
                message=f"[APPLY] Applied {patch.operation} to {patch.target}",
                backup_path=backup_path,
            )

        except Exception as e:
            return FileOperationResult(
                target=patch.target,
                status="ERROR",
                message=str(e),
                backup_path=backup_path,
            )

    def apply_patches(
        self, patches: list[FilePatch], dry_run: bool = False
    ) -> FileRuntimeResult:
        """Apply multiple patches sequentially."""
        logs: list[str] = []
        results: list[FileOperationResult] = []

        for patch in patches:
            result = self.apply_patch(patch, dry_run=dry_run)
            results.append(result)
            logs.append(f"[{result.status}] {result.target}: {result.message}")

        overall = (
            "COMPLETED" if all(r.status == "SUCCESS" for r in results) else "BLOCKED"
        )

        return FileRuntimeResult(
            overall_status=overall,
            results=results,
            logs=logs,
        )

    def _validate_path(self, target: str) -> Path:
        """Validate path security: allowed files + workspace boundary."""
        # Check allowed files
        if target not in self._allowed_files:
            raise SecurityError(f"File not allowed: {target}")

        # Resolve and check workspace boundary
        resolved = (self._workspace / target).resolve()
        workspace_str = str(self._workspace)
        resolved_str = str(resolved)

        if not resolved_str.startswith(workspace_str):
            raise SecurityError(f"Path traversal detected: {target}")

        return resolved

    @staticmethod
    def _apply_append(path: Path, content: str) -> None:
        """Append content to a file."""
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
