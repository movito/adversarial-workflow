# ADV-0015 Handoff: Model Routing Layer - Phase 1

**Task**: ADV-0015 - Model Routing Layer - Phase 1
**Assigned To**: feature-developer
**Created By**: planner
**Date**: 2026-02-03

---

## Mission

Implement dual-field support for evaluator model resolution: parse both legacy `model` field and new `model_requirement` field, with automatic resolution via embedded registry. This enables Library team integration testing.

---

## Current State Analysis

### Existing Files to Modify

1. **`adversarial_workflow/evaluators/config.py`** (52 lines)
   - Current: `EvaluatorConfig` dataclass with `model: str` and `api_key_env: str`
   - Change: Add optional `model_requirement: ModelRequirement | None = None`
   - Add: New `ModelRequirement` dataclass

2. **`adversarial_workflow/evaluators/discovery.py`** (238 lines)
   - Current: Parses YAML with `known_fields` whitelist (line 147-159)
   - Change: Add `model_requirement` to known fields
   - Change: Parse nested `model_requirement` dict into `ModelRequirement` object
   - Change: Make `model` and `api_key_env` optional when `model_requirement` present

3. **`adversarial_workflow/evaluators/runner.py`** (200+ lines)
   - Current: Uses `config.model` directly (lines 134, 140, 171)
   - Change: Call `ModelResolver.resolve()` before using model
   - Change: Use resolved `(model_id, api_key_env)` tuple

### New File to Create

4. **`adversarial_workflow/evaluators/resolver.py`** (~150 lines)
   - `ResolutionError` exception class
   - `ModelResolver` class with embedded registry
   - `resolve(config) -> (model_id, api_key_env)` method
   - Fallback logic with warning

---

## Implementation Order (TDD)

### Phase 1: Data Structures (Tests First)

```python
# tests/test_model_resolver.py - write these first

def test_model_requirement_dataclass():
    """ModelRequirement stores family, tier, min_version, min_context."""
    req = ModelRequirement(family="claude", tier="opus")
    assert req.family == "claude"
    assert req.tier == "opus"
    assert req.min_version == ""  # default
    assert req.min_context == 0   # default

def test_evaluator_config_with_model_requirement():
    """EvaluatorConfig accepts optional model_requirement."""
    config = EvaluatorConfig(
        name="test", description="Test", model="", api_key_env="",
        prompt="Test", output_suffix="TEST",
        model_requirement=ModelRequirement(family="claude", tier="opus")
    )
    assert config.model_requirement is not None
```

Then implement in `config.py`:

```python
@dataclass
class ModelRequirement:
    """Model capability requirements (from library)."""
    family: str
    tier: str
    min_version: str = ""
    min_context: int = 0

@dataclass
class EvaluatorConfig:
    # ... existing fields ...

    # NEW: Structured model requirement (Phase 1)
    model_requirement: ModelRequirement | None = None
```

### Phase 2: Resolver Logic (Tests First)

```python
# tests/test_model_resolver.py - continued

def test_resolve_claude_opus():
    """Resolver maps claude/opus to correct model ID."""
    config = EvaluatorConfig(
        name="test", description="Test", model="", api_key_env="",
        prompt="Test", output_suffix="TEST",
        model_requirement=ModelRequirement(family="claude", tier="opus")
    )
    resolver = ModelResolver()
    model_id, api_key_env = resolver.resolve(config)
    assert "claude" in model_id.lower()
    assert "opus" in model_id.lower()
    assert api_key_env == "ANTHROPIC_API_KEY"

def test_resolve_legacy_fallback():
    """Resolver uses legacy model field when model_requirement absent."""
    config = EvaluatorConfig(
        name="test", description="Test",
        model="gpt-4o", api_key_env="OPENAI_API_KEY",
        prompt="Test", output_suffix="TEST"
    )
    resolver = ModelResolver()
    model_id, api_key_env = resolver.resolve(config)
    assert model_id == "gpt-4o"
    assert api_key_env == "OPENAI_API_KEY"

def test_resolve_fallback_on_unknown_family():
    """Resolver falls back to legacy when family unknown."""
    config = EvaluatorConfig(
        name="test", description="Test",
        model="gpt-4o", api_key_env="OPENAI_API_KEY",  # fallback
        prompt="Test", output_suffix="TEST",
        model_requirement=ModelRequirement(family="unknown", tier="unknown")
    )
    resolver = ModelResolver()
    with pytest.warns(UserWarning, match="resolution failed"):
        model_id, api_key_env = resolver.resolve(config)
    assert model_id == "gpt-4o"  # fell back

def test_resolve_error_when_no_model():
    """Resolver raises when neither model nor model_requirement present."""
    config = EvaluatorConfig(
        name="test", description="Test",
        model="", api_key_env="",
        prompt="Test", output_suffix="TEST"
    )
    resolver = ModelResolver()
    with pytest.raises(ResolutionError, match="No model"):
        resolver.resolve(config)
```

Then implement `resolver.py`.

### Phase 3: YAML Parsing (Tests First)

```python
# tests/test_evaluator_discovery.py - add these

def test_parse_yaml_with_model_requirement(tmp_path):
    """Parser handles model_requirement field."""
    yml = tmp_path / "test.yml"
    yml.write_text("""
name: test-eval
description: Test evaluator
model_requirement:
  family: gemini
  tier: flash
prompt: "Test prompt"
output_suffix: TEST
""")
    config = parse_evaluator_yaml(yml)
    assert config.model_requirement is not None
    assert config.model_requirement.family == "gemini"
    assert config.model_requirement.tier == "flash"
    assert config.model == ""  # not required when model_requirement present

def test_parse_yaml_with_both_fields(tmp_path):
    """Parser handles dual-field format (library format)."""
    yml = tmp_path / "test.yml"
    yml.write_text("""
name: test-eval
description: Test evaluator
model: gemini/gemini-2.5-flash
api_key_env: GEMINI_API_KEY
model_requirement:
  family: gemini
  tier: flash
  min_version: "2.5"
prompt: "Test prompt"
output_suffix: TEST
""")
    config = parse_evaluator_yaml(yml)
    assert config.model == "gemini/gemini-2.5-flash"  # legacy present
    assert config.model_requirement.family == "gemini"  # new present
```

Then update `discovery.py`.

### Phase 4: Runner Integration (Tests First)

```python
# tests/test_runner_resolution.py

def test_runner_uses_resolved_model(tmp_path, mocker):
    """Runner resolves model_requirement before execution."""
    # Mock subprocess to capture the model argument
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value = MagicMock(returncode=0)

    # Create evaluator with model_requirement only
    config = EvaluatorConfig(
        name="test", description="Test",
        model="", api_key_env="",
        prompt="Test", output_suffix="TEST",
        model_requirement=ModelRequirement(family="gemini", tier="flash"),
        source="local"
    )

    # ... setup and run ...

    # Verify resolved model was passed to aider
    call_args = mock_run.call_args
    assert "gemini" in str(call_args)  # resolved, not empty
```

Then update `runner.py`.

---

## Registry Data (From Library Team)

Use this embedded registry matching `providers/registry.yml`:

```python
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
        "large": {"models": ["llama-3.3-70b"], "prefix": ""},
        "medium": {"models": ["llama-3.1-8b"], "prefix": ""},
    },
}

API_KEY_MAP = {
    "claude": "ANTHROPIC_API_KEY",
    "gpt": "OPENAI_API_KEY",
    "o": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "codestral": "MISTRAL_API_KEY",
    "llama": "TOGETHER_API_KEY",
}
```

---

## Key Implementation Notes

### 1. Backwards Compatibility is MANDATORY

```python
# MUST work: Legacy evaluator with only model field
name: my-evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: "..."
output_suffix: TEST

# MUST work: New evaluator with only model_requirement
name: my-evaluator
model_requirement:
  family: gpt
  tier: flagship
prompt: "..."
output_suffix: TEST

# MUST work: Dual-field (library format)
name: my-evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
model_requirement:
  family: gpt
  tier: flagship
prompt: "..."
output_suffix: TEST
```

### 2. Resolution Order

1. If `model_requirement` present → resolve via registry
2. If resolution fails AND `model` present → warn + fallback to legacy
3. If resolution fails AND no `model` → raise `ResolutionError`
4. If no `model_requirement` AND `model` present → use legacy directly
5. If neither → raise `ResolutionError`

### 3. Warning Format

```python
import warnings

warnings.warn(
    f"model_requirement resolution failed for {config.name}: {error}. "
    f"Falling back to legacy model field: {config.model}",
    UserWarning
)
```

### 4. Error Format

```python
class ResolutionError(Exception):
    """Raised when model resolution fails."""
    pass

# Clear error messages:
raise ResolutionError(f"Unknown model family: {req.family}")
raise ResolutionError(f"Unknown tier '{req.tier}' for family '{req.family}'")
raise ResolutionError("No model or model_requirement specified")
```

---

## Files to Update Summary

| File | Action | Lines Changed (est.) |
|------|--------|---------------------|
| `evaluators/config.py` | Add ModelRequirement, extend EvaluatorConfig | +25 |
| `evaluators/resolver.py` | NEW FILE | +120 |
| `evaluators/discovery.py` | Parse model_requirement, make model optional | +30, ~10 modified |
| `evaluators/runner.py` | Use resolver before execution | +10, ~5 modified |
| `evaluators/__init__.py` | Export new classes | +3 |
| `tests/test_model_resolver.py` | NEW FILE | +150 |
| `tests/test_evaluator_discovery.py` | Add model_requirement tests | +50 |

---

## Integration Testing with Library

After implementation, test with real library evaluator:

```bash
# Install library evaluator
adversarial library install google/gemini-flash

# Check it has model_requirement
cat .adversarial/evaluators/google-gemini-flash.yml | grep -A4 model_requirement

# Run evaluation (should resolve model_requirement)
adversarial evaluate some-file.md --evaluator gemini-flash
```

---

## Related Documents

- **Task Spec**: `delegation/tasks/1-backlog/ADV-0015-model-routing-phase1.md`
- **ADR-0004**: `docs/decisions/adr/library-refs/ADR-0004-evaluator-definition-model-routing-separation.md`
- **ADR-0005**: `docs/decisions/adr/library-refs/ADR-0005-library-workflow-interface-contract.md`
- **Library Registry**: https://github.com/movito/adversarial-evaluator-library/blob/main/providers/registry.yml

---

## Definition of Done

- [ ] All 11 acceptance criteria met
- [ ] Unit tests for resolver (all resolution paths)
- [ ] Integration tests with sample evaluators
- [ ] Existing evaluators still work (backwards compat)
- [ ] CI passes
- [ ] Code review approved
