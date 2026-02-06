# ADV-0031: Library Evaluator Execution

**Status**: Done
**Priority**: HIGH
**Created**: 2026-02-05
**Type**: Feature

---

## Summary

Enable execution of library-installed evaluators via the `adversarial evaluate` command. Currently, users can install evaluators from the library but cannot run them - the evaluate command is hardcoded to use config.yml settings.

## Problem Statement

From adversarial-evaluator-library integration testing:

1. `adversarial library install evaluator-name` works - creates `.adversarial/evaluators/{provider}-{name}.yml`
2. `adversarial list-evaluators` shows local evaluators correctly
3. **BUT** `adversarial evaluate task.md` ignores installed evaluators entirely
4. The evaluate command runs `.adversarial/scripts/evaluate_plan.sh` which reads `evaluator_model` from config.yml
5. No way to select or run a specific installed evaluator

## Proposed Solution (Phase 1 - Minimal)

Add `--evaluator <name>` flag to the evaluate command:

```bash
# Current behavior (unchanged for backward compatibility)
adversarial evaluate task.md  # Uses config.yml evaluator_model

# New behavior with --evaluator flag
adversarial evaluate --evaluator plan-evaluator task.md
adversarial evaluate -e security-reviewer task.md  # short form
```

### Implementation Approach

1. **Add --evaluator flag to CLI** (`cli.py`)
   - Accept evaluator name (not path)
   - Validate evaluator exists via `discover_local_evaluators()`

2. **Modify evaluate() function** (`cli.py`)
   - If `--evaluator` specified: Load evaluator config, use its model/prompt
   - If not specified: Use existing shell script behavior (backward compatible)

3. **Create native evaluator execution**
   - Load evaluator YAML via `discover_local_evaluators()`
   - Extract: `model`, `api_key_env`, `prompt`, `output_suffix`
   - Run aider with those settings (bypass shell script)

4. **Support model_requirement field**
   - If evaluator has `model_requirement`, use `ModelResolver` to resolve model
   - Fall back to legacy `model` field if resolution fails

## Technical Details

### Files to Modify

1. **adversarial_workflow/cli.py**
   - Add `--evaluator` / `-e` argument to evaluate subparser
   - Modify `evaluate()` to handle evaluator selection
   - Add `run_with_evaluator()` helper function

2. **adversarial_workflow/evaluators/__init__.py**
   - Ensure `discover_local_evaluators` is exported
   - Ensure `EvaluatorConfig` is exported

### Evaluator Config Structure

Library evaluators have this structure (from `.adversarial/evaluators/*.yml`):

```yaml
_meta:
  source: adversarial-evaluator-library
  source_path: provider/name
  version: "1.0.0"

name: plan-evaluator
description: Comprehensive plan evaluation
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: |
  You are reviewing an implementation plan...
output_suffix: -PLAN-EVALUATION.md
timeout: 300

# OR with model_requirement (ADV-0015)
model_requirement:
  family: gpt
  tier: flagship
  min_context: 128000
```

### Model Resolution Flow

```
If evaluator.model_requirement exists:
  Try ModelResolver.resolve(model_requirement)
  If success: Use resolved model + api_key_env
  If fails: Fall back to evaluator.model (if present)
Else:
  Use evaluator.model directly
```

## Acceptance Criteria

### Must Have
- [ ] `adversarial evaluate --evaluator <name> task.md` works
- [ ] Uses evaluator's model, prompt, and output_suffix
- [ ] Validates evaluator exists before running
- [ ] Backward compatible: no --evaluator = existing behavior
- [ ] Works with both legacy `model` and `model_requirement` fields

### Should Have
- [ ] `-e` short form works
- [ ] Helpful error message if evaluator not found
- [ ] Lists available evaluators in help text
- [ ] Supports aliases (if evaluator has aliases configured)

### Nice to Have
- [ ] `--list-evaluators` flag to show available evaluators inline
- [ ] Tab completion for evaluator names (future)

## Testing Requirements

### Unit Tests (`tests/test_evaluate_with_evaluator.py`)

```python
def test_evaluate_with_evaluator_flag():
    """Test --evaluator flag selects correct evaluator."""

def test_evaluate_validates_evaluator_exists():
    """Test error when evaluator not found."""

def test_evaluate_uses_evaluator_model():
    """Test evaluator's model is used, not config.yml."""

def test_evaluate_uses_evaluator_prompt():
    """Test evaluator's prompt is used."""

def test_evaluate_model_requirement_resolution():
    """Test model_requirement is resolved when present."""

def test_evaluate_without_flag_uses_config():
    """Test backward compatibility - no flag uses config.yml."""
```

### Integration Tests

- Install a library evaluator, run with --evaluator flag
- Verify output file has correct suffix from evaluator config

## Dependencies

- ADV-0015 Model Routing Phase 1 (MERGED) - provides ModelResolver
- ADV-0013 Library CLI Core (MERGED) - provides library install
- ADV-0014 Library CLI Enhancements (MERGED) - provides enhanced library commands

## Estimated Effort

- Core implementation: 4-6 hours
- Tests: 2-3 hours
- Documentation: 1 hour
- **Total: ~1 day**

## Notes

- This is Phase 1 of library evaluator integration
- Phase 2 could add: evaluate --all (run all evaluators), custom output paths
- Shell script approach remains for users who don't use --evaluator flag

---

**Ready for implementation after ADV-0030 (BugBot fixes) is complete.**
