# Review Insights Index

Knowledge extracted from code reviews for future reference (KIT-ADR-0019).

---

## Evaluators (`adversarial_workflow/evaluators/`)

### ADV-0029: YAML field validation should check for bool coercion
- YAML parses `yes`/`no`/`true`/`false` as booleans, not strings
- When validating integer fields, explicitly check `isinstance(value, bool)` before `isinstance(value, int)` (since bool is a subclass of int in Python)
- Pattern used in `discovery.py:126-152`

### ADV-0029: Precedence logging pattern for config overrides
- When multiple sources can provide a value (CLI > config > default), log which source is active
- Pattern: `print(f"Using {setting}: {value} ({source})")`
- Helps users understand where their configuration comes from

---

## Testing (`tests/`)

### ADV-0029: Integration testing subprocess timeouts with mock scripts
- Create lightweight mock scripts that sleep for configurable durations
- Test timeout success: mock sleeps less than timeout
- Test timeout failure: mock sleeps longer than timeout
- Verify timeout values flow through entire stack
- See `tests/test_timeout_integration.py` for pattern

### ADV-0029: Use raw strings for regex in pytest.raises match
- Style preference: `match=r"pattern.*here"` not `match="pattern.*here"`
- Prevents escape sequence issues

---

## CLI (`adversarial_workflow/cli.py`)

### ADV-0029: Validation at execution time for CLI overrides
- CLI flag validation (e.g., max values) should happen at execution time, not argument parsing
- Allows config defaults to be used if CLI flag not provided
- Pattern: Check `args.flag is not None` before applying validation

---

*Last updated: 2026-01-28*
