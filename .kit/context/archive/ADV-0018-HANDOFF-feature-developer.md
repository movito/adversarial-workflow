# ADV-0018 Task Starter

## Quick Context

You are implementing dynamic CLI command registration for evaluators. This allows custom evaluators defined in `.adversarial/evaluators/*.yml` to appear as CLI subcommands (e.g., `adversarial athena task.md`).

**Branch**: `feature/adv-0018-cli-dynamic-commands`
**Base**: `main`
**Depends On**: ADV-0015, ADV-0016, ADV-0017 - all merged
**Target Version**: v0.6.0

## Branch Already Created

```bash
git checkout feature/adv-0018-cli-dynamic-commands
```

## Overview

Currently `cli.py` has hardcoded subparsers for `evaluate`, `proofread`, etc. You'll replace this with dynamic registration that:
1. Calls `get_all_evaluators()` at startup
2. Registers each evaluator as a subparser with aliases
3. Routes execution through `run_evaluator()`

## Files to Modify

### 1. Modify `adversarial_workflow/cli.py`

Find the `main()` function (around line 3043). Make these changes:

#### Step 1: Add imports near top of main()

```python
def main():
    # Add these imports at the start of main()
    from adversarial_workflow.evaluators import (
        get_all_evaluators,
        run_evaluator,
        BUILTIN_EVALUATORS,
    )
    import logging
    logger = logging.getLogger(__name__)
```

#### Step 2: Define static commands set

After the imports, define commands that cannot be overridden:

```python
    # Commands that cannot be overridden by evaluators
    STATIC_COMMANDS = {
        "init", "check", "doctor", "health", "quickstart",
        "agent", "split", "validate"
    }
```

#### Step 3: Replace hardcoded evaluator subparsers

Find where `evaluate`, `proofread`, `review` subparsers are created. Replace with dynamic registration:

```python
    # Dynamic evaluator registration
    try:
        evaluators = get_all_evaluators()
    except Exception as e:
        logger.warning(f"Evaluator discovery failed: {e}")
        evaluators = BUILTIN_EVALUATORS

    registered_configs = set()  # Track by id() to avoid duplicate alias registration

    for name, config in evaluators.items():
        # Skip if name conflicts with static command
        if name in STATIC_COMMANDS:
            logger.warning(f"Evaluator '{name}' conflicts with CLI command; skipping")
            continue

        # Skip if this config was already registered (aliases share config object)
        if id(config) in registered_configs:
            continue
        registered_configs.add(id(config))

        # Create subparser for this evaluator
        eval_parser = subparsers.add_parser(
            config.name,
            help=config.description,
            aliases=config.aliases if config.aliases else [],
        )
        eval_parser.add_argument("file", help="File to evaluate")
        eval_parser.add_argument(
            "--timeout", "-t",
            type=int,
            default=180,
            help="Timeout in seconds (default: 180)"
        )
        # Store config for later execution
        eval_parser.set_defaults(evaluator_config=config)
```

#### Step 4: Update command dispatch

Find the command dispatch section (where `if args.command == "init":` etc.). Add evaluator handling:

```python
    # After parsing args
    if not args.command:
        parser.print_help()
        return 0

    # Check for evaluator command first (has evaluator_config attribute)
    if hasattr(args, "evaluator_config"):
        return run_evaluator(
            args.evaluator_config,
            args.file,
            timeout=args.timeout,
        )

    # Then handle static commands
    if args.command == "init":
        # ... existing init logic ...
```

#### Step 5: Remove old hardcoded evaluate/proofread/review dispatch

The old dispatch like:
```python
elif args.command == "evaluate":
    return evaluate(args.file)
```

Can be removed - these now go through the dynamic evaluator path.

### 2. Create `tests/test_cli_dynamic_commands.py`

```python
"""Tests for dynamic CLI command registration."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestDynamicCommandRegistration:
    """Test dynamic evaluator command registration."""

    def test_builtin_evaluators_in_help(self):
        """Built-in evaluators appear in --help."""
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "evaluate" in result.stdout
        assert "proofread" in result.stdout
        assert "review" in result.stdout

    def test_local_evaluator_in_help(self, tmp_path, monkeypatch):
        """Local evaluator appears in --help output."""
        # Setup: Create local evaluator
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "custom.yml").write_text("""
name: custom
description: Custom test evaluator
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: CUSTOM-TEST
""")
        # Also need config.yml for init check
        (tmp_path / ".adversarial" / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        assert "custom" in result.stdout
        assert "Custom test evaluator" in result.stdout

    def test_static_command_not_overridden(self, tmp_path, monkeypatch):
        """Static commands cannot be overridden by evaluators."""
        # Create evaluator named 'init' (should be skipped)
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "init.yml").write_text("""
name: init
description: This should not override init
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test
output_suffix: TEST
""")
        (tmp_path / ".adversarial" / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        # 'init' should still be the setup command, not an evaluator
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "init", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        # Init help should mention project setup, not evaluation
        assert "Initialize" in result.stdout or "setup" in result.stdout.lower()


class TestEvaluatorExecution:
    """Test evaluator command execution."""

    def test_evaluator_routes_to_run_evaluator(self, tmp_path, monkeypatch):
        """Evaluator command calls run_evaluator with correct config."""
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        # Create evaluator
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "myeval.yml").write_text("""
name: myeval
description: My evaluator
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Evaluate this
output_suffix: MY-EVAL
""")
        (tmp_path / ".adversarial" / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        with patch("adversarial_workflow.evaluators.runner.run_evaluator") as mock_run:
            mock_run.return_value = 0

            # Import and run main
            from adversarial_workflow.cli import main
            import sys

            with patch.object(sys, "argv", ["adversarial", "myeval", "test.md"]):
                # This would call run_evaluator
                pass  # Full integration test would verify this

    def test_timeout_flag_passed(self, tmp_path, monkeypatch):
        """--timeout flag is passed to run_evaluator."""
        # Similar setup, verify timeout=300 is passed when --timeout 300 used
        pass  # Implementation left to feature-developer


class TestAliasSupport:
    """Test evaluator alias support."""

    def test_alias_appears_in_help(self, tmp_path, monkeypatch):
        """Evaluator aliases appear in help."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "knowledge.yml").write_text("""
name: knowledge
description: Knowledge evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Evaluate knowledge
output_suffix: KNOWLEDGE
aliases:
  - know
  - k
""")
        (tmp_path / ".adversarial" / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        # Aliases should be shown
        assert "knowledge" in result.stdout


class TestBackwardsCompatibility:
    """Test backwards compatibility."""

    def test_evaluate_command_works(self):
        """adversarial evaluate --help still works."""
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "evaluate", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "file" in result.stdout.lower()

    def test_proofread_command_works(self):
        """adversarial proofread --help still works."""
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "proofread", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_review_command_works(self):
        """adversarial review --help still works."""
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "review", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestGracefulDegradation:
    """Test graceful degradation on errors."""

    def test_discovery_failure_falls_back_to_builtins(self, monkeypatch):
        """If discovery fails, CLI still works with built-ins."""
        # Mock get_all_evaluators to raise exception
        with patch("adversarial_workflow.evaluators.get_all_evaluators") as mock_get:
            mock_get.side_effect = Exception("Discovery failed")

            result = subprocess.run(
                [sys.executable, "-m", "adversarial_workflow.cli", "--help"],
                capture_output=True,
                text=True,
            )
            # Should still show built-in evaluators
            assert "evaluate" in result.stdout
```

## Verify

```bash
# Run all tests
pytest tests/ -v

# Run just the new tests
pytest tests/test_cli_dynamic_commands.py -v

# Manual verification
adversarial --help  # Should show evaluate, proofread, review

# Create a local evaluator and test
mkdir -p .adversarial/evaluators
cat > .adversarial/evaluators/test.yml << 'EOF'
name: test
description: Test evaluator
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Just say hello
output_suffix: TEST
EOF

adversarial --help  # Should now also show 'test'
adversarial test --help  # Should show file argument and --timeout
```

## Commit and PR

```bash
git add .
git commit -m "feat(cli): Add dynamic evaluator command registration (ADV-0018)

- Register evaluators as subparsers dynamically at startup
- Support aliases for evaluator commands
- Route evaluator commands through run_evaluator()
- Graceful degradation if discovery fails
- Static commands protected from override

Co-Authored-By: Claude <noreply@anthropic.com>"

git push -u origin feature/adv-0018-cli-dynamic-commands

gh pr create --title "feat(cli): Add dynamic evaluator command registration (ADV-0018)" --body "## Summary
- Dynamically registers evaluators (built-in + local) as CLI subcommands
- Custom evaluators in \`.adversarial/evaluators/\` appear in \`adversarial --help\`
- \`adversarial <evaluator> file.md\` routes through \`run_evaluator()\`
- Supports evaluator aliases
- Graceful fallback to built-ins if discovery fails

## Test Plan
- [ ] \`adversarial --help\` shows built-in evaluators
- [ ] Local evaluator appears in help when defined
- [ ] \`adversarial <custom> file.md\` executes correctly
- [ ] Aliases work
- [ ] Static commands (init, check, etc.) cannot be overridden
- [ ] All existing tests pass

Part of plugin architecture epic (ADV-0013)
Depends on: ADV-0015, ADV-0016, ADV-0017"
```

## Acceptance Checklist

- [ ] Custom evaluators appear in `adversarial --help`
- [ ] `adversarial <custom-name> file.md` executes the custom evaluator
- [ ] Aliases work (e.g., `adversarial k` for `knowledge`)
- [ ] Built-in evaluators unchanged (`evaluate`, `proofread`, `review`)
- [ ] `--timeout` flag works for all evaluators
- [ ] Static commands protected from override
- [ ] Graceful fallback if discovery fails
- [ ] Unit tests pass
- [ ] All existing tests pass (137+)
