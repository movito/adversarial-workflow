# ADV-0032: Resolver Model Field Priority

**Status**: In Progress
**Priority**: HIGH
**Created**: 2026-02-06
**Type**: Bug Fix / Architecture
**Source**: adversarial-evaluator-library feedback

---

## Problem Statement

The ModelResolver uses a hardcoded registry to resolve `model_requirement` → model ID. When model IDs are updated (e.g., Anthropic releasing `claude-opus-4-6`), the registry becomes stale.

**Current behavior**:
1. Evaluator has `model_requirement: {family: claude, tier: opus}` AND `model: claude-opus-4-6`
2. Resolver finds `claude/opus` in registry → returns `claude-4-opus-20260115` (OLD)
3. Evaluator's `model: claude-opus-4-6` field is ignored
4. Aider fails or uses wrong model

**Impact**:
- Library evaluators break when Anthropic/OpenAI/etc. update model IDs
- `list-evaluators` shows correct model (reads file), `evaluate` uses wrong model (uses resolver)

## Proposed Solution

**Change resolution priority**: When evaluator has explicit `model` field, use it directly. Only resolve `model_requirement` when `model` is absent.

**New resolution order**:
1. If `model` present → use directly (evaluator specifies exact model)
2. If `model_requirement` present AND `model` absent → resolve via registry
3. If neither → raise ResolutionError

**Rationale**:
- Evaluator authors know which model they want
- `model_requirement` becomes a fallback for truly portable evaluators
- No need to constantly update hardcoded registry
- Library team maintains current model IDs in evaluator files

## Implementation

### File: `adversarial_workflow/evaluators/resolver.py`

**Current code** (line 128-159):

```python
def resolve(self, config: EvaluatorConfig) -> tuple[str, str]:
    if config.model_requirement:
        try:
            return self._resolve_requirement(config.model_requirement)
        except ResolutionError as e:
            if config.model:
                # Fall back to legacy with warning
                warnings.warn(...)
                return (config.model, config.api_key_env)
            raise

    # Legacy only
    if config.model:
        return (config.model, config.api_key_env)

    raise ResolutionError("No model or model_requirement specified")
```

**New code**:

```python
def resolve(self, config: EvaluatorConfig) -> tuple[str, str]:
    # Priority 1: Explicit model field (evaluator specifies exact model)
    if config.model:
        return (config.model, config.api_key_env)

    # Priority 2: Resolve model_requirement via registry
    if config.model_requirement:
        return self._resolve_requirement(config.model_requirement)

    raise ResolutionError("No model or model_requirement specified")
```

## Acceptance Criteria

- [ ] Evaluator with `model` field uses that model directly
- [ ] Evaluator with only `model_requirement` uses registry resolution
- [ ] Evaluator with neither raises ResolutionError
- [ ] Backward compatible: existing evaluators still work
- [ ] Tests updated to reflect new priority
- [ ] CI passes

## Testing

Update `tests/test_model_resolver.py`:

```python
def test_model_field_takes_priority():
    """Explicit model field overrides model_requirement resolution."""
    config = EvaluatorConfig(
        name="test",
        model="claude-opus-4-6",  # Explicit model
        api_key_env="ANTHROPIC_API_KEY",
        model_requirement=ModelRequirement(family="claude", tier="opus"),
        # ... other fields
    )
    resolver = ModelResolver()
    model_id, api_key = resolver.resolve(config)

    # Should use explicit model, not registry resolution
    assert model_id == "claude-opus-4-6"
    assert "anthropic/" not in model_id  # No prefix added
```

## Notes

- This is a semantic change but improves maintainability
- Registry can still be useful for future Phase 2 features (user routing config)
- Library team can update model IDs without waiting for workflow releases

---

**Estimated Effort**: 1-2 hours
