# Review Starter: ADV-0029

**Task**: ADV-0029 - Configurable Timeout per Evaluator
**Task File**: `delegation/tasks/4-in-review/ADV-0029-configurable-timeout-per-evaluator.md`
**Branch**: feature/ADV-0029-configurable-timeout → main
**PR**: https://github.com/movito/adversarial-workflow/pull/16

## Implementation Summary

Added optional `timeout` field to evaluator YAML configuration so users can define per-evaluator timeouts (e.g., 300s for slow models like Mistral Large).

**Key features:**
- YAML `timeout` field with validation (positive int, max 600s)
- Timeout precedence: CLI `--timeout` > YAML config > default (180s)
- Timeout source logging ("CLI override", "evaluator config", "default")
- Boolean rejection (YAML `yes`/`true` → error, not silently accepted as 1)
- CLI non-positive timeout rejection (`--timeout 0` or `-5` → error)

## Files Changed

| File | Type | Description |
|------|------|-------------|
| `adversarial_workflow/evaluators/config.py` | modified | Added `timeout: int = 180` field to dataclass |
| `adversarial_workflow/evaluators/discovery.py` | modified | Added timeout validation (null, empty, bool, non-int, negative, >600) |
| `adversarial_workflow/cli.py` | modified | Timeout precedence logic, source logging, CLI validation |
| `tests/test_evaluator_discovery.py` | modified | +11 timeout validation tests (including boolean edge cases) |
| `tests/test_cli_dynamic_commands.py` | modified | +2 CLI timeout help text tests |
| `tests/test_timeout_integration.py` | new | 9 integration tests for timeout flow |
| `docs/CUSTOM_EVALUATORS.md` | modified | Schema, example, troubleshooting, best practices |

## Test Results

- **206 tests passing** (22 new tests added)
- CI passes on Python 3.10, 3.11, 3.12
- CI passes on Ubuntu and macOS

## Commits

1. `ef296be` - feat(evaluators): Add configurable timeout per evaluator (ADV-0029)
2. `8120701` - fix(evaluators): Address Bugbot feedback on timeout validation

## Areas for Review Focus

1. **Boolean validation logic** (`discovery.py:129-133`) - Checks `bool` before `int` since bool is subclass of int
2. **CLI validation** (`cli.py:3116-3119`) - Non-positive timeout returns error code 1
3. **Timeout precedence** (`cli.py:3105-3114`) - CLI > YAML > default logic
4. **Edge case coverage** - Tests cover null, empty, 0, negative, float, bool, >600

## Bugbot Feedback (Addressed)

| Issue | Severity | Status |
|-------|----------|--------|
| Boolean YAML values silently accepted | Medium | Fixed |
| CLI accepts non-positive timeout | Medium | Fixed |
| Unused imports in tests | Low | Fixed |

## Related Documentation

- Original proposal: `docs/proposals/adversarial-workflow-timeout-issue.md`
- Handoff file: `.agent-context/ADV-0029-HANDOFF-feature-developer.md`

---
**Ready for code-reviewer agent in new tab**
