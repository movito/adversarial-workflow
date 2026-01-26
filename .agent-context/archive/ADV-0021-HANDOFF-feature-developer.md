# ADV-0021 Task Starter

## Quick Context

Fix: The CLI doesn't load `.env` files at startup, causing custom evaluators with non-OpenAI API keys to fail. One-line fix + tests.

**Branch**: `fix/adv-0021-env-loading`
**Base**: `main`
**Target**: v0.6.1 patch release

## The Bug

```bash
# User has GEMINI_API_KEY in .env
echo "GEMINI_API_KEY=AIzaSy..." > .env

# But this fails:
adversarial athena task.md
# Error: GEMINI_API_KEY not set
```

**Root cause**: `load_dotenv()` is imported but only called in `quickstart()`, not at CLI startup.

## Create Branch

```bash
git checkout main
git pull origin main
git checkout -b fix/adv-0021-env-loading
```

## Implementation (3 steps)

### Step 1: Fix main() in cli.py

Location: `adversarial_workflow/cli.py`, line ~2867

**Current:**
```python
def main():
    """Main CLI entry point."""
    import logging

    from adversarial_workflow.evaluators import (
```

**Change to:**
```python
def main():
    """Main CLI entry point."""
    import logging
    from dotenv import load_dotenv

    # Load .env file before any commands run
    load_dotenv()

    from adversarial_workflow.evaluators import (
```

### Step 2: Create Tests

Create `tests/test_env_loading.py`:

```python
"""Tests for .env file loading at CLI startup."""

import os
import subprocess
import sys


class TestEnvFileLoading:
    """Tests for automatic .env loading."""

    def test_env_loaded_before_evaluator_commands(self, tmp_path, monkeypatch):
        """API keys in .env are available to evaluator commands."""
        # Create .env with test key
        (tmp_path / ".env").write_text("TEST_API_KEY=secret-test-value\n")

        # Create minimal evaluator config
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "test.yml").write_text("""
name: test
description: Test evaluator
model: gpt-4o-mini
api_key_env: TEST_API_KEY
prompt: Test prompt
output_suffix: TEST
""")

        monkeypatch.chdir(tmp_path)
        # Ensure key is NOT in current environment
        monkeypatch.delenv("TEST_API_KEY", raising=False)

        # list-evaluators should work (loads .env, discovers evaluator)
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "list-evaluators"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert result.returncode == 0
        assert "test" in result.stdout

    def test_env_loaded_for_builtin_commands(self, tmp_path, monkeypatch):
        """.env is loaded even for built-in commands."""
        # Create .env with OpenAI key
        (tmp_path / ".env").write_text("OPENAI_API_KEY=sk-test-key\n")

        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        # check command should find the key from .env
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "check"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        # Should mention OpenAI (found from .env)
        # The check may fail for other reasons but should see the key
        assert "OPENAI" in result.stdout or "openai" in result.stdout.lower()

    def test_missing_env_file_no_error(self, tmp_path, monkeypatch):
        """CLI works fine when no .env file exists."""
        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert result.returncode == 0
        assert "adversarial" in result.stdout.lower()
```

### Step 3: Bump Version to 0.6.1

Update in all three locations:

**pyproject.toml:**
```toml
version = "0.6.1"
```

**adversarial_workflow/__init__.py:**
```python
__version__ = "0.6.1"
```

**adversarial_workflow/cli.py:**
```python
__version__ = "0.6.1"
```

## Testing

```bash
# Run new tests
pytest tests/test_env_loading.py -v

# Run all tests
pytest tests/ -v

# Manual verification
echo "TEST_KEY=hello" > .env
unset TEST_KEY
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('TEST_KEY'))"
# Should print: hello
```

## Files to Modify

| File | Change |
|------|--------|
| `adversarial_workflow/cli.py` | Add `load_dotenv()` at start of `main()` |
| `tests/test_env_loading.py` | Create new test file |
| `pyproject.toml` | Version 0.6.0 → 0.6.1 |
| `adversarial_workflow/__init__.py` | Version 0.6.0 → 0.6.1 |
| `adversarial_workflow/cli.py` | Version 0.6.0 → 0.6.1 |

## Acceptance Criteria

- [ ] `load_dotenv()` called at start of `main()`
- [ ] New tests pass
- [ ] All existing tests pass (166+)
- [ ] Version bumped to 0.6.1

## Post-Implementation

After tests pass, follow the **Post-Implementation Workflow** in the feature-developer agent definition:
1. Commit and push
2. Create PR
3. Monitor CodeRabbit and BugBot feedback
4. Address any issues
5. Create review starter when bots are satisfied

## Resources

- Task spec: `delegation/tasks/2-todo/ADV-0021-env-loading-fix.md`
- Bug report: `docs/proposals/ADVERSARIAL-WORKFLOW-ENV-LOADING.md`
- CLI main(): `adversarial_workflow/cli.py:2867`
