# ADV-0037: Suppress Browser Opening During Evaluation

**Status**: Todo
**Priority**: Medium
**Created**: 2026-02-07
**Type**: Bug Fix / UX
**Estimated Effort**: 1-2 hours

---

## Problem Statement

When running evaluations, a browser window opens to `https://platform.openai.com/api-keys`. This is disruptive, especially in CI/CD environments or when running multiple evaluations.

## Root Cause

Aider (the underlying tool) opens a browser when:
1. API key is missing or invalid
2. Possibly other authentication scenarios

Aider has a `--no-browser` flag that can suppress this behavior.

## Proposed Solution

Add `--no-browser` flag to all aider invocations in the evaluator runner.

### File: `adversarial_workflow/evaluators/runner.py`

```python
# When building aider command
cmd = [
    "aider",
    "--no-browser",  # ADD THIS
    "--model", model_id,
    ...
]
```

## Acceptance Criteria

- [ ] `--no-browser` flag added to aider invocations
- [ ] Browser no longer opens during normal evaluation
- [ ] Browser no longer opens when API key is missing (should show error instead)
- [ ] Tests updated/added for this behavior
- [ ] Works in CI/CD environments (non-TTY)

## Investigation Notes

Found via `aider --help`:
```
--gui | --no-gui | --browser | --no-browser
```

The `--no-browser` flag should suppress browser opening.

## Testing

```bash
# Test with missing API key - should error, not open browser
unset OPENAI_API_KEY
adversarial evaluate test.md --evaluator gpt4o-quick

# Test normal evaluation - should not open browser
export OPENAI_API_KEY="valid-key"
adversarial evaluate test.md --evaluator gpt4o-quick
```

## Related

- Aider documentation on authentication
- CI/CD compatibility (non-interactive mode)

---

**Notes**: Quick fix - just add the flag to runner.py aider command construction.
