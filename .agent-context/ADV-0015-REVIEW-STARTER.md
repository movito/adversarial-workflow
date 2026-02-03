# Review Starter: ADV-0015

**Task**: ADV-0015 - Model Routing Layer - Phase 1
**Task File**: `delegation/tasks/4-in-review/ADV-0015-model-routing-phase1.md`
**Branch**: feat/adv-0015-model-routing-phase1 → main
**PR**: #21

## Implementation Summary

Implemented Phase 1 of the model routing layer with dual-field support. Evaluators can now specify model requirements using either the legacy `model` field or the new `model_requirement` structured field. The resolver maps family/tier pairs to actual model IDs via an embedded registry.

- Added `ModelRequirement` dataclass for structured model capability requirements
- Created `ModelResolver` with embedded registry supporting 7 model families
- Updated YAML parsing to handle `model_requirement` field with validation
- Integrated resolver into runner with fallback to legacy field on failure

## Files Changed

### New Files
- `adversarial_workflow/evaluators/resolver.py` - ModelResolver class with embedded registry and resolution logic

### Modified Files
- `adversarial_workflow/evaluators/config.py` - Added ModelRequirement dataclass and extended EvaluatorConfig
- `adversarial_workflow/evaluators/discovery.py` - Parse model_requirement from YAML with validation
- `adversarial_workflow/evaluators/runner.py` - Use resolver before execution, handle ResolutionError
- `adversarial_workflow/evaluators/__init__.py` - Export new classes
- `tests/test_evaluator_discovery.py` - Added model_requirement parsing tests
- `tests/test_evaluator_runner.py` - Added model resolution integration tests
- `tests/test_model_resolver.py` - New test file with 28 resolver tests

## Test Results

```text
350 passed in 7.74s
Coverage: 55%
- 28 new tests for ModelResolver
- 10 new tests for model_requirement YAML parsing
- 5 new tests for runner integration
```

## Areas for Review Focus

1. **Resolution Order Logic** (`resolver.py:119-140`): Fallback behavior when model_requirement fails - should warn and use legacy model if available, or raise if not. Verify this matches ADR-0004 spec.

2. **Registry Data** (`resolver.py:39-110`): Embedded registry must match library's providers/registry.yml. Currently hardcoded - Phase 2 will add external registry fetching.

3. **Backwards Compatibility** (`discovery.py:56-80`): Changed required fields logic - model/api_key_env now optional when model_requirement present. Verify no breaking changes to existing evaluators.

4. **Warning Messages** (`resolver.py:127-132`): Fallback warnings use `warnings.warn()` - review message clarity and stacklevel.

## Related Documentation

- **Task file**: `delegation/tasks/4-in-review/ADV-0015-model-routing-phase1.md`
- **ADRs**: ADR-0004 (Model Routing Separation), ADR-0005 (Interface Contract)
- **Handoff**: `.agent-context/ADV-0015-HANDOFF-feature-developer.md`

## Pre-Review Checklist (Implementation Agent)

Before requesting review, verify:

- [x] All acceptance criteria from task file are implemented
- [x] Tests written and passing (350 tests)
- [x] Local CI passes (`./scripts/ci-check.sh`)
- [x] Task moved to `4-in-review/`
- [x] No debug code or console.logs left behind
- [x] Docstrings for public APIs

---

**Ready for code-reviewer agent in new tab**

To start review:
1. Open new Claude Code tab
2. Run: `agents/launch code-reviewer`
3. Reviewer will auto-detect this starter file
