# ADV-0029: Configurable Timeout per Evaluator

**Status**: In Progress
**Priority**: Medium
**Type**: Feature
**Estimated Effort**: Medium (4-5 hours)
**Created**: 2026-01-28
**Source**: Feature request from gas-taxes project team

---

## Summary

Add optional `timeout` field to evaluator YAML configuration to allow per-evaluator timeout customization. The existing `--timeout` CLI flag should override YAML values.

## Problem Statement

The current hardcoded 180-second timeout kills Mistral Large requests on large documents (>5K words) before completion. Different models have vastly different response times:

| Model | Small Doc (~1K) | Medium Doc (~3K) | Large Doc (~6.8K) |
|-------|-----------------|------------------|-------------------|
| GPT-5.2 | ~15s | ~45s | ~90s |
| Mistral Large | 29s | 87s | **>180s (TIMEOUT)** |
| Mistral Small | 7s | 44s | 173s |

## Proposed Solution

### YAML Schema Addition

```yaml
# .adversarial/evaluators/mistral-content.yml
name: mistral-content
description: Content review using Mistral Large
model: mistral/mistral-large-latest
api_key_env: MISTRAL_API_KEY
timeout: 300  # NEW: timeout in seconds (default: 180, max: 600)
output_suffix: -mistral-content.md

prompt: |
  ...
```

### Behavior

1. If `timeout` not specified in YAML → use default (180s)
2. If `timeout` specified in YAML → use that value
3. If `--timeout` CLI flag provided → override YAML/default value
4. Maximum allowed: 600 seconds (10 minutes) to prevent runaway processes

### Backward Compatibility

**Existing evaluator configs without `timeout` field will continue to work unchanged.** The `timeout` field has a default value of 180 in `EvaluatorConfig`, so:
- Existing YAML files: No changes needed, get default 180s
- Built-in evaluators: Continue using 180s default
- CLI behavior: Unchanged (flag still works, just now can read from config)

### Timeout Error Handling

When a timeout occurs (existing behavior in `runner.py`):
1. `subprocess.TimeoutExpired` is caught
2. Error message displayed: `"Error: Evaluation timed out (>{timeout}s)"`
3. Process is terminated (subprocess killed)
4. Exit code 1 returned

No cleanup is needed - the subprocess is killed and aider handles its own cleanup.

---

## Implementation Plan

### Phase 1: Add timeout field to EvaluatorConfig

**File**: `adversarial_workflow/evaluators/config.py`

1. Add `timeout: int = 180` to EvaluatorConfig dataclass (after `version` field)
2. Update docstring to document the new field

```python
# Add to EvaluatorConfig dataclass (line ~44, after version field)
timeout: int = 180  # Timeout in seconds (default: 180, max: 600)
```

### Phase 2: Parse timeout from YAML

**File**: `adversarial_workflow/evaluators/discovery.py`

1. Add `"timeout"` to `known_fields` set (line ~136)
2. Add validation logic after required fields check:
   - Must be an integer
   - Must be positive (> 0)
   - Must not exceed 600 seconds
   - Log warning if timeout > 600 and clamp to 600

```python
# Add validation (around line 115, after aliases validation)
if "timeout" in data:
    timeout = data["timeout"]
    # Handle null/empty values
    if timeout is None or timeout == "":
        raise EvaluatorParseError(
            f"Field 'timeout' cannot be null or empty"
        )
    if not isinstance(timeout, int):
        raise EvaluatorParseError(
            f"Field 'timeout' must be an integer, got {type(timeout).__name__}: {timeout!r}"
        )
    # timeout=0 is invalid (does not disable timeout - use a large value instead)
    if timeout <= 0:
        raise EvaluatorParseError(
            f"Field 'timeout' must be positive (> 0), got {timeout}"
        )
    if timeout > 600:
        logger.warning(
            "Timeout %ds exceeds maximum (600s), clamping to 600s in %s",
            timeout, yml_file.name
        )
        data["timeout"] = 600
```

**Edge case decisions:**
- `timeout: 0` → Invalid (error). To effectively disable timeout, use `timeout: 600`
- `timeout: null` → Invalid (error). Omit the field to use default
- `timeout: ""` → Invalid (error). Must be an integer

### Phase 3: Update CLI to use config timeout

**File**: `adversarial_workflow/cli.py`

1. Change `--timeout` default from `180` to `None` (lines 3082-3086)
2. Add CLI timeout validation (>600s should clamp with warning, consistent with YAML)
3. Add logging of actual timeout value at evaluation start
4. Update execution logic to prefer: CLI flag > YAML config > default (line ~3102)

```python
# Change default to None
eval_parser.add_argument(
    "--timeout",
    "-t",
    type=int,
    default=None,  # Changed from 180
    help="Timeout in seconds (default: from evaluator config or 180, max: 600)",
)

# Update execution (around line 3100)
timeout = args.timeout if args.timeout is not None else args.evaluator_config.timeout

# Validate CLI timeout (consistent with YAML validation)
if timeout > 600:
    print(f"{YELLOW}Warning: Timeout {timeout}s exceeds maximum (600s), clamping to 600s{RESET}")
    timeout = 600

# Log actual timeout and source being used
if args.timeout is not None:
    source = "CLI override"
elif args.evaluator_config.timeout != 180:
    source = "evaluator config"
else:
    source = "default"
print(f"Using timeout: {timeout}s ({source})")

return run_evaluator(
    args.evaluator_config,
    args.file,
    timeout=timeout,
)
```

### Phase 3.5: Verify runner.py integration

**File**: `adversarial_workflow/evaluators/runner.py`

The runner already accepts `timeout` parameter and passes it to subprocess. Verify:
1. `run_evaluator(config, file_path, timeout)` signature unchanged
2. Timeout is passed through to `subprocess.run(..., timeout=timeout)`
3. `TimeoutExpired` exception handling already exists

**No changes needed to runner.py** - just verification that timeout flows through correctly.

### Phase 4: Tests

**File**: `tests/test_evaluate.py`
- Add test for timeout field parsing from YAML
- Add test for timeout validation (negative, too large, non-integer)
- Add test for CLI override of YAML timeout
- Add test for CLI timeout >600s clamping

**File**: `tests/test_cli_dynamic_commands.py`
- Update existing timeout tests to account for None default
- Add test for config-based timeout

**File**: `tests/test_timeout_integration.py` (NEW)
- Integration test that actually runs an evaluator with custom timeout
- Uses a mock evaluator script that accepts a configurable sleep duration:
  ```python
  # Mock evaluator: tests/fixtures/mock_evaluator.py
  import sys, time
  sleep_duration = int(sys.argv[1]) if len(sys.argv) > 1 else 1
  time.sleep(sleep_duration)
  print("Mock evaluation complete")
  ```
- Test cases:
  1. Evaluator with timeout=5, mock sleeps 2s → Success
  2. Evaluator with timeout=2, mock sleeps 5s → TimeoutExpired
  3. CLI `--timeout 3` overrides YAML `timeout: 10`, mock sleeps 5s → TimeoutExpired
- Verifies timeout logging shows correct source (CLI/YAML/default)

### Phase 5: Documentation

**File**: `docs/evaluators.md` (or equivalent)
- Document new `timeout` field in YAML schema
- Document precedence: CLI > YAML > default

---

## Files to Modify

| File | Changes |
|------|---------|
| `adversarial_workflow/evaluators/config.py` | Add `timeout` field |
| `adversarial_workflow/evaluators/discovery.py` | Add to known_fields, add validation |
| `adversarial_workflow/cli.py` | Change default, add CLI validation, add logging |
| `adversarial_workflow/evaluators/runner.py` | Verify only (no changes expected) |
| `tests/test_evaluate.py` | Add timeout parsing/validation tests |
| `tests/test_cli_dynamic_commands.py` | Update existing tests |
| `tests/test_timeout_integration.py` | NEW: Integration test for timeout flow |
| `docs/evaluators.md` | Document new field |

---

## Acceptance Criteria

- [ ] **YAML Parsing**: `timeout` field parsed from evaluator YAML
- [ ] **YAML Validation**: Non-integer, negative, and >600 values handled correctly
- [ ] **CLI Validation**: CLI `--timeout >600` clamps with warning (consistent with YAML)
- [ ] **CLI Override**: `--timeout` flag overrides YAML value
- [ ] **Default Behavior**: Missing `timeout` uses default 180s (backward compatible)
- [ ] **Maximum Enforcement**: Timeout capped at 600s with warning (both YAML and CLI)
- [ ] **Logging**: Actual timeout value AND source (CLI/YAML/default) logged at evaluation start
- [ ] **Integration Test**: Test verifies timeout flows through entire stack
- [ ] **Unit Tests Pass**: All existing tests pass, new tests added
- [ ] **Documentation**: YAML schema documented

---

## Success Metrics

**Quantitative**:
- All 7 acceptance criteria met
- Test coverage for new code > 90%
- No regression in existing tests

**Qualitative**:
- Clean, consistent code style
- Clear error messages for validation failures

---

## Test Cases

```bash
# 1. YAML-based timeout (should use 300s from config)
# Create evaluator with timeout: 300, evaluate large doc
adversarial evaluate --evaluator mistral-content large-doc.md

# 2. CLI override (should use 400s despite YAML saying 300)
adversarial evaluate --evaluator mistral-content --timeout 400 large-doc.md

# 3. No timeout in YAML (should use default 180s)
adversarial evaluate --evaluator basic-evaluator doc.md

# 4. Invalid timeout in YAML (should error)
# timeout: "five minutes" → EvaluatorParseError

# 5. Excessive timeout (should clamp and warn)
# timeout: 1200 → clamped to 600 with warning

# 6. Edge cases (should all error with clear messages)
# timeout: 0 → EvaluatorParseError("must be positive (> 0)")
# timeout: null → EvaluatorParseError("cannot be null or empty")
# timeout: "" → EvaluatorParseError("cannot be null or empty")
# timeout: -5 → EvaluatorParseError("must be positive (> 0)")

# 7. CLI excessive timeout (should clamp and warn)
adversarial evaluate --evaluator basic --timeout 999 doc.md
# → Warning: Timeout 999s exceeds maximum (600s), clamping to 600s
```

---

## References

- Proposal: `docs/proposals/adversarial-workflow-timeout-issue.md`
- Current implementation: `adversarial_workflow/evaluators/runner.py:19`
- CLI flag: `adversarial_workflow/cli.py:3082-3086`
- EvaluatorConfig: `adversarial_workflow/evaluators/config.py:9-48`

---

## Notes

- The CLI `--timeout` flag already exists - this task adds YAML config support
- Built-in evaluators (evaluate, proofread, review) will use the default timeout unless overridden via CLI
- Consider future enhancement: per-model timeout recommendations in documentation
