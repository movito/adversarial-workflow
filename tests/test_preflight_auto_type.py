"""Tests for preflight-check.sh auto-type detection from task spec.

Tests the logic that reads **Type** from task spec frontmatter and maps it
to preflight modes (sync, docs), with explicit --type always winning.
"""

import os
import subprocess
import tempfile

# The bash snippet under test — mirrors the auto-detect block in preflight-check.sh
AUTO_TYPE_SNIPPET = r"""
TASK_TYPE="$1"
TASK_FILE="$2"

if [ -z "$TASK_TYPE" ] && [ -n "$TASK_FILE" ]; then
    SPEC_TYPE=$(grep '^\*\*Type\*\*:' "$TASK_FILE" | sed 's/.*: *//')
    case "$SPEC_TYPE" in
        "Upstream Sync") TASK_TYPE="sync" ;;
        "Documentation") TASK_TYPE="docs" ;;
    esac
fi

echo "$TASK_TYPE"
"""


def _run_auto_type(task_type: str, task_file_content: str | None) -> str:
    """Run the auto-type bash snippet and return the resulting TASK_TYPE."""
    file_path = ""
    tmp_path = None
    try:
        if task_file_content is not None:
            fd, tmp_path = tempfile.mkstemp(suffix=".md")
            with os.fdopen(fd, "w") as f:
                f.write(task_file_content)
            file_path = tmp_path

        result = subprocess.run(
            ["bash", "-c", AUTO_TYPE_SNIPPET, "--", task_type, file_path],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip()
    finally:
        if tmp_path is not None:
            os.unlink(tmp_path)


class TestPreflightAutoType:
    """Test auto-type detection from task spec **Type** field."""

    def test_auto_detect_upstream_sync(self):
        """Task with **Type**: Upstream Sync maps to sync mode."""
        result = _run_auto_type("", "# ADV-9999\n\n**Status**: Todo\n**Type**: Upstream Sync\n")
        assert result == "sync"

    def test_auto_detect_documentation(self):
        """Task with **Type**: Documentation maps to docs mode."""
        result = _run_auto_type("", "# ADV-9999\n\n**Status**: Todo\n**Type**: Documentation\n")
        assert result == "docs"

    def test_explicit_type_overrides_spec(self):
        """Explicit --type flag overrides task spec auto-detection."""
        result = _run_auto_type("code", "# ADV-9999\n\n**Type**: Upstream Sync\n")
        assert result == "code"

    def test_unmapped_type_falls_through(self):
        """Unmapped type values (Enhancement, Bug Fix) leave TASK_TYPE empty."""
        result = _run_auto_type("", "# ADV-9999\n\n**Type**: Enhancement\n")
        assert result == ""

    def test_bug_fix_falls_through(self):
        """Bug Fix type falls through to code-changes heuristic."""
        result = _run_auto_type("", "# ADV-9999\n\n**Type**: Bug Fix\n")
        assert result == ""

    def test_no_task_file(self):
        """No task file found — TASK_TYPE stays empty for heuristic."""
        result = _run_auto_type("", None)
        assert result == ""

    def test_no_type_field_in_spec(self):
        """Task file exists but has no **Type** field — falls through."""
        result = _run_auto_type("", "# ADV-9999\n\n**Status**: Todo\n")
        assert result == ""
