# ADV-0016 Task Starter

## Quick Context

You are implementing YAML parsing and evaluator discovery for the plugin architecture. This allows users to define custom evaluators in `.adversarial/evaluators/*.yml` files.

**Branch**: `feature/adv-0016-evaluator-discovery`
**Base**: `main`
**Depends On**: ADV-0015 (EvaluatorConfig) - already merged
**Target Version**: v0.6.0

## Create Branch

```bash
git checkout main
git pull
git checkout -b feature/adv-0016-evaluator-discovery
```

## Files to Create/Modify

### 1. Create `adversarial_workflow/evaluators/discovery.py`

```python
"""
YAML parsing and discovery for custom evaluators.

This module handles discovering evaluator definitions from
.adversarial/evaluators/*.yml files and parsing them into
EvaluatorConfig objects.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import yaml

from .config import EvaluatorConfig

logger = logging.getLogger(__name__)


class EvaluatorParseError(Exception):
    """Raised when evaluator YAML is invalid."""

    pass


def parse_evaluator_yaml(yml_file: Path) -> EvaluatorConfig:
    """Parse a YAML file into an EvaluatorConfig.

    Args:
        yml_file: Path to the YAML file

    Returns:
        EvaluatorConfig instance

    Raises:
        EvaluatorParseError: If YAML is invalid or missing required fields
        yaml.YAMLError: If YAML syntax is invalid
    """
    # Read file with explicit UTF-8 encoding
    try:
        content = yml_file.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        raise EvaluatorParseError(
            f"File encoding error (not UTF-8): {yml_file}"
        ) from e

    # Parse YAML
    data = yaml.safe_load(content)

    # Check for empty YAML
    if data is None or data == {} or (isinstance(data, str) and not data.strip()):
        raise EvaluatorParseError(f"Empty or invalid YAML file: {yml_file}")

    # Validate required fields
    required = ["name", "description", "model", "api_key_env", "prompt", "output_suffix"]
    missing = [f for f in required if f not in data]
    if missing:
        raise EvaluatorParseError(f"Missing required fields: {', '.join(missing)}")

    # Validate name format (valid CLI command name)
    name = data["name"]
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", name):
        raise EvaluatorParseError(
            f"Invalid evaluator name '{name}': must start with letter, "
            "contain only letters, numbers, hyphens, underscores"
        )

    # Normalize aliases (handle None, string, or list)
    aliases = data.get("aliases")
    if aliases is None:
        data["aliases"] = []
    elif isinstance(aliases, str):
        data["aliases"] = [aliases]
    elif not isinstance(aliases, list):
        raise EvaluatorParseError(
            f"aliases must be string or list, got {type(aliases).__name__}"
        )

    # Validate alias names
    for alias in data.get("aliases", []):
        if isinstance(alias, str) and not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", alias):
            raise EvaluatorParseError(
                f"Invalid alias '{alias}': must start with letter, "
                "contain only letters, numbers, hyphens, underscores"
            )

    # Validate prompt is non-empty
    prompt = data.get("prompt", "")
    if not prompt or not prompt.strip():
        raise EvaluatorParseError("prompt cannot be empty")

    # Filter to known fields only (log unknown fields)
    known_fields = {
        "name",
        "description",
        "model",
        "api_key_env",
        "prompt",
        "output_suffix",
        "log_prefix",
        "fallback_model",
        "aliases",
        "version",
    }
    unknown = set(data.keys()) - known_fields
    if unknown:
        logger.warning(f"Unknown fields in {yml_file.name}: {', '.join(sorted(unknown))}")

    # Build filtered data dict
    filtered_data = {k: v for k, v in data.items() if k in known_fields}

    # Create config with metadata
    config = EvaluatorConfig(
        **filtered_data,
        source="local",
        config_file=str(yml_file),
    )

    return config


def discover_local_evaluators(
    base_path: Path | None = None,
) -> dict[str, EvaluatorConfig]:
    """Discover evaluators from .adversarial/evaluators/*.yml

    Args:
        base_path: Project root (default: current directory)

    Returns:
        Dict mapping evaluator name (and aliases) to EvaluatorConfig
    """
    if base_path is None:
        base_path = Path.cwd()

    evaluators: dict[str, EvaluatorConfig] = {}
    local_dir = base_path / ".adversarial" / "evaluators"

    if not local_dir.exists():
        return evaluators

    # Sort for deterministic order
    for yml_file in sorted(local_dir.glob("*.yml")):
        try:
            config = parse_evaluator_yaml(yml_file)

            # Check for name conflicts
            if config.name in evaluators:
                logger.warning(
                    f"Evaluator '{config.name}' in {yml_file.name} "
                    "conflicts with existing; skipping"
                )
                continue

            # Register primary name
            evaluators[config.name] = config

            # Register aliases (point to same config object)
            for alias in config.aliases:
                if alias in evaluators:
                    logger.warning(
                        f"Alias '{alias}' conflicts with existing evaluator; "
                        "skipping alias"
                    )
                    continue
                evaluators[alias] = config

        except EvaluatorParseError as e:
            logger.warning(f"Skipping {yml_file.name}: {e}")
        except yaml.YAMLError as e:
            logger.warning(f"Skipping {yml_file.name}: YAML syntax error: {e}")
        except Exception as e:
            logger.warning(f"Could not load {yml_file.name}: {e}")

    return evaluators
```

### 2. Update `adversarial_workflow/evaluators/__init__.py`

```python
"""
Evaluators module for adversarial-workflow.

This module provides the plugin architecture for custom evaluators.
"""

from .config import EvaluatorConfig
from .discovery import (
    EvaluatorParseError,
    discover_local_evaluators,
    parse_evaluator_yaml,
)

__all__ = [
    "EvaluatorConfig",
    "EvaluatorParseError",
    "discover_local_evaluators",
    "parse_evaluator_yaml",
]
```

### 3. Create `tests/test_evaluator_discovery.py`

```python
"""Tests for evaluator YAML parsing and discovery."""

import pytest

from adversarial_workflow.evaluators import (
    EvaluatorParseError,
    discover_local_evaluators,
    parse_evaluator_yaml,
)


class TestParseEvaluatorYaml:
    """Tests for parse_evaluator_yaml function."""

    def test_parse_valid_yaml(self, tmp_path):
        """Parse a valid evaluator YAML with all required fields."""
        yml = tmp_path / "test.yml"
        yml.write_text(
            """
name: test
description: Test evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Evaluate this document
output_suffix: TEST-EVAL
"""
        )
        config = parse_evaluator_yaml(yml)

        assert config.name == "test"
        assert config.description == "Test evaluator"
        assert config.model == "gpt-4o"
        assert config.api_key_env == "OPENAI_API_KEY"
        assert config.prompt == "Evaluate this document"
        assert config.output_suffix == "TEST-EVAL"
        assert config.source == "local"
        assert config.config_file == str(yml)

    def test_parse_with_optional_fields(self, tmp_path):
        """Parse YAML with all optional fields specified."""
        yml = tmp_path / "athena.yml"
        yml.write_text(
            """
name: athena
description: Knowledge evaluation
model: gemini-2.5-pro
api_key_env: GEMINI_API_KEY
prompt: You are Athena
output_suffix: KNOWLEDGE-EVAL
log_prefix: ATHENA
fallback_model: gpt-4o
version: 2.0.0
aliases:
  - knowledge
  - research
"""
        )
        config = parse_evaluator_yaml(yml)

        assert config.name == "athena"
        assert config.log_prefix == "ATHENA"
        assert config.fallback_model == "gpt-4o"
        assert config.version == "2.0.0"
        assert config.aliases == ["knowledge", "research"]

    def test_parse_missing_required_field(self, tmp_path):
        """Error on missing required field."""
        yml = tmp_path / "invalid.yml"
        yml.write_text("name: test\ndescription: Test\n")

        with pytest.raises(EvaluatorParseError, match="Missing required fields"):
            parse_evaluator_yaml(yml)

    def test_parse_invalid_name_starts_with_number(self, tmp_path):
        """Error on name starting with number."""
        yml = tmp_path / "bad-name.yml"
        yml.write_text(
            """
name: 123-invalid
description: Bad name
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test
output_suffix: TEST
"""
        )

        with pytest.raises(EvaluatorParseError, match="Invalid evaluator name"):
            parse_evaluator_yaml(yml)

    def test_parse_invalid_name_special_chars(self, tmp_path):
        """Error on name with invalid special characters."""
        yml = tmp_path / "bad-name.yml"
        yml.write_text(
            """
name: test@invalid
description: Bad name
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test
output_suffix: TEST
"""
        )

        with pytest.raises(EvaluatorParseError, match="Invalid evaluator name"):
            parse_evaluator_yaml(yml)

    def test_parse_invalid_alias(self, tmp_path):
        """Error on invalid alias name."""
        yml = tmp_path / "bad-alias.yml"
        yml.write_text(
            """
name: valid
description: Valid name but bad alias
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test
output_suffix: TEST
aliases:
  - 123-bad
"""
        )

        with pytest.raises(EvaluatorParseError, match="Invalid alias"):
            parse_evaluator_yaml(yml)

    def test_parse_empty_prompt(self, tmp_path):
        """Error on empty prompt."""
        yml = tmp_path / "empty-prompt.yml"
        yml.write_text(
            """
name: test
description: Test
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: ""
output_suffix: TEST
"""
        )

        with pytest.raises(EvaluatorParseError, match="prompt cannot be empty"):
            parse_evaluator_yaml(yml)

    def test_parse_whitespace_prompt(self, tmp_path):
        """Error on whitespace-only prompt."""
        yml = tmp_path / "whitespace-prompt.yml"
        yml.write_text(
            """
name: test
description: Test
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: "   "
output_suffix: TEST
"""
        )

        with pytest.raises(EvaluatorParseError, match="prompt cannot be empty"):
            parse_evaluator_yaml(yml)

    def test_parse_encoding_error(self, tmp_path):
        """Error on non-UTF-8 file."""
        yml = tmp_path / "bad-encoding.yml"
        yml.write_bytes(b"\xff\xfe" + "name: test".encode("utf-16-le"))

        with pytest.raises(EvaluatorParseError, match="encoding error"):
            parse_evaluator_yaml(yml)

    def test_parse_empty_yaml(self, tmp_path):
        """Error on empty YAML file."""
        yml = tmp_path / "empty.yml"
        yml.write_text("")

        with pytest.raises(EvaluatorParseError, match="Empty or invalid"):
            parse_evaluator_yaml(yml)

    def test_parse_whitespace_only_yaml(self, tmp_path):
        """Error on whitespace-only YAML file."""
        yml = tmp_path / "whitespace.yml"
        yml.write_text("   \n   \n")

        with pytest.raises(EvaluatorParseError, match="Empty or invalid"):
            parse_evaluator_yaml(yml)

    def test_parse_aliases_as_string(self, tmp_path):
        """Single alias as string converts to list."""
        yml = tmp_path / "test.yml"
        yml.write_text(
            """
name: test
description: Test
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: TEST
aliases: alt_name
"""
        )
        config = parse_evaluator_yaml(yml)

        assert config.aliases == ["alt_name"]

    def test_parse_aliases_as_list(self, tmp_path):
        """Multiple aliases as list."""
        yml = tmp_path / "test.yml"
        yml.write_text(
            """
name: test
description: Test
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: TEST
aliases:
  - alt1
  - alt2
"""
        )
        config = parse_evaluator_yaml(yml)

        assert config.aliases == ["alt1", "alt2"]

    def test_parse_aliases_none(self, tmp_path):
        """Missing aliases defaults to empty list."""
        yml = tmp_path / "test.yml"
        yml.write_text(
            """
name: test
description: Test
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: TEST
"""
        )
        config = parse_evaluator_yaml(yml)

        assert config.aliases == []

    def test_parse_unknown_fields_logged(self, tmp_path, caplog):
        """Unknown fields are logged as warnings but don't cause failure."""
        yml = tmp_path / "test.yml"
        yml.write_text(
            """
name: test
description: Test
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: TEST
unknown_field: some value
another_unknown: 123
"""
        )

        import logging

        with caplog.at_level(logging.WARNING):
            config = parse_evaluator_yaml(yml)

        assert config.name == "test"
        assert "Unknown fields" in caplog.text
        assert "unknown_field" in caplog.text


class TestDiscoverLocalEvaluators:
    """Tests for discover_local_evaluators function."""

    def test_discover_no_directory(self, tmp_path):
        """Empty dict when no .adversarial/evaluators directory."""
        result = discover_local_evaluators(tmp_path)

        assert result == {}

    def test_discover_empty_directory(self, tmp_path):
        """Empty dict when evaluators directory is empty."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)

        result = discover_local_evaluators(tmp_path)

        assert result == {}

    def test_discover_single_evaluator(self, tmp_path):
        """Discover a single evaluator."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "test.yml").write_text(
            """
name: test
description: Test evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: TEST-EVAL
"""
        )

        result = discover_local_evaluators(tmp_path)

        assert "test" in result
        assert result["test"].name == "test"
        assert result["test"].source == "local"

    def test_discover_multiple_evaluators(self, tmp_path):
        """Discover multiple evaluators."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)

        (eval_dir / "alpha.yml").write_text(
            """
name: alpha
description: Alpha evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Alpha prompt
output_suffix: ALPHA-EVAL
"""
        )
        (eval_dir / "beta.yml").write_text(
            """
name: beta
description: Beta evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Beta prompt
output_suffix: BETA-EVAL
"""
        )

        result = discover_local_evaluators(tmp_path)

        assert len(result) == 2
        assert "alpha" in result
        assert "beta" in result

    def test_discover_evaluator_with_aliases(self, tmp_path):
        """Discover evaluator with aliases - aliases map to same config."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "athena.yml").write_text(
            """
name: athena
description: Knowledge eval
model: gemini-2.5-pro
api_key_env: GEMINI_API_KEY
prompt: You are Athena
output_suffix: KNOWLEDGE-EVAL
aliases:
  - knowledge
  - research
"""
        )

        result = discover_local_evaluators(tmp_path)

        assert "athena" in result
        assert "knowledge" in result
        assert "research" in result
        # All point to same config object
        assert result["athena"] is result["knowledge"]
        assert result["athena"] is result["research"]

    def test_discover_skips_invalid_yaml(self, tmp_path, caplog):
        """Invalid YAML files are skipped with warning."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "bad.yml").write_text("name: incomplete\n")
        (eval_dir / "good.yml").write_text(
            """
name: good
description: Good evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Good prompt
output_suffix: GOOD-EVAL
"""
        )

        import logging

        with caplog.at_level(logging.WARNING):
            result = discover_local_evaluators(tmp_path)

        assert "good" in result
        assert "incomplete" not in result
        assert "Skipping bad.yml" in caplog.text

    def test_discover_name_conflict_first_wins(self, tmp_path, caplog):
        """First evaluator wins on name conflict (sorted order)."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)

        # 'aaa.yml' comes before 'zzz.yml' in sorted order
        (eval_dir / "aaa.yml").write_text(
            """
name: duplicate
description: First one
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: First prompt
output_suffix: FIRST
"""
        )
        (eval_dir / "zzz.yml").write_text(
            """
name: duplicate
description: Second one
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Second prompt
output_suffix: SECOND
"""
        )

        import logging

        with caplog.at_level(logging.WARNING):
            result = discover_local_evaluators(tmp_path)

        assert result["duplicate"].description == "First one"
        assert "conflicts with existing" in caplog.text

    def test_discover_alias_conflict_skipped(self, tmp_path, caplog):
        """Alias conflicting with existing name is skipped."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)

        (eval_dir / "aaa.yml").write_text(
            """
name: first
description: First evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: First prompt
output_suffix: FIRST
"""
        )
        (eval_dir / "bbb.yml").write_text(
            """
name: second
description: Second evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Second prompt
output_suffix: SECOND
aliases:
  - first
"""
        )

        import logging

        with caplog.at_level(logging.WARNING):
            result = discover_local_evaluators(tmp_path)

        assert result["first"].name == "first"  # Original, not alias
        assert result["second"].name == "second"
        assert "Alias 'first' conflicts" in caplog.text

    def test_discover_uses_cwd_by_default(self, tmp_path, monkeypatch):
        """Uses current working directory when base_path is None."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "test.yml").write_text(
            """
name: test
description: Test
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test
output_suffix: TEST
"""
        )

        monkeypatch.chdir(tmp_path)
        result = discover_local_evaluators()  # No base_path argument

        assert "test" in result

    def test_discover_ignores_non_yml_files(self, tmp_path):
        """Only .yml files are discovered, not .yaml or others."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)

        # This should be discovered
        (eval_dir / "good.yml").write_text(
            """
name: good
description: Good
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Good
output_suffix: GOOD
"""
        )

        # These should be ignored
        (eval_dir / "ignored.yaml").write_text(
            """
name: ignored
description: Ignored
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Ignored
output_suffix: IGNORED
"""
        )
        (eval_dir / "readme.md").write_text("# README")
        (eval_dir / "config.json").write_text("{}")

        result = discover_local_evaluators(tmp_path)

        assert "good" in result
        assert "ignored" not in result
        assert len(result) == 1
```

## Run Tests

```bash
# Run the new tests
pytest tests/test_evaluator_discovery.py -v

# Run all tests to ensure nothing is broken
pytest tests/ -v
```

## Verify Imports Work

```bash
python -c "
from adversarial_workflow.evaluators import (
    EvaluatorConfig,
    EvaluatorParseError,
    discover_local_evaluators,
    parse_evaluator_yaml,
)
print('All imports OK')
"
```

## Manual Test (Optional)

Create a test evaluator to verify discovery works:

```bash
mkdir -p .adversarial/evaluators
cat > .adversarial/evaluators/test-evaluator.yml << 'EOF'
name: test-evaluator
description: A test evaluator for verification
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: This is a test prompt
output_suffix: TEST-EVAL
aliases:
  - tester
EOF

python -c "
from adversarial_workflow.evaluators import discover_local_evaluators
evaluators = discover_local_evaluators()
print(f'Discovered {len(evaluators)} evaluators:')
for name, config in evaluators.items():
    print(f'  - {name}: {config.description}')
"

# Cleanup
rm -rf .adversarial/evaluators/test-evaluator.yml
```

## Commit & Push

After tests pass:

```bash
git add -A
git commit -m "feat(evaluators): Add YAML parsing and evaluator discovery

- Add discovery.py with parse_evaluator_yaml() and discover_local_evaluators()
- Implement EvaluatorParseError for validation errors
- Validate name format, aliases, and prompt content
- Handle encoding errors and empty files gracefully
- Log warnings for unknown fields and conflicts
- Update __init__.py exports
- Add comprehensive test coverage (25+ test cases)

Part of ADV-0016 for v0.6.0 plugin architecture.

Co-Authored-By: Claude <noreply@anthropic.com>"

git push -u origin feature/adv-0016-evaluator-discovery
```

## Create PR

```bash
gh pr create --title "feat(evaluators): Add YAML parsing and evaluator discovery (ADV-0016)" --body "$(cat <<'EOF'
## Summary

Implements ADV-0016: Adds YAML parsing and discovery for custom evaluators defined in `.adversarial/evaluators/*.yml`.

## Changes

- Created `adversarial_workflow/evaluators/discovery.py` with:
  - `parse_evaluator_yaml()` - Parse YAML into EvaluatorConfig
  - `discover_local_evaluators()` - Find all evaluators in directory
  - `EvaluatorParseError` - Custom exception for validation errors
- Updated `__init__.py` with new exports
- Added comprehensive test suite (25+ test cases)

## Validation Features

- Required field validation (name, description, model, api_key_env, prompt, output_suffix)
- Name format validation (alphanumeric, hyphens, underscores)
- Alias validation (same rules as names)
- Empty prompt detection
- UTF-8 encoding enforcement
- Unknown field warnings
- Name/alias conflict handling (first-wins policy)

## Test plan

- [x] `pytest tests/test_evaluator_discovery.py -v` passes
- [x] `pytest tests/ -v` - all existing tests pass
- [x] Import verification for all exports
- [x] Manual discovery test with sample YAML

## Related

- Task: ADV-0016-evaluator-discovery.md
- Depends on: ADV-0015 (EvaluatorConfig)
- Epic: ADV-0013 Plugin Architecture
- Target: v0.6.0

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

## Acceptance Checklist

- [ ] `adversarial_workflow/evaluators/discovery.py` created
- [ ] `parse_evaluator_yaml()` validates all required fields
- [ ] `parse_evaluator_yaml()` validates name format
- [ ] `parse_evaluator_yaml()` validates alias names
- [ ] `parse_evaluator_yaml()` validates prompt is non-empty
- [ ] `parse_evaluator_yaml()` handles encoding errors
- [ ] `discover_local_evaluators()` finds all `.yml` files
- [ ] `discover_local_evaluators()` handles missing directory
- [ ] `discover_local_evaluators()` registers aliases correctly
- [ ] `discover_local_evaluators()` handles conflicts with logging
- [ ] `__init__.py` exports updated
- [ ] All tests pass (new + existing)
- [ ] PR created and ready for review
