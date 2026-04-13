# ADV-0015: Evaluators Module Skeleton + EvaluatorConfig

**Status**: Done
**Priority**: High
**Estimated Effort**: 2-3 hours
**Target Version**: v0.6.0
**Parent Epic**: ADV-0013
**Depends On**: None
**Branch**: `feature/plugin-architecture`

## Summary

Create the `adversarial_workflow/evaluators/` module with the `EvaluatorConfig` dataclass that will be the foundation for both built-in and custom evaluators.

## Background

This is the first step in the plugin architecture implementation. We need a well-defined data structure to represent evaluator configurations before we can parse YAML files or run evaluators.

## Requirements

### Create Module Structure

```text
adversarial_workflow/
└── evaluators/
    ├── __init__.py     # Export public API
    └── config.py       # EvaluatorConfig dataclass
```

### EvaluatorConfig Dataclass

```python
# adversarial_workflow/evaluators/config.py
from dataclasses import dataclass, field

@dataclass
class EvaluatorConfig:
    """Configuration for an evaluator (built-in or custom)."""

    # Required fields
    name: str                          # Command name (e.g., "evaluate", "athena")
    description: str                   # Help text for CLI
    model: str                         # Model to use (e.g., "gpt-4o", "gemini-2.5-pro")
    api_key_env: str                   # Environment variable for API key
    prompt: str                        # The evaluation prompt template
    output_suffix: str                 # Log file suffix (e.g., "PLAN-EVALUATION")

    # Optional fields with defaults
    log_prefix: str = ""               # CLI output prefix (e.g., "ATHENA")
    fallback_model: str | None = None  # Fallback model if primary fails
    aliases: list[str] = field(default_factory=list)  # Alternative command names
    version: str = "1.0.0"             # Evaluator version

    # Metadata (set internally)
    source: str = "builtin"            # "builtin" or "local"
    config_file: str | None = None     # Path to YAML file (if local)
```

### Module Exports

```python
# adversarial_workflow/evaluators/__init__.py
from .config import EvaluatorConfig

__all__ = ["EvaluatorConfig"]
```

## Testing Requirements

Create `tests/test_evaluator_config.py`:

1. **Test dataclass creation** - Verify all required fields work
2. **Test defaults** - Verify optional fields have correct defaults
3. **Test field types** - Verify type hints are accurate
4. **Test equality** - Two configs with same values are equal

```python
def test_evaluator_config_required_fields():
    config = EvaluatorConfig(
        name="test",
        description="Test evaluator",
        model="gpt-4o",
        api_key_env="OPENAI_API_KEY",
        prompt="Evaluate this",
        output_suffix="TEST-EVAL",
    )
    assert config.name == "test"
    assert config.aliases == []  # Default
    assert config.fallback_model is None  # Default

def test_evaluator_config_with_optionals():
    config = EvaluatorConfig(
        name="athena",
        description="Knowledge eval",
        model="gemini-2.5-pro",
        api_key_env="GEMINI_API_KEY",
        prompt="You are Athena...",
        output_suffix="KNOWLEDGE-EVAL",
        log_prefix="ATHENA",
        aliases=["knowledge", "research"],
        fallback_model="gpt-4o",
    )
    assert config.aliases == ["knowledge", "research"]
    assert config.fallback_model == "gpt-4o"
```

## Acceptance Criteria

- [ ] `adversarial_workflow/evaluators/` directory created
- [ ] `EvaluatorConfig` dataclass with all fields defined
- [ ] Type hints for Python 3.10+ compatibility
- [ ] Unit tests for dataclass behavior
- [ ] All existing tests still pass

## Implementation Notes

- Use `from __future__ import annotations` for Python 3.10 compatibility
- The `source` and `config_file` fields are metadata set during discovery, not from YAML
- Keep this simple - more complex validation happens in the parser (ADV-0016)

## References

- Parent Epic: ADV-0013-plugin-architecture-epic.md
- Proposal: docs/proposals/ADVERSARIAL-PLUGIN-IMPLEMENTATION-HANDOFF.md
