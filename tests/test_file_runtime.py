"""Tests for harness/file_runtime.py."""

from harness.file_runtime import FilePatch, SafeFileRuntime


def test_append_to_allowed_file(tmp_path):
    target = tmp_path / "app.py"
    target.write_text("print('hello')\n")
    runtime = SafeFileRuntime(tmp_path, ["app.py"])

    patch = FilePatch(target="app.py", content="print('world')\n")
    result = runtime.apply_patch(patch)

    assert result.status == "SUCCESS"
    assert "app.py" in result.target
    assert target.read_text() == "print('hello')\nprint('world')\n"


def test_blocked_for_disallowed_file(tmp_path):
    target = tmp_path / "secret.py"
    target.write_text("secret")
    runtime = SafeFileRuntime(tmp_path, ["app.py"])

    patch = FilePatch(target="secret.py", content="hack")
    result = runtime.apply_patch(patch)

    assert result.status == "BLOCKED"
    assert "not allowed" in result.message
    assert target.read_text() == "secret"


def test_blocked_for_path_traversal(tmp_path):
    runtime = SafeFileRuntime(tmp_path, ["../../etc/passwd"])

    patch = FilePatch(target="../../etc/passwd", content="hack")
    result = runtime.apply_patch(patch)

    assert result.status == "BLOCKED"
    assert "traversal" in result.message.lower() or "not allowed" in result.message


def test_backup_created(tmp_path):
    target = tmp_path / "app.py"
    target.write_text("original\n")
    runtime = SafeFileRuntime(tmp_path, ["app.py"])

    patch = FilePatch(target="app.py", content="added\n")
    result = runtime.apply_patch(patch)

    assert result.status == "SUCCESS"
    assert result.backup_path != ""
    assert (tmp_path / "app.py.bak").exists()
    assert (tmp_path / "app.py.bak").read_text() == "original\n"


def test_no_backup_for_new_file(tmp_path):
    runtime = SafeFileRuntime(tmp_path, ["new.py"])

    patch = FilePatch(target="new.py", content="new content\n")
    result = runtime.apply_patch(patch)

    assert result.status == "SUCCESS"
    assert result.backup_path == ""
    assert (tmp_path / "new.py").exists()
    assert (tmp_path / "new.py").read_text() == "new content\n"


def test_apply_patches_multiple_files(tmp_path):
    (tmp_path / "a.py").write_text("a\n")
    (tmp_path / "b.py").write_text("b\n")
    runtime = SafeFileRuntime(tmp_path, ["a.py", "b.py"])

    patches = [
        FilePatch(target="a.py", content="a2\n"),
        FilePatch(target="b.py", content="b2\n"),
    ]
    result = runtime.apply_patches(patches)

    assert result.overall_status == "COMPLETED"
    assert len(result.results) == 2
    assert all(r.status == "SUCCESS" for r in result.results)
    assert (tmp_path / "a.py").read_text() == "a\na2\n"
    assert (tmp_path / "b.py").read_text() == "b\nb2\n"


def test_apply_patches_partial_failure(tmp_path):
    (tmp_path / "a.py").write_text("a\n")
    runtime = SafeFileRuntime(tmp_path, ["a.py"])

    patches = [
        FilePatch(target="a.py", content="a2\n"),
        FilePatch(target="blocked.py", content="nope\n"),
    ]
    result = runtime.apply_patches(patches)

    assert result.overall_status == "BLOCKED"
    assert result.results[0].status == "SUCCESS"
    assert result.results[1].status == "BLOCKED"


def test_logs_not_empty(tmp_path):
    (tmp_path / "a.py").write_text("a\n")
    runtime = SafeFileRuntime(tmp_path, ["a.py"])

    patches = [FilePatch(target="a.py", content="b\n")]
    result = runtime.apply_patches(patches)

    assert len(result.logs) > 0
    assert "SUCCESS" in result.logs[0]


def test_unknown_operation(tmp_path):
    (tmp_path / "a.py").write_text("a\n")
    runtime = SafeFileRuntime(tmp_path, ["a.py"])

    patch = FilePatch(target="a.py", content="b", operation="delete")
    result = runtime.apply_patch(patch)

    assert result.status == "ERROR"
    assert "Unknown operation" in result.message


def test_relative_path_allowed(tmp_path):
    subdir = tmp_path / "src"
    subdir.mkdir()
    (subdir / "app.py").write_text("code\n")
    runtime = SafeFileRuntime(tmp_path, ["src/app.py"])

    patch = FilePatch(target="src/app.py", content="more\n")
    result = runtime.apply_patch(patch)

    assert result.status == "SUCCESS"
    assert (subdir / "app.py").read_text() == "code\nmore\n"


def test_absolute_path_blocked(tmp_path):
    runtime = SafeFileRuntime(tmp_path, ["/etc/passwd"])

    patch = FilePatch(target="/etc/passwd", content="hack")
    result = runtime.apply_patch(patch)

    assert result.status == "BLOCKED"


def test_dry_run_does_not_modify_file(tmp_path):
    target = tmp_path / "app.py"
    target.write_text("original\n")
    runtime = SafeFileRuntime(tmp_path, ["app.py"])

    patch = FilePatch(target="app.py", content="added\n")
    result = runtime.apply_patch(patch, dry_run=True)

    assert result.status == "SUCCESS"
    assert target.read_text() == "original\n"


def test_dry_run_no_backup(tmp_path):
    target = tmp_path / "app.py"
    target.write_text("original\n")
    runtime = SafeFileRuntime(tmp_path, ["app.py"])

    patch = FilePatch(target="app.py", content="added\n")
    result = runtime.apply_patch(patch, dry_run=True)

    assert result.backup_path == ""
    assert not (tmp_path / "app.py.bak").exists()


def test_dry_run_message_prefix(tmp_path):
    runtime = SafeFileRuntime(tmp_path, ["app.py"])

    patch = FilePatch(target="app.py", content="x\n")
    result = runtime.apply_patch(patch, dry_run=True)

    assert "[DRY-RUN]" in result.message


def test_apply_message_prefix(tmp_path):
    target = tmp_path / "app.py"
    target.write_text("x\n")
    runtime = SafeFileRuntime(tmp_path, ["app.py"])

    patch = FilePatch(target="app.py", content="y\n")
    result = runtime.apply_patch(patch, dry_run=False)

    assert "[APPLY]" in result.message


def test_dry_run_patches_multiple_files(tmp_path):
    (tmp_path / "a.py").write_text("a\n")
    (tmp_path / "b.py").write_text("b\n")
    runtime = SafeFileRuntime(tmp_path, ["a.py", "b.py"])

    patches = [
        FilePatch(target="a.py", content="a2\n"),
        FilePatch(target="b.py", content="b2\n"),
    ]
    result = runtime.apply_patches(patches, dry_run=True)

    assert result.overall_status == "COMPLETED"
    assert (tmp_path / "a.py").read_text() == "a\n"
    assert (tmp_path / "b.py").read_text() == "b\n"
