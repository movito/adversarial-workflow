# ADV-0015: Model Routing Layer - Phase 1

**Status**: In Progress
**Priority**: Medium
**Estimated Effort**: 2-3 days
**Depends On**: ADV-0013 (Library CLI Core)
**Source**: Cross-project architecture alignment (ADR-0004)
**Library Status**: ✅ Interface Ready (2026-02-03)

---

## Summary

Implement Phase 1 of the model routing layer: support for both legacy `model` string field and structured `model_requirement` field in evaluator configurations. This enables gradual migration to the new routing architecture without breaking existing evaluators.

---

## Library Team Update (2026-02-03)

The adversarial-evaluator-library team has completed Phase 2 interface implementation per ADR-0005:

| Deliverable | Status | Details |
|-------------|--------|---------|
| Provider Registry | ✅ Published | `providers/registry.yml` |
| Schema v1.0 | ✅ Final | 7 families, 10+ tiers, litellm prefixes |
| Evaluator Updates | ✅ Complete | All 18 evaluators have `model_requirement` |
| Dual-Field Support | ✅ Active | Legacy `model` + new `model_requirement` |

**Registry Families Available:**

| Family | Vendor | Tiers | litellm_prefix |
|--------|--------|-------|----------------|
| gpt | OpenAI | flagship, standard, mini | `""` |
| o | OpenAI | flagship, mini | `""` |
| claude | Anthropic | opus, sonnet, haiku | `"anthropic/"` |
| gemini | Google | pro, flash | `"gemini/"` |
| mistral | Mistral | large, small | `"mistral/"` |
| codestral | Mistral | latest | `"mistral/"` |
| llama | Meta | large, medium | varies by host |

**Library PR**: https://github.com/movito/adversarial-evaluator-library/pull/3

---

## Background

### Problem Statement

The current evaluator configuration couples model specifications to specific API endpoints:

```yaml
# Current: WHAT and HOW are coupled
model: claude-4-opus-20260115      # Specific endpoint
api_key_env: ANTHROPIC_API_KEY     # Specific auth
```

This prevents users from choosing their preferred access method (direct API vs Vertex AI vs OpenRouter) without duplicating evaluator definitions.

### Solution: Layered Architecture (ADR-0004)

Separate evaluator definitions (WHAT) from model routing (HOW):

```yaml
# New: Requirements-based model specification
model_requirement:
  family: claude
  tier: opus
  min_version: "4"
```

### Phase 1 Scope

This task implements **dual-field support** only:
- Parse both `model` (legacy) and `model_requirement` (new) fields
- When `model_requirement` present, resolve to actual model ID
- Fall back to `model` field if `model_requirement` not present or fails
- No user routing config yet (Phase 2)

---

## Requirements

### 1. Model Requirement Data Structure

```python
# adversarial_workflow/evaluators/config.py

@dataclass
class ModelRequirement:
    """Model capability requirements (from library)."""
    family: str           # claude, openai, gemini, llama, mistral
    tier: str             # opus, sonnet, haiku / gpt4, gpt4o / pro, flash
    min_version: str = "" # Optional: minimum model generation
    min_context: int = 0  # Optional: minimum context window (tokens)
```

### 2. Extended EvaluatorConfig

```python
@dataclass
class EvaluatorConfig:
    # Existing fields (unchanged)
    name: str
    description: str
    model: str              # Legacy field, still supported
    api_key_env: str        # Legacy field, still supported
    prompt: str
    output_suffix: str
    # ... other existing fields ...

    # NEW: Structured model requirement
    model_requirement: ModelRequirement | None = None
```

### 3. Resolution Logic

```python
# adversarial_workflow/evaluators/resolver.py

class ModelResolver:
    """Resolves model requirements to actual model IDs."""

    # Default registry - matches adversarial-evaluator-library/providers/registry.yml
    # Updated 2026-02-03 per Library team handoff
    DEFAULT_REGISTRY = {
        "claude": {
            "opus": {"models": ["claude-4-opus-20260115", "claude-opus-4-5-20251101"], "prefix": "anthropic/"},
            "sonnet": {"models": ["claude-4-sonnet-20260115"], "prefix": "anthropic/"},
            "haiku": {"models": ["claude-4-haiku-20260115"], "prefix": "anthropic/"},
        },
        "gpt": {
            "flagship": {"models": ["gpt-4o", "gpt-4o-2024-08-06"], "prefix": ""},
            "standard": {"models": ["gpt-4-turbo", "gpt-4"], "prefix": ""},
            "mini": {"models": ["gpt-4o-mini"], "prefix": ""},
        },
        "o": {
            "flagship": {"models": ["o1", "o1-2024-12-17"], "prefix": ""},
            "mini": {"models": ["o3-mini"], "prefix": ""},
        },
        "gemini": {
            "pro": {"models": ["gemini-2.5-pro"], "prefix": "gemini/"},
            "flash": {"models": ["gemini-2.5-flash"], "prefix": "gemini/"},
        },
        "mistral": {
            "large": {"models": ["mistral-large-latest"], "prefix": "mistral/"},
            "small": {"models": ["mistral-small-latest"], "prefix": "mistral/"},
        },
        "codestral": {
            "latest": {"models": ["codestral-latest"], "prefix": "mistral/"},
        },
        "llama": {
            "large": {"models": ["llama-3.3-70b"], "prefix": ""},  # varies by host
            "medium": {"models": ["llama-3.1-8b"], "prefix": ""},
        },
    }

    def resolve(self, config: EvaluatorConfig) -> tuple[str, str]:
        """
        Resolve evaluator config to (model_id, api_key_env).

        Resolution order:
        1. If model_requirement present: resolve via registry
        2. Fall back to legacy model + api_key_env fields
        3. Error if neither works

        Returns:
            (model_id, api_key_env) tuple
        """
        if config.model_requirement:
            try:
                return self._resolve_requirement(config.model_requirement)
            except ResolutionError as e:
                if config.model:
                    # Fall back to legacy
                    warn(f"model_requirement resolution failed, using legacy: {e}")
                    return (config.model, config.api_key_env)
                raise

        # Legacy only
        if config.model:
            return (config.model, config.api_key_env)

        raise ResolutionError("No model or model_requirement specified")

    def _resolve_requirement(self, req: ModelRequirement) -> tuple[str, str]:
        """Resolve requirement to model ID."""
        family = self.DEFAULT_REGISTRY.get(req.family)
        if not family:
            raise ResolutionError(f"Unknown model family: {req.family}")

        tier_models = family.get(req.tier)
        if not tier_models:
            raise ResolutionError(f"Unknown tier {req.tier} for family {req.family}")

        # Return first (latest) model in tier
        model_id = tier_models[0]

        # Determine API key env from family
        api_key_env = self._get_api_key_env(req.family)

        return (model_id, api_key_env)

    def _get_api_key_env(self, family: str) -> str:
        """Get default API key environment variable for family."""
        return {
            "claude": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "llama": "TOGETHER_API_KEY",  # Default hosting
            "mistral": "MISTRAL_API_KEY",
        }.get(family, f"{family.upper()}_API_KEY")
```

### 4. Integration with Runner

Update the evaluator runner to use resolution:

```python
# adversarial_workflow/evaluators/runner.py

def _run_custom_evaluator(config: EvaluatorConfig, ...):
    # NEW: Resolve model before use
    resolver = ModelResolver()
    model_id, api_key_env = resolver.resolve(config)

    # Use resolved values
    cmd = [
        "aider",
        "--model", model_id,  # Was: config.model
        ...
    ]
```

### 5. YAML Loading

Update evaluator YAML loading to parse `model_requirement`:

```python
# adversarial_workflow/evaluators/discovery.py

def _load_evaluator_yaml(path: Path) -> EvaluatorConfig:
    data = yaml.safe_load(path.read_text())

    # Parse model_requirement if present
    model_req = None
    if "model_requirement" in data:
        req_data = data["model_requirement"]
        model_req = ModelRequirement(
            family=req_data["family"],
            tier=req_data["tier"],
            min_version=req_data.get("min_version", ""),
            min_context=req_data.get("min_context", 0),
        )

    return EvaluatorConfig(
        name=data["name"],
        model=data.get("model", ""),  # Optional now
        api_key_env=data.get("api_key_env", ""),  # Optional now
        model_requirement=model_req,
        ...
    )
```

---

## Acceptance Criteria

### Must Have

- [ ] `ModelRequirement` dataclass defined with family, tier, min_version, min_context
- [ ] `EvaluatorConfig` extended with optional `model_requirement` field
- [ ] `ModelResolver` class with embedded default registry
- [ ] Resolution logic: `model_requirement` → registry → fallback to `model`
- [ ] Clear error messages when resolution fails
- [ ] Warning when falling back to legacy field
- [ ] YAML loader parses `model_requirement` field
- [ ] Evaluator runner uses resolved model ID
- [ ] Backwards compatible: existing evaluators with only `model` still work
- [ ] Unit tests for resolver and all resolution paths
- [ ] Integration tests with sample evaluators

### Must NOT Have

- [ ] User routing configuration (Phase 2 - ADV-0016)
- [ ] External registry fetching (Phase 2)
- [ ] Breaking changes to existing evaluator format

---

## Testing Strategy

### Unit Tests

```python
# tests/test_model_resolver.py

def test_resolve_model_requirement_claude_opus():
    config = EvaluatorConfig(
        name="test",
        model_requirement=ModelRequirement(family="claude", tier="opus"),
        ...
    )
    resolver = ModelResolver()
    model_id, api_key_env = resolver.resolve(config)
    assert "claude" in model_id and "opus" in model_id
    assert api_key_env == "ANTHROPIC_API_KEY"

def test_resolve_legacy_model_field():
    config = EvaluatorConfig(
        name="test",
        model="gpt-4o",
        api_key_env="OPENAI_API_KEY",
        ...
    )
    resolver = ModelResolver()
    model_id, api_key_env = resolver.resolve(config)
    assert model_id == "gpt-4o"
    assert api_key_env == "OPENAI_API_KEY"

def test_resolve_fallback_on_requirement_failure():
    config = EvaluatorConfig(
        name="test",
        model="gpt-4o",  # Fallback
        api_key_env="OPENAI_API_KEY",
        model_requirement=ModelRequirement(family="unknown", tier="unknown"),
    )
    resolver = ModelResolver()
    with pytest.warns(UserWarning, match="resolution failed"):
        model_id, api_key_env = resolver.resolve(config)
    assert model_id == "gpt-4o"  # Fell back

def test_resolve_error_no_model_or_requirement():
    config = EvaluatorConfig(name="test", ...)
    resolver = ModelResolver()
    with pytest.raises(ResolutionError):
        resolver.resolve(config)
```

### Integration Tests

```python
# tests/test_resolver_integration.py

def test_run_evaluator_with_model_requirement(tmp_path):
    """Evaluator with model_requirement runs successfully."""
    evaluator_yaml = tmp_path / ".adversarial" / "evaluators" / "test.yml"
    evaluator_yaml.parent.mkdir(parents=True)
    evaluator_yaml.write_text("""
name: test-evaluator
model_requirement:
  family: openai
  tier: gpt4o
prompt: "Test prompt"
output_suffix: TEST
""")
    # ... verify evaluator loads and resolves correctly
```

---

## File Structure

```
adversarial_workflow/
├── evaluators/
│   ├── config.py          # MODIFY: Add ModelRequirement, update EvaluatorConfig
│   ├── discovery.py       # MODIFY: Parse model_requirement from YAML
│   ├── resolver.py        # NEW: ModelResolver class
│   └── runner.py          # MODIFY: Use resolver before running
```

---

## Migration Path

1. **Phase 1 (This Task)**: Dual field support, embedded registry
2. **Phase 2 (ADV-0016)**: User routing config, external registry
3. **Phase 3 (Future)**: Deprecate legacy `model` field

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Registry becomes stale | Medium | Embedded registry covers common models; Phase 2 adds external |
| Breaking existing evaluators | High | Backwards compatibility is mandatory; legacy fields always work |
| Resolution errors confusing | Medium | Clear error messages with suggestions |

---

## Related Documents

- **Architecture**: `docs/decisions/adr/library-refs/ADR-0004-evaluator-definition-model-routing-separation.md`
- **Interface Contract**: `docs/decisions/adr/library-refs/ADR-0005-library-workflow-interface-contract.md` ✅
- **Registry Schema**: `providers/registry.yml` in adversarial-evaluator-library (schema v1.0)
- **Prerequisite**: ADV-0013 (Library CLI Core - provides evaluators with `model_requirement`)
- **Follow-up**: ADV-0016 (Model Routing Layer - Phase 2: User routing config)
