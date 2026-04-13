# ADV-0015 Task Starter

## Quick Context

You are implementing the foundation for the plugin architecture: the `EvaluatorConfig` dataclass and evaluators module skeleton.

**Branch**: `feature/adv-0015-evaluator-config`
**Base**: `main`
**Target Version**: v0.6.0

## Create Branch

```bash
git checkout main
git pull
git checkout -b feature/adv-0015-evaluator-config
```

## Files to Create

### 1. `adversarial_workflow/evaluators/__init__.py`

```python
"""
Evaluators module for adversarial-workflow.

This module provides the plugin architecture for custom evaluators.
"""

from .config import EvaluatorConfig

__all__ = ["EvaluatorConfig"]
```

### 2. `adversarial_workflow/evaluators/config.py`

```python
"""
EvaluatorConfig dataclass for evaluator definitions.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EvaluatorConfig:
    """Configuration for an evaluator (built-in or custom).

    This dataclass represents the configuration for any evaluator,
    whether built-in (evaluate, proofread, review) or custom
    (defined in .adversarial/evaluators/*.yml).

    Attributes:
        name: Command name (e.g., "evaluate", "athena")
        description: Help text shown in CLI
        model: Model to use (e.g., "gpt-4o", "gemini-2.5-pro")
        api_key_env: Environment variable name for API key
        prompt: The evaluation prompt template
        output_suffix: Log file suffix (e.g., "PLAN-EVALUATION")
        log_prefix: CLI output prefix (e.g., "ATHENA")
        fallback_model: Fallback model if primary fails
        aliases: Alternative command names
        version: Evaluator version
        source: "builtin" or "local" (set internally)
        config_file: Path to YAML file if local (set internally)
    """

    # Required fields
    name: str
    description: str
    model: str
    api_key_env: str
    prompt: str
    output_suffix: str

    # Optional fields with defaults
    log_prefix: str = ""
    fallback_model: str | None = None
    aliases: list[str] = field(default_factory=list)
    version: str = "1.0.0"

    # Metadata (set internally during discovery, not from YAML)
    source: str = "builtin"
    config_file: str | None = None
```

### 3. `tests/test_evaluator_config.py`

```python
"""Tests for EvaluatorConfig dataclass."""

import pytest

from adversarial_workflow.evaluators import EvaluatorConfig


class TestEvaluatorConfig:
    """Tests for EvaluatorConfig dataclass."""

    def test_required_fields_only(self):
        """Create config with only required fields."""
        config = EvaluatorConfig(
            name="test",
            description="Test evaluator",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            prompt="Evaluate this document",
            output_suffix="TEST-EVAL",
        )

        assert config.name == "test"
        assert config.description == "Test evaluator"
        assert config.model == "gpt-4o"
        assert config.api_key_env == "OPENAI_API_KEY"
        assert config.prompt == "Evaluate this document"
        assert config.output_suffix == "TEST-EVAL"

    def test_default_values(self):
        """Verify default values for optional fields."""
        config = EvaluatorConfig(
            name="test",
            description="Test",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            prompt="Test",
            output_suffix="TEST",
        )

        assert config.log_prefix == ""
        assert config.fallback_model is None
        assert config.aliases == []
        assert config.version == "1.0.0"
        assert config.source == "builtin"
        assert config.config_file is None

    def test_with_all_optional_fields(self):
        """Create config with all optional fields specified."""
        config = EvaluatorConfig(
            name="athena",
            description="Knowledge evaluation using Gemini 2.5 Pro",
            model="gemini-2.5-pro",
            api_key_env="GEMINI_API_KEY",
            prompt="You are Athena, a knowledge evaluation specialist...",
            output_suffix="KNOWLEDGE-EVAL",
            log_prefix="ATHENA",
            fallback_model="gpt-4o",
            aliases=["knowledge", "research"],
            version="1.0.0",
            source="local",
            config_file="/path/to/athena.yml",
        )

        assert config.name == "athena"
        assert config.log_prefix == "ATHENA"
        assert config.fallback_model == "gpt-4o"
        assert config.aliases == ["knowledge", "research"]
        assert config.source == "local"
        assert config.config_file == "/path/to/athena.yml"

    def test_aliases_not_shared_between_instances(self):
        """Verify aliases list is not shared between instances."""
        config1 = EvaluatorConfig(
            name="test1",
            description="Test 1",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            prompt="Test",
            output_suffix="TEST",
        )
        config2 = EvaluatorConfig(
            name="test2",
            description="Test 2",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            prompt="Test",
            output_suffix="TEST",
        )

        config1.aliases.append("alias1")

        assert config1.aliases == ["alias1"]
        assert config2.aliases == []  # Should NOT be affected

    def test_equality(self):
        """Two configs with same values are equal."""
        config1 = EvaluatorConfig(
            name="test",
            description="Test",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            prompt="Test",
            output_suffix="TEST",
        )
        config2 = EvaluatorConfig(
            name="test",
            description="Test",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            prompt="Test",
            output_suffix="TEST",
        )

        assert config1 == config2

    def test_inequality(self):
        """Two configs with different values are not equal."""
        config1 = EvaluatorConfig(
            name="test1",
            description="Test",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            prompt="Test",
            output_suffix="TEST",
        )
        config2 = EvaluatorConfig(
            name="test2",
            description="Test",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            prompt="Test",
            output_suffix="TEST",
        )

        assert config1 != config2
```

## Run Tests

```bash
# Run the new tests
pytest tests/test_evaluator_config.py -v

# Run all tests to ensure nothing is broken
pytest tests/ -v
```

## Verify Import Works

```bash
python -c "from adversarial_workflow.evaluators import EvaluatorConfig; print('Import OK')"
```

## Commit & Push

After tests pass:

```bash
git add -A
git commit -m "feat(evaluators): Add EvaluatorConfig dataclass for plugin architecture

- Create adversarial_workflow/evaluators/ module
- Add EvaluatorConfig dataclass with required and optional fields
- Include metadata fields (source, config_file) for discovery
- Add comprehensive unit tests

Part of ADV-0015 for v0.6.0 plugin architecture.

Co-Authored-By: Claude <noreply@anthropic.com>"

git push -u origin feature/adv-0015-evaluator-config
```

## Create PR

```bash
gh pr create --title "feat(evaluators): Add EvaluatorConfig dataclass (ADV-0015)" --body "$(cat <<'EOF'
## Summary

Implements ADV-0015: Creates the foundation for the plugin architecture with the `EvaluatorConfig` dataclass.

## Changes

- Created `adversarial_workflow/evaluators/` module
- Added `EvaluatorConfig` dataclass with:
  - Required fields: name, description, model, api_key_env, prompt, output_suffix
  - Optional fields: log_prefix, fallback_model, aliases, version
  - Metadata fields: source, config_file
- Added comprehensive unit tests

## Test plan

- [x] `pytest tests/test_evaluator_config.py -v` passes
- [x] `pytest tests/ -v` - all existing tests pass
- [x] Import verification: `from adversarial_workflow.evaluators import EvaluatorConfig`

## Related

- Task: ADV-0015-evaluators-module-skeleton.md
- Epic: ADV-0013 Plugin Architecture
- Target: v0.6.0

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

## Acceptance Checklist

- [ ] `adversarial_workflow/evaluators/` directory exists
- [ ] `EvaluatorConfig` dataclass has all fields defined
- [ ] Type hints use Python 3.10+ syntax with `from __future__ import annotations`
- [ ] Unit tests pass
- [ ] All existing tests still pass
- [ ] PR created and ready for review
