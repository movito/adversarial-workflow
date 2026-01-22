# ADV-0018: CLI Dynamic Command Registration

**Status**: Done
**Priority**: High
**Estimated Effort**: 3-4 hours
**Target Version**: v0.6.0
**Parent Epic**: ADV-0013
**Depends On**: ADV-0015, ADV-0016, ADV-0017
**Branch**: `feature/plugin-architecture`

## Summary

Modify the CLI to dynamically register evaluators (both built-in and custom) as subcommands. This enables `adversarial athena task.md` to work when `athena.yml` is defined locally.

## Background

Current CLI uses hardcoded argparse subparsers for each command. To support custom evaluators, we need dynamic registration that:
1. Discovers available evaluators at startup
2. Registers each as a CLI subcommand
3. Routes execution through the generic runner

## Error Handling & Edge Cases

### Discovery Failures

If `get_all_evaluators()` fails:
- **Catch and log warning** - do not crash CLI
- **Fall back to built-in evaluators only** - CLI remains functional
- **Print warning message** once: "Warning: Could not load local evaluators"

```python
try:
    evaluators = get_all_evaluators()
except Exception as e:
    logger.warning(f"Evaluator discovery failed: {e}")
    evaluators = BUILTIN_EVALUATORS  # Graceful degradation
```

### Command Name Collision Resolution

**Priority order** (highest to lowest):
1. Static commands (`init`, `check`, `health`, `split`, etc.)
2. Built-in evaluators (`evaluate`, `proofread`, `review`)
3. Local evaluators (from `.adversarial/evaluators/`)

**Resolution rules**:
- Static commands are registered FIRST, before evaluator discovery
- If a local evaluator name matches a static command, **skip it with warning**
- If a local evaluator name matches a built-in evaluator, **local wins** (override)

```python
STATIC_COMMANDS = {"init", "check", "doctor", "health", "quickstart", "agent", "split", "validate"}

for name, config in evaluators.items():
    if name in STATIC_COMMANDS:
        logger.warning(f"Local evaluator '{name}' conflicts with CLI command; skipping")
        continue
    # ... register evaluator
```

### Invalid Evaluator Configs

Handled by ADV-0016 discovery - invalid YAML files are logged and skipped.
By the time configs reach CLI registration, they are guaranteed valid.

## Requirements

### Modify `main()` Function

Replace hardcoded evaluator subparsers with dynamic registration:

```python
# cli.py main() - Modified Section

def main():
    parser = argparse.ArgumentParser(...)
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Non-evaluator commands (unchanged)
    init_parser = subparsers.add_parser("init", ...)
    subparsers.add_parser("quickstart", ...)
    subparsers.add_parser("check", ...)
    # ... etc

    # Dynamic evaluator registration
    from adversarial_workflow.evaluators import get_all_evaluators, run_evaluator

    evaluators = get_all_evaluators()
    registered_configs = set()  # Track by id() to avoid duplicate alias registration

    for name, config in evaluators.items():
        # Skip if this config was already registered (aliases share config)
        if id(config) in registered_configs:
            continue
        registered_configs.add(id(config))

        # Create subparser for this evaluator
        eval_parser = subparsers.add_parser(
            config.name,
            help=config.description,
            aliases=config.aliases,
        )
        eval_parser.add_argument("file", help="File to evaluate")
        eval_parser.add_argument(
            "--timeout", "-t", type=int, default=180,
            help="Timeout in seconds (default: 180)"
        )
        # Store config for later execution
        eval_parser.set_defaults(evaluator_config=config)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Execute command
    if args.command == "init":
        # ... existing logic ...
    elif hasattr(args, "evaluator_config"):
        # This is an evaluator command
        return run_evaluator(
            args.evaluator_config,
            args.file,
            timeout=args.timeout,
        )
    else:
        parser.print_help()
        return 1
```

### Simplify Existing Evaluator Functions

The existing `evaluate()`, `proofread()`, and `review()` functions can be removed or kept as thin wrappers:

```python
# Optional: Keep for backwards compatibility in Python API
def evaluate(task_file: str) -> int:
    """Run Phase 1: Plan evaluation.

    Note: Prefer using CLI: adversarial evaluate <file>
    """
    from .evaluators import BUILTIN_EVALUATORS, run_evaluator
    return run_evaluator(BUILTIN_EVALUATORS["evaluate"], task_file)
```

### Handle Command Routing

Update the command dispatch to handle dynamic evaluators:

```python
# In main(), command execution section

# First, check if it's a known static command
static_commands = {
    "init": lambda: init(args.path) if not args.interactive else init_interactive(args.path),
    "quickstart": quickstart,
    "check": check,
    "doctor": check,
    "health": lambda: health(verbose=args.verbose, json_output=args.json),
    "validate": lambda: validate(args.test_command),
    "split": lambda: split(args.task_file, ...),
}

if args.command in static_commands:
    return static_commands[args.command]()
elif hasattr(args, "evaluator_config"):
    # Dynamic evaluator command
    return run_evaluator(args.evaluator_config, args.file, args.timeout)
elif args.command == "agent":
    # Handle agent subcommands
    ...
else:
    parser.print_help()
    return 1
```

### Help Text Formatting

Ensure `--help` output is clean:

```text
$ adversarial --help
usage: adversarial [-h] [--version] {init,quickstart,check,...} ...

Adversarial Workflow - Multi-stage AI code review

positional arguments:
  {init,quickstart,check,health,agent,evaluate,proofread,review,athena,...}
                        Command to run
    init                Initialize workflow in project
    quickstart          Quick start with example task
    check               Validate setup and dependencies
    evaluate            Plan evaluation (GPT-4o)
    proofread           Teaching content review (GPT-4o)
    review              Code review (GPT-4o)
    athena              Knowledge evaluation (Gemini 2.5 Pro)  # Local evaluator
    ...
```

### Performance Consideration

Evaluator discovery should be fast (<100ms). If it becomes slow:

```python
# Option 1: Lazy loading
_evaluators_cache = None

def get_all_evaluators():
    global _evaluators_cache
    if _evaluators_cache is None:
        _evaluators_cache = _discover_all()
    return _evaluators_cache

# Option 2: Only discover when needed
# Don't call get_all_evaluators() unless user runs an evaluator command
```

For v0.6.0, eager loading is fine. Optimize later if needed.

## Testing Requirements

Create `tests/test_cli_dynamic_commands.py`:

### Discovery Integration

```python
def test_cli_shows_local_evaluator_in_help(tmp_path, monkeypatch):
    """Local evaluator appears in --help output."""
    # Setup: Create .adversarial/evaluators/test.yml
    eval_dir = tmp_path / ".adversarial" / "evaluators"
    eval_dir.mkdir(parents=True)
    (eval_dir / "test.yml").write_text("""
name: test
description: Test evaluator
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Test
output_suffix: TEST
""")

    monkeypatch.chdir(tmp_path)

    # Run help and check output
    result = subprocess.run(
        ["adversarial", "--help"],
        capture_output=True,
        text=True,
    )
    assert "test" in result.stdout
    assert "Test evaluator" in result.stdout
```

### Execution Routing

```python
def test_cli_routes_to_custom_evaluator(tmp_path, monkeypatch, mocker):
    """Custom evaluator is callable via CLI."""
    # Setup evaluator
    # ...

    # Mock run_evaluator to verify it's called
    mock_run = mocker.patch("adversarial_workflow.evaluators.run_evaluator")
    mock_run.return_value = 0

    result = subprocess.run(
        ["adversarial", "test", "somefile.md"],
        capture_output=True,
        cwd=tmp_path,
    )

    mock_run.assert_called_once()
```

### Backwards Compatibility

```python
def test_builtin_evaluate_still_works():
    """adversarial evaluate works as before."""
    # Verify evaluate command exists and routes correctly
    ...

def test_builtin_proofread_still_works():
    """adversarial proofread works as before."""
    ...
```

### Alias Support

```python
def test_alias_routes_to_same_evaluator(tmp_path, monkeypatch):
    """Aliases work as separate commands."""
    # Create evaluator with aliases
    # Verify both `adversarial athena` and `adversarial knowledge` work
    ...
```

## Acceptance Criteria

- [ ] Custom evaluators appear in `adversarial --help`
- [ ] `adversarial <custom-name> file.md` executes the custom evaluator
- [ ] Aliases work (`adversarial knowledge` == `adversarial athena`)
- [ ] Built-in evaluators unchanged (`evaluate`, `proofread`, `review`)
- [ ] `--timeout` flag works for all evaluators
- [ ] Discovery completes in <100ms
- [ ] Clear error messages for missing evaluators
- [ ] Unit and integration tests pass
- [ ] All existing tests pass

## Migration Notes

- No breaking changes to existing CLI
- Python API (`from adversarial_workflow import evaluate`) preserved
- Custom evaluators only work when `.adversarial/evaluators/` exists

## Implementation Order

1. Import evaluator modules in main()
2. Add dynamic subparser registration loop
3. Update command dispatch to handle evaluator_config
4. Simplify existing evaluate/proofread/review (optional)
5. Add tests
6. Verify backwards compatibility

## References

- Parent Epic: ADV-0013-plugin-architecture-epic.md
- Depends On: ADV-0015, ADV-0016, ADV-0017
- Current main(): cli.py:3043-3196
