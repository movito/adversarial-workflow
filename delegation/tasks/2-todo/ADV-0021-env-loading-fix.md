# ADV-0021: Fix .env Loading for Custom Evaluators

**Status**: Todo
**Priority**: High
**Estimated Effort**: 30 minutes
**Target Version**: v0.6.1
**Reported By**: ombruk-idrettsbygg project

## Summary

The CLI does not load `.env` files at startup, causing custom evaluators with non-OpenAI API keys to fail even when keys are properly configured in `.env`.

## Problem

Users configuring custom evaluators with `api_key_env: GEMINI_API_KEY` (or other non-OpenAI keys) get errors even when the key exists in `.env`:

```bash
adversarial athena task.md
# Error: GEMINI_API_KEY not set
#    Set in .env or export GEMINI_API_KEY=your-key
```

The error message is misleading—it suggests `.env` works when it doesn't.

## Root Cause

`load_dotenv()` is imported but only called in specific functions (`quickstart`, `init_interactive`), not at CLI startup in `main()`.

| Command | Loads .env? |
|---------|-------------|
| `adversarial quickstart` | ✅ Yes |
| `adversarial athena task.md` | ❌ No |
| `adversarial evaluate task.md` | ❌ No |

## Solution

Add `load_dotenv()` at the start of `main()` in `cli.py`:

```python
def main():
    """Main CLI entry point."""
    import logging
    from dotenv import load_dotenv

    load_dotenv()  # Load .env before any commands run

    from adversarial_workflow.evaluators import (
        get_all_evaluators,
        run_evaluator,
        BUILTIN_EVALUATORS,
    )
    # ... rest of main()
```

## Implementation

### 1. Update main() in cli.py

Location: `adversarial_workflow/cli.py`, function `main()` (line ~2867)

Add `load_dotenv()` call immediately after the docstring, before any other imports or logic.

### 2. Add Tests

Create tests in `tests/test_env_loading.py`:

```python
"""Tests for .env file loading."""

import os
import subprocess
import sys


class TestEnvLoading:
    """Tests for automatic .env loading."""

    def test_env_file_loaded_for_custom_evaluator(self, tmp_path, monkeypatch):
        """Custom evaluator can read API key from .env file."""
        # Setup .env with test key
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_API_KEY=test-value-12345\n")

        # Setup custom evaluator that uses the key
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "test.yml").write_text("""
name: test
description: Test evaluator
model: gpt-4o-mini
api_key_env: TEST_API_KEY
prompt: Test
output_suffix: TEST
""")

        monkeypatch.chdir(tmp_path)

        # Unset the key from current environment
        monkeypatch.delenv("TEST_API_KEY", raising=False)

        # Run list-evaluators (doesn't need the key, just verifies .env loading)
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "list-evaluators"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert result.returncode == 0
        assert "test" in result.stdout

    def test_env_file_loaded_at_startup(self, tmp_path, monkeypatch):
        """Verify .env is loaded before evaluator discovery."""
        # Create .env with a marker variable
        env_file = tmp_path / ".env"
        env_file.write_text("ADV_TEST_MARKER=loaded\n")

        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("ADV_TEST_MARKER", raising=False)

        # The --help command should still load .env
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
            env={**os.environ, "ADV_TEST_MARKER": ""},  # Clear in subprocess
        )

        assert result.returncode == 0
```

### 3. Update Version

Bump to v0.6.1 in:
- `pyproject.toml`
- `adversarial_workflow/__init__.py`
- `adversarial_workflow/cli.py`

## Acceptance Criteria

- [ ] `load_dotenv()` called at start of `main()`
- [ ] Custom evaluators can read API keys from `.env`
- [ ] Built-in evaluators continue to work
- [ ] All existing tests pass (166+)
- [ ] New tests for .env loading pass
- [ ] Version bumped to 0.6.1

## Testing

```bash
# Manual test
echo "GEMINI_API_KEY=test" > .env
unset GEMINI_API_KEY
adversarial list-evaluators  # Should work

# Run tests
pytest tests/test_env_loading.py -v
pytest tests/ -v
```

## References

- Proposal: `docs/proposals/ADVERSARIAL-WORKFLOW-ENV-LOADING.md`
- Reported by: ombruk-idrettsbygg project
- Affects: v0.6.0 custom evaluator users
