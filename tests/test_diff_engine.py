"""Tests for harness/diff_engine.py."""

from harness.diff_engine import DiffPatch, DiffPatchEngine


def test_replace_simple(tmp_path):
    target = tmp_path / "app.py"
    target.write_text('def hello():\n    return "hi"\n')
    engine = DiffPatchEngine(tmp_path, ["app.py"])

    patch = DiffPatch(
        target="app.py",
        search='return "hi"',
        replace='return "hello"',
        description="Change greeting",
    )
    result = engine.apply(patch, dry_run=False)

    assert result.status == "SUCCESS"
    assert "[APPLY]" in result.message
    assert target.read_text() == 'def hello():\n    return "hello"\n'


def test_search_not_found(tmp_path):
    target = tmp_path / "app.py"
    target.write_text("def hello():\n    pass\n")
    engine = DiffPatchEngine(tmp_path, ["app.py"])

    patch = DiffPatch(
        target="app.py",
        search="nonexistent",
        replace="replacement",
        description="Bad search",
    )
    result = engine.apply(patch, dry_run=False)

    assert result.status == "NOT_FOUND"
    assert "not found" in result.message
    assert target.read_text() == "def hello():\n    pass\n"


def test_file_not_found(tmp_path):
    engine = DiffPatchEngine(tmp_path, ["missing.py"])

    patch = DiffPatch(
        target="missing.py",
        search="x",
        replace="y",
        description="Missing file",
    )
    result = engine.apply(patch, dry_run=False)

    assert result.status == "NOT_FOUND"


def test_blocked_disallowed_file(tmp_path):
    target = tmp_path / "secret.py"
    target.write_text("secret")
    engine = DiffPatchEngine(tmp_path, ["app.py"])

    patch = DiffPatch(
        target="secret.py",
        search="secret",
        replace="hacked",
        description="Bad",
    )
    result = engine.apply(patch, dry_run=False)

    assert result.status == "BLOCKED"
    assert target.read_text() == "secret"


def test_blocked_path_traversal(tmp_path):
    engine = DiffPatchEngine(tmp_path, ["../../etc/passwd"])

    patch = DiffPatch(
        target="../../etc/passwd",
        search="root",
        replace="hacked",
        description="Bad",
    )
    result = engine.apply(patch, dry_run=False)

    assert result.status == "BLOCKED"


def test_dry_run_does_not_modify(tmp_path):
    target = tmp_path / "app.py"
    target.write_text("original\n")
    engine = DiffPatchEngine(tmp_path, ["app.py"])

    patch = DiffPatch(
        target="app.py",
        search="original",
        replace="changed",
        description="Test",
    )
    result = engine.apply(patch, dry_run=True)

    assert result.status == "SUCCESS"
    assert "[DRY-RUN]" in result.message
    assert target.read_text() == "original\n"


def test_dry_run_search_not_found(tmp_path):
    target = tmp_path / "app.py"
    target.write_text("content\n")
    engine = DiffPatchEngine(tmp_path, ["app.py"])

    patch = DiffPatch(
        target="app.py",
        search="missing",
        replace="x",
        description="Test",
    )
    result = engine.apply(patch, dry_run=True)

    assert result.status == "NOT_FOUND"


def test_backup_created(tmp_path):
    target = tmp_path / "app.py"
    target.write_text("original\n")
    engine = DiffPatchEngine(tmp_path, ["app.py"])

    patch = DiffPatch(
        target="app.py",
        search="original",
        replace="changed",
        description="Test",
    )
    result = engine.apply(patch, dry_run=False)

    assert result.backup_path != ""
    assert (tmp_path / "app.py.bak").exists()
    assert (tmp_path / "app.py.bak").read_text() == "original\n"


def test_rollback_restores_file(tmp_path):
    target = tmp_path / "app.py"
    target.write_text("original\n")
    engine = DiffPatchEngine(tmp_path, ["app.py"])

    patch = DiffPatch(
        target="app.py",
        search="original",
        replace="changed",
        description="Test",
    )
    engine.apply(patch, dry_run=False)
    assert target.read_text() == "changed\n"

    rollback_result = engine.rollback()

    assert rollback_result.overall_status == "COMPLETED"
    assert target.read_text() == "original\n"


def test_rollback_no_backups(tmp_path):
    engine = DiffPatchEngine(tmp_path, ["app.py"])

    result = engine.rollback()

    assert result.overall_status == "COMPLETED"
    assert "No backups" in result.logs[0]


def test_apply_patches_multiple(tmp_path):
    (tmp_path / "a.py").write_text("old_a\n")
    (tmp_path / "b.py").write_text("old_b\n")
    engine = DiffPatchEngine(tmp_path, ["a.py", "b.py"])

    patches = [
        DiffPatch(
            target="a.py",
            search="old_a",
            replace="new_a",
            description="Update a",
        ),
        DiffPatch(
            target="b.py",
            search="old_b",
            replace="new_b",
            description="Update b",
        ),
    ]
    result = engine.apply_patches(patches, dry_run=False)

    assert result.overall_status == "COMPLETED"
    assert len(result.results) == 2
    assert (tmp_path / "a.py").read_text() == "new_a\n"
    assert (tmp_path / "b.py").read_text() == "new_b\n"


def test_apply_patches_partial_failure(tmp_path):
    (tmp_path / "a.py").write_text("old_a\n")
    engine = DiffPatchEngine(tmp_path, ["a.py"])

    patches = [
        DiffPatch(
            target="a.py",
            search="old_a",
            replace="new_a",
            description="Update a",
        ),
        DiffPatch(
            target="blocked.py",
            search="x",
            replace="y",
            description="Blocked",
        ),
    ]
    result = engine.apply_patches(patches, dry_run=False)

    assert result.overall_status == "BLOCKED"
    assert result.results[0].status == "SUCCESS"
    assert result.results[1].status == "BLOCKED"


def test_multiple_replaces_same_file(tmp_path):
    target = tmp_path / "app.py"
    target.write_text("aaa\n")
    engine = DiffPatchEngine(tmp_path, ["app.py"])

    patch = DiffPatch(
        target="app.py",
        search="a",
        replace="b",
        description="Replace all a with b",
    )
    result = engine.apply(patch, dry_run=False)

    assert result.status == "SUCCESS"
    assert target.read_text() == "bbb\n"
