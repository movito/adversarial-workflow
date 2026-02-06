# ADV-0032 Handoff: Feature Developer

**Created**: 2026-02-06
**Task**: Resolver Model Field Priority
**Branch**: `feat/adv-0032-resolver-model-priority` (already created)

---

## Quick Context

The ModelResolver's hardcoded registry has stale model IDs. When library evaluators specify `model: claude-opus-4-6`, the resolver ignores it and uses the registry's old `claude-4-opus-20260115`.

**Fix**: Change resolution priority so explicit `model` field takes precedence over `model_requirement` resolution.

---

## Implementation

### File: `adversarial_workflow/evaluators/resolver.py`

**Replace the `resolve` method** (lines 128-159):

```python
def resolve(self, config: EvaluatorConfig) -> tuple[str, str]:
    """Resolve evaluator config to (model_id, api_key_env).

    Resolution priority:
    1. Explicit model field - evaluator specifies exact model ID
    2. model_requirement - resolve via registry when model absent
    3. Neither - raise ResolutionError

    Args:
        config: EvaluatorConfig with model and/or model_requirement

    Returns:
        (model_id, api_key_env) tuple

    Raises:
        ResolutionError: If no model or model_requirement specified
    """
    # Priority 1: Explicit model field takes precedence
    # This allows evaluators to specify exact model IDs that stay current
    if config.model:
        return (config.model, config.api_key_env)

    # Priority 2: Resolve model_requirement via registry
    # Used for truly portable evaluators without specific model preference
    if config.model_requirement:
        return self._resolve_requirement(config.model_requirement)

    raise ResolutionError("No model or model_requirement specified")
```

**Also update the docstring** at the top of the class (lines 30-36):

```python
"""Resolves model requirements to actual model IDs.

Uses an embedded registry (matching adversarial-evaluator-library/providers/registry.yml)
to map family/tier pairs to concrete model identifiers.

Resolution order:
1. If model present: use directly (evaluator specifies exact model)
2. If model_requirement present AND model absent: resolve via registry
3. If neither: raise ResolutionError
"""
```

---

## Test Updates

### File: `tests/test_model_resolver.py`

**Add new test**:

```python
def test_model_field_takes_priority_over_requirement(self):
    """Explicit model field overrides model_requirement resolution."""
    config = EvaluatorConfig(
        name="priority-test",
        description="Test model priority",
        model="claude-opus-4-6",  # Explicit - should win
        api_key_env="ANTHROPIC_API_KEY",
        prompt="Test prompt",
        output_suffix="-TEST.md",
        model_requirement=ModelRequirement(
            family="claude",
            tier="opus",
        ),  # Would resolve to old ID - should be ignored
    )
    resolver = ModelResolver()
    model_id, api_key_env = resolver.resolve(config)

    # Explicit model wins
    assert model_id == "claude-opus-4-6"
    assert api_key_env == "ANTHROPIC_API_KEY"
    # No prefix added (registry not used)
    assert "anthropic/" not in model_id
```

**Update existing tests** if they expect the old behavior (model_requirement taking priority).

---

## Verification Checklist

- [ ] `resolve()` returns explicit `model` when present
- [ ] `resolve()` uses registry only when `model` is absent
- [ ] `resolve()` raises error when neither present
- [ ] Existing tests pass (may need updates)
- [ ] New priority test passes
- [ ] `./scripts/ci-check.sh` passes

---

## Commit Message Template

```text
fix(resolver): Prioritize explicit model field over requirement resolution

When evaluator has explicit `model` field, use it directly instead of
resolving via registry. This prevents stale registry IDs from overriding
current model specifications.

New resolution order:
1. model field (explicit) → use directly
2. model_requirement (no model) → resolve via registry
3. neither → error

Fixes library evaluator compatibility with updated Anthropic model IDs.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

---

## After Implementation

1. Run tests: `pytest tests/test_model_resolver.py -v`
2. Run full CI: `./scripts/ci-check.sh`
3. Commit and push
4. Create PR targeting `main`
