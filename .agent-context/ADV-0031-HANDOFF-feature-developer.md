# ADV-0031 Handoff: Feature Developer

**Created**: 2026-02-05
**Task**: Library Evaluator Execution
**Branch**: Create `feat/adv-0031-evaluator-execution`

---

## Quick Context

Users can install library evaluators but can't run them. Add `--evaluator <name>` flag to `adversarial evaluate` to select and run installed evaluators.

---

## Implementation Guide

### Step 1: Add CLI Argument

In `adversarial_workflow/cli.py`, find the evaluate subparser and add:

```python
# Find this section (around line 3050-3060):
evaluate_parser = subparsers.add_parser(
    "evaluate",
    help="Run Phase 1: Plan evaluation",
)
evaluate_parser.add_argument(
    "task_file",
    help="Path to task file to evaluate",
)

# ADD these arguments:
evaluate_parser.add_argument(
    "--evaluator", "-e",
    help="Use a specific evaluator (from .adversarial/evaluators/)",
    metavar="NAME",
)
```

### Step 2: Modify evaluate() Function

Find the `evaluate()` function (around line 1837) and modify:

```python
def evaluate(task_file: str, evaluator_name: str | None = None) -> int:
    """Run Phase 1: Plan evaluation.

    Args:
        task_file: Path to task file to evaluate
        evaluator_name: Optional evaluator name (uses config.yml if not specified)
    """

    # If evaluator specified, use native execution
    if evaluator_name:
        return run_with_evaluator(task_file, evaluator_name)

    # Otherwise, use existing shell script approach
    # ... existing code ...
```

### Step 3: Create run_with_evaluator() Function

Add this new function before `evaluate()`:

```python
def run_with_evaluator(task_file: str, evaluator_name: str) -> int:
    """Run evaluation using a specific evaluator.

    Args:
        task_file: Path to task file
        evaluator_name: Name of evaluator (from .adversarial/evaluators/)

    Returns:
        0 on success, 1 on failure
    """
    from adversarial_workflow.evaluators import discover_local_evaluators
    from adversarial_workflow.evaluators.models import ModelResolver

    # Discover available evaluators
    evaluators = discover_local_evaluators()

    if not evaluators:
        print(f"{RED}Error: No evaluators installed.{RESET}")
        print("Install evaluators with: adversarial library install <name>")
        return 1

    # Find requested evaluator (supports aliases)
    if evaluator_name not in evaluators:
        print(f"{RED}Error: Evaluator '{evaluator_name}' not found.{RESET}")
        print()
        print("Available evaluators:")
        seen = set()
        for name, config in sorted(evaluators.items()):
            if id(config) not in seen:
                print(f"  {config.name}")
                seen.add(id(config))
        return 1

    config = evaluators[evaluator_name]

    # Resolve model
    model = config.model
    api_key_env = config.api_key_env

    if config.model_requirement:
        try:
            resolver = ModelResolver()
            resolved = resolver.resolve(config.model_requirement)
            model = resolved.model_id
            api_key_env = resolved.api_key_env
        except Exception as e:
            if not model:
                print(f"{RED}Error: Could not resolve model requirement: {e}{RESET}")
                return 1
            # Fall back to legacy model field
            print(f"{YELLOW}Warning: Model resolution failed, using fallback: {model}{RESET}")

    # Check API key
    api_key = os.environ.get(api_key_env, "")
    if not api_key:
        print(f"{RED}Error: {api_key_env} not set.{RESET}")
        print(f"Add to .env: {api_key_env}=your-key-here")
        return 1

    # Validate task file
    if not os.path.exists(task_file):
        print(f"{RED}Error: Task file not found: {task_file}{RESET}")
        return 1

    # Determine output file
    task_name = Path(task_file).stem
    output_suffix = config.output_suffix or "-EVALUATION.md"
    log_dir = Path(".adversarial/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    output_file = log_dir / f"{task_name}{output_suffix}"

    # Display info
    print(f"{BOLD}Evaluator:{RESET} {config.name}")
    print(f"{BOLD}Model:{RESET} {model}")
    print(f"{BOLD}Task:{RESET} {task_file}")
    print()

    # Run aider
    import subprocess

    cmd = [
        "aider",
        "--model", model,
        "--yes",
        "--no-detect-urls",
        "--no-git",
        "--map-tokens", "0",
        "--no-gitignore",
        "--read", task_file,
        "--message", config.prompt,
        "--no-auto-commits",
    ]

    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except FileNotFoundError:
        print(f"{RED}Error: aider not found. Install with: pip install aider-chat{RESET}")
        return 1
```

### Step 4: Update CLI Main Handler

Find the evaluate command handler (around line 3382):

```python
# Change from:
elif args.command == "evaluate":
    return evaluate(args.task_file)

# To:
elif args.command == "evaluate":
    return evaluate(args.task_file, evaluator_name=getattr(args, 'evaluator', None))
```

---

## Test Scaffolding

Create `tests/test_evaluate_with_evaluator.py`:

```python
"""Tests for evaluate command with --evaluator flag."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from adversarial_workflow.cli import evaluate, run_with_evaluator


class TestRunWithEvaluator:
    """Test run_with_evaluator function."""

    @pytest.fixture
    def mock_evaluator(self, tmp_path):
        """Create a mock evaluator file."""
        evaluators_dir = tmp_path / ".adversarial" / "evaluators"
        evaluators_dir.mkdir(parents=True)

        evaluator_file = evaluators_dir / "test-evaluator.yml"
        evaluator_file.write_text('''
name: test-evaluator
description: Test evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: |
  Review this task.
output_suffix: -TEST-EVAL.md
''')
        return tmp_path

    @pytest.fixture
    def mock_task_file(self, tmp_path):
        """Create a mock task file."""
        task = tmp_path / "TASK-001.md"
        task.write_text("# Task\nDo something.")
        return task

    def test_evaluator_not_found(self, tmp_path, monkeypatch):
        """Test error when evaluator doesn't exist."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".adversarial" / "evaluators").mkdir(parents=True)

        result = run_with_evaluator("task.md", "nonexistent")
        assert result == 1

    @patch("adversarial_workflow.cli.subprocess.run")
    def test_evaluator_runs_aider(self, mock_run, mock_evaluator, mock_task_file, monkeypatch):
        """Test evaluator runs aider with correct model."""
        monkeypatch.chdir(mock_evaluator)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        mock_run.return_value = MagicMock(returncode=0)

        result = run_with_evaluator(str(mock_task_file), "test-evaluator")

        assert result == 0
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "--model" in cmd
        assert "gpt-4o" in cmd


class TestEvaluateWithFlag:
    """Test evaluate() with --evaluator flag."""

    @patch("adversarial_workflow.cli.run_with_evaluator")
    def test_evaluator_flag_calls_run_with_evaluator(self, mock_run):
        """Test --evaluator flag routes to run_with_evaluator."""
        mock_run.return_value = 0

        result = evaluate("task.md", evaluator_name="my-evaluator")

        mock_run.assert_called_once_with("task.md", "my-evaluator")
        assert result == 0

    @patch("adversarial_workflow.cli.os.path.exists")
    def test_no_flag_uses_shell_script(self, mock_exists):
        """Test no --evaluator flag uses existing shell script."""
        mock_exists.return_value = False

        # Without evaluator_name, should try shell script
        result = evaluate("task.md", evaluator_name=None)

        # Will fail because script doesn't exist, but proves path taken
        assert result == 1
```

---

## Verification Checklist

- [ ] `adversarial evaluate --evaluator test-evaluator task.md` works
- [ ] `-e` short form works
- [ ] Error message when evaluator not found lists available options
- [ ] Without `--evaluator`, existing behavior unchanged
- [ ] Model resolution works for `model_requirement` evaluators
- [ ] Falls back to `model` field when resolution fails
- [ ] API key validated before running
- [ ] All existing tests pass
- [ ] New tests pass
- [ ] `./scripts/ci-check.sh` passes

---

## Commit Message Template

```
feat(cli): Add --evaluator flag to evaluate command

- Add -e/--evaluator flag to select installed evaluators
- Create run_with_evaluator() for native evaluator execution
- Support model_requirement resolution via ModelResolver
- Backward compatible: no flag uses existing shell script

Enables running library-installed evaluators:
  adversarial evaluate --evaluator plan-evaluator task.md

Part of library evaluator integration (ADV-0031).
```

---

## After Implementation

1. Run full test suite: `pytest tests/ -v`
2. Run CI check: `./scripts/ci-check.sh`
3. Commit with message above
4. Push and create PR targeting `main`
5. Request code review
