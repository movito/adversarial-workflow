# ADV-0019 Task Starter

## Quick Context

Add `adversarial list-evaluators` command and documentation for the plugin architecture. This is the final task in the v0.6.0 plugin implementation chain.

**Branch**: `feature/adv-0019-list-evaluators-docs`
**Base**: `main` (dd7ab5b)
**Depends On**: ADV-0015, ADV-0016, ADV-0017, ADV-0018 (all merged)

## What's Already in Place

The evaluators module (`adversarial_workflow/evaluators/`) provides:
```python
from adversarial_workflow.evaluators import (
    get_all_evaluators,      # Returns dict of all evaluators (built-in + local)
    discover_local_evaluators,  # Returns dict of local evaluators only
    BUILTIN_EVALUATORS,      # Dict of built-in evaluators
    EvaluatorConfig,         # Dataclass for evaluator config
)
```

## Implementation Tasks

### 1. Add `list_evaluators()` function to cli.py

Location: Add after line ~2850 (near other utility commands)

```python
def list_evaluators() -> int:
    """List all available evaluators (built-in and local)."""
    from adversarial_workflow.evaluators import (
        BUILTIN_EVALUATORS,
        discover_local_evaluators,
    )

    # Print built-in evaluators
    print(f"{BOLD}Built-in Evaluators:{RESET}")
    for name, config in sorted(BUILTIN_EVALUATORS.items()):
        print(f"  {name:14} {config.description}")

    print()

    # Print local evaluators
    local_evaluators = discover_local_evaluators()
    if local_evaluators:
        print(f"{BOLD}Local Evaluators{RESET} (.adversarial/evaluators/):")

        # Group by primary name (skip aliases)
        seen_configs = set()
        for name, config in sorted(local_evaluators.items()):
            if id(config) in seen_configs:
                continue
            seen_configs.add(id(config))

            print(f"  {config.name:14} {config.description}")
            if config.aliases:
                print(f"    aliases: {', '.join(config.aliases)}")
            print(f"    model: {config.model}")
            if config.version != "1.0.0":
                print(f"    version: {config.version}")
    else:
        print(f"{GRAY}No local evaluators found.{RESET}")
        print()
        print("Create .adversarial/evaluators/*.yml to add custom evaluators.")
        print("See: https://github.com/movito/adversarial-workflow#custom-evaluators")

    return 0
```

### 2. Register subparser in main()

Find the static command subparsers section (around line ~3070) and add:

```python
subparsers.add_parser(
    "list-evaluators",
    help="List all available evaluators (built-in and local)",
)
```

### 3. Add command dispatch

Find the command dispatch section and add (before the `else` clause):

```python
elif args.command == "list-evaluators":
    return list_evaluators()
```

### 4. Add STATIC_COMMANDS entry

Find `STATIC_COMMANDS` set and add `"list-evaluators"` to protect it from evaluator override.

### 5. Create tests

Create `tests/test_list_evaluators.py`:

```python
"""Tests for adversarial list-evaluators command."""

import subprocess
import sys


class TestListEvaluatorsCommand:
    """Tests for list-evaluators CLI command."""

    def test_list_evaluators_shows_builtins(self, tmp_path, monkeypatch):
        """Built-in evaluators appear in output."""
        monkeypatch.chdir(tmp_path)
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "list-evaluators"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Built-in Evaluators" in result.stdout
        assert "evaluate" in result.stdout
        assert "proofread" in result.stdout
        assert "review" in result.stdout

    def test_list_evaluators_no_local_message(self, tmp_path, monkeypatch):
        """Shows helpful message when no local evaluators."""
        monkeypatch.chdir(tmp_path)
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "list-evaluators"],
            capture_output=True,
            text=True,
        )
        assert "No local evaluators" in result.stdout
        assert ".adversarial/evaluators/*.yml" in result.stdout

    def test_list_evaluators_with_local(self, tmp_path, monkeypatch):
        """Shows local evaluators when present."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "test.yml").write_text("""
name: test
description: Test evaluator
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: TEST
aliases:
  - t
""")

        monkeypatch.chdir(tmp_path)
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "list-evaluators"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Local Evaluators" in result.stdout
        assert "test" in result.stdout
        assert "aliases: t" in result.stdout
        assert "model: gpt-4o-mini" in result.stdout

    def test_list_evaluators_help(self, tmp_path, monkeypatch):
        """list-evaluators appears in --help."""
        monkeypatch.chdir(tmp_path)
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "--help"],
            capture_output=True,
            text=True,
        )
        assert "list-evaluators" in result.stdout
```

### 6. Documentation (lower priority)

Create these files if time permits:
- Update `README.md` with Custom Evaluators section
- Create `docs/CUSTOM_EVALUATORS.md`
- Create `docs/examples/athena.yml`
- Update `CHANGELOG.md` for v0.6.0

See task spec for full content templates.

## Testing Commands

```bash
# Run new tests
pytest tests/test_list_evaluators.py -v

# Run all tests
pytest tests/ -v

# Manual test
adversarial list-evaluators
```

## Files to Create/Modify

| File | Action |
|------|--------|
| `adversarial_workflow/cli.py` | Add function + registration |
| `tests/test_list_evaluators.py` | Create new test file |
| `README.md` | Add Custom Evaluators section |
| `docs/CUSTOM_EVALUATORS.md` | Create (optional) |
| `docs/examples/athena.yml` | Create example (optional) |
| `CHANGELOG.md` | Update for v0.6.0 (optional) |

## Acceptance Criteria

- [ ] `adversarial list-evaluators` shows built-in evaluators
- [ ] `adversarial list-evaluators` shows local evaluators with details
- [ ] Helpful message when no local evaluators exist
- [ ] `list-evaluators` appears in `--help`
- [ ] Unit tests pass
- [ ] All existing tests pass (160+)

## Post-Implementation

After tests pass, follow the **Post-Implementation Workflow** in the feature-developer agent definition:
1. Commit and push
2. Create PR
3. Monitor CodeRabbit and BugBot feedback
4. Address any issues
5. Create review starter when bots are satisfied

## Resources

- Task spec: `delegation/tasks/2-todo/ADV-0019-list-evaluators-and-docs.md`
- Evaluators module: `adversarial_workflow/evaluators/`
- CLI main(): `adversarial_workflow/cli.py` (start at line ~3043)
