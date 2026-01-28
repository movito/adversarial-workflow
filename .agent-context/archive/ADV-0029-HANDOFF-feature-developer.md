# ADV-0029: Configurable Timeout per Evaluator - Implementation Handoff

**Date**: 2026-01-28
**From**: Planner
**To**: feature-developer
**Task**: delegation/tasks/2-todo/ADV-0029-configurable-timeout-per-evaluator.md
**Status**: Ready for implementation
**Evaluation**: Revised after 2 rounds of GPT-4o feedback ($0.05)

---

## Task Summary

Add optional `timeout` field to evaluator YAML configuration. The CLI `--timeout` flag already exists; this task adds YAML config support so evaluators can define their own defaults. Mistral Large users reported that 180-second default kills large document evaluations before completion.

## Current Situation

- **Problem**: Hardcoded 180s timeout kills Mistral Large on large docs (>5K words)
- **CLI**: `--timeout` flag already exists but requires manual override each time
- **Request**: Allow evaluators to define their own timeout in YAML config

## Your Mission

Implement configurable timeout with this precedence: CLI flag > YAML config > default (180s)

### Phase 1: Add timeout field to EvaluatorConfig (30 min)
- File: `adversarial_workflow/evaluators/config.py`
- Add `timeout: int = 180` to dataclass
- Update docstring

### Phase 2: Parse timeout from YAML (1 hour)
- File: `adversarial_workflow/evaluators/discovery.py`
- Add `"timeout"` to `known_fields` set
- Add validation (must be int, positive, max 600s)
- Handle edge cases: null, empty string, 0

### Phase 3: Update CLI (1 hour)
- File: `adversarial_workflow/cli.py`
- Change `--timeout` default from 180 to None
- Add CLI timeout validation (>600s clamps with warning)
- Add timeout source logging (CLI/YAML/default)
- Wire up: `timeout = args.timeout or config.timeout`

### Phase 4: Tests (1.5 hours)
- `tests/test_evaluate.py`: Parsing, validation, CLI override tests
- `tests/test_cli_dynamic_commands.py`: Update existing timeout tests
- `tests/test_timeout_integration.py` (NEW): End-to-end timeout flow test

### Phase 5: Documentation (30 min)
- Update evaluator YAML schema docs

---

## Critical Implementation Details

### 1. EvaluatorConfig Field Addition

```python
# adversarial_workflow/evaluators/config.py (after version field, line ~44)
timeout: int = 180  # Timeout in seconds (default: 180, max: 600)
```

### 2. YAML Validation Logic

```python
# adversarial_workflow/evaluators/discovery.py (add to known_fields around line 126)
known_fields = {
    "name", "description", "model", "api_key_env", "prompt",
    "output_suffix", "log_prefix", "fallback_model", "aliases", "version",
    "timeout",  # <-- ADD THIS
}

# Add validation after existing field checks (around line 115)
if "timeout" in data:
    timeout = data["timeout"]
    if timeout is None or timeout == "":
        raise EvaluatorParseError(f"Field 'timeout' cannot be null or empty")
    if not isinstance(timeout, int):
        raise EvaluatorParseError(
            f"Field 'timeout' must be an integer, got {type(timeout).__name__}: {timeout!r}"
        )
    if timeout <= 0:
        raise EvaluatorParseError(f"Field 'timeout' must be positive (> 0), got {timeout}")
    if timeout > 600:
        logger.warning(
            "Timeout %ds exceeds maximum (600s), clamping to 600s in %s",
            timeout, yml_file.name
        )
        data["timeout"] = 600
```

### 3. CLI Updates

```python
# adversarial_workflow/cli.py (around line 3082)
eval_parser.add_argument(
    "--timeout", "-t",
    type=int,
    default=None,  # Changed from 180
    help="Timeout in seconds (default: from evaluator config or 180, max: 600)",
)

# Around line 3100, before run_evaluator call
timeout = args.timeout if args.timeout is not None else args.evaluator_config.timeout

# Add CLI validation
if timeout > 600:
    print(f"{YELLOW}Warning: Timeout {timeout}s exceeds maximum (600s), clamping to 600s{RESET}")
    timeout = 600

# Log timeout source
if args.timeout is not None:
    source = "CLI override"
elif args.evaluator_config.timeout != 180:
    source = "evaluator config"
else:
    source = "default"
print(f"Using timeout: {timeout}s ({source})")
```

### 4. Integration Test Mock Evaluator

```python
# tests/fixtures/mock_evaluator.py (create this)
import sys
import time

sleep_duration = int(sys.argv[1]) if len(sys.argv) > 1 else 1
time.sleep(sleep_duration)
print("Mock evaluation complete")
```

---

## Edge Case Decisions

| Case | Behavior |
|------|----------|
| `timeout: 0` | Invalid (error) |
| `timeout: null` | Invalid (error) |
| `timeout: ""` | Invalid (error) |
| `timeout: -5` | Invalid (error) |
| `timeout: 1200` | Clamp to 600 with warning |
| `--timeout 999` | Clamp to 600 with warning |
| No timeout in YAML | Use default (180) |

---

## Resources for Implementation

- **Task Spec**: `delegation/tasks/2-todo/ADV-0029-configurable-timeout-per-evaluator.md`
- **Current config.py**: `adversarial_workflow/evaluators/config.py:9-48`
- **Current discovery.py**: `adversarial_workflow/evaluators/discovery.py`
- **Current CLI**: `adversarial_workflow/cli.py:3082-3106`
- **Existing timeout tests**: `tests/test_cli_dynamic_commands.py` (search for "timeout")
- **Evaluation log**: `.adversarial/logs/ADV-0029-configurable-timeout-per-evaluator-PLAN-EVALUATION.md`

---

## Starting Point

1. **Run `./scripts/project start ADV-0029`** to move task to `3-in-progress/`
2. Read the existing `EvaluatorConfig` in `config.py`
3. Add the `timeout` field
4. Run existing tests to ensure no breakage: `pytest tests/test_evaluate.py tests/test_cli_dynamic_commands.py -v`
5. Add validation to `discovery.py`
6. Update CLI in `cli.py`
7. Write new tests
8. Run full test suite: `pytest`

---

## Success Looks Like

```bash
# 1. YAML timeout works
$ cat .adversarial/evaluators/slow-model.yml
name: slow-model
timeout: 300
...

$ adversarial slow-model doc.md
Using timeout: 300s (evaluator config)
...

# 2. CLI override works
$ adversarial slow-model --timeout 400 doc.md
Using timeout: 400s (CLI override)
...

# 3. Default works (no timeout in YAML)
$ adversarial evaluate doc.md
Using timeout: 180s (default)
...

# 4. All tests pass
$ pytest
... 100% passed ...
```

---

## Notes

- The `--timeout` CLI flag already exists and works - you're just adding YAML support
- Built-in evaluators (evaluate, proofread, review) don't need YAML changes - they use default
- runner.py already accepts timeout parameter - no changes needed there

---

**Task File**: `delegation/tasks/2-todo/ADV-0029-configurable-timeout-per-evaluator.md`
**Evaluation Log**: `.adversarial/logs/ADV-0029-configurable-timeout-per-evaluator-PLAN-EVALUATION.md`
**Handoff Date**: 2026-01-28
**Coordinator**: Planner
