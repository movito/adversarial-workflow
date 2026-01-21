# ADV-0016: YAML Parsing and Evaluator Discovery

**Status**: Todo
**Priority**: High
**Estimated Effort**: 3-4 hours
**Target Version**: v0.6.0
**Parent Epic**: ADV-0013
**Depends On**: ADV-0015 (EvaluatorConfig)
**Branch**: `feature/plugin-architecture`

## Summary

Implement YAML parsing for custom evaluator definitions and the discovery mechanism that finds evaluators in `.adversarial/evaluators/*.yml`.

## Background

Projects need to define custom evaluators without modifying the installed package. This task implements the parser and discovery logic that reads YAML files and creates `EvaluatorConfig` objects.

## Scope Clarification

**This task focuses on**: YAML parsing and discovery only.

**Handled by dependent tasks**:
- **CLI Integration** (ADV-0018): How `EvaluatorConfig` objects become CLI commands via `get_all_evaluators()` in `main()`
- **Runtime Validation** (ADV-0017): API key validation, model execution, error handling
- **Model Validation**: Delegated to aider which validates models at runtime

**Design decisions**:
- Model names are NOT validated here - aider supports many models and validates them at runtime
- API key existence is NOT checked here - checked at execution time in runner
- This task produces `EvaluatorConfig` objects; CLI registration happens in ADV-0018
- Only `.yml` extension supported (not `.yaml`) - simplicity over flexibility
- UTF-8 encoding required; non-UTF-8 files raise `EvaluatorParseError`
- Subdirectories in `.adversarial/evaluators/` are NOT scanned - flat structure only
- Circular aliases are impossible by design: aliases point to `EvaluatorConfig` objects, not other alias names
- YAML multi-document files (---) use only first document (standard `safe_load` behavior)

**Integration with existing system**:
1. `discover_local_evaluators()` is called by `get_all_evaluators()` (defined in ADV-0017)
2. `get_all_evaluators()` merges built-in + local evaluators
3. `main()` in cli.py calls `get_all_evaluators()` to register CLI commands (ADV-0018)

## Requirements

### File Structure

```text
adversarial_workflow/
└── evaluators/
    ├── __init__.py     # Updated exports
    ├── config.py       # From ADV-0015
    └── discovery.py    # NEW: Discovery and parsing
```

### YAML Schema

```yaml
# .adversarial/evaluators/athena.yml
name: athena                         # Required: Command name
description: Knowledge evaluation    # Required: Help text
model: gemini-2.5-pro               # Required: Model to use
api_key_env: GEMINI_API_KEY         # Required: Env var for API key
output_suffix: KNOWLEDGE-EVALUATION # Required: Log file suffix
prompt: |                           # Required: The evaluation prompt
  You are Athena...

# Optional fields
version: 1.0.0                      # Evaluator version (default: 1.0.0)
log_prefix: "ATHENA"                # CLI output prefix (default: "")
fallback_model: gpt-4o              # Fallback if primary fails (default: null)
aliases:                            # Alternative command names (default: [])
  - knowledge
  - research
```

### Parser Implementation

```python
# adversarial_workflow/evaluators/discovery.py

import logging
import re
import yaml
from pathlib import Path
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
    try:
        content = yml_file.read_text(encoding='utf-8')
    except UnicodeDecodeError as e:
        raise EvaluatorParseError(f"File encoding error (not UTF-8): {yml_file}") from e

    data = yaml.safe_load(content)

    # Empty YAML (None, empty dict, or whitespace-only)
    if data is None or data == {} or (isinstance(data, str) and not data.strip()):
        raise EvaluatorParseError(f"Empty or invalid YAML file: {yml_file}")

    # Validate required fields
    required = ["name", "description", "model", "api_key_env", "prompt", "output_suffix"]
    missing = [f for f in required if f not in data]
    if missing:
        raise EvaluatorParseError(f"Missing required fields: {', '.join(missing)}")

    # Validate name is a valid CLI command name (alphanumeric, hyphens, underscores)
    import re
    name = data["name"]
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', name):
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
        raise EvaluatorParseError(f"aliases must be string or list, got {type(aliases).__name__}")

    # Validate aliases follow same naming rules
    for alias in data.get("aliases", []):
        if isinstance(alias, str) and not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', alias):
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
        "name", "description", "model", "api_key_env", "prompt",
        "output_suffix", "log_prefix", "fallback_model", "aliases", "version"
    }
    unknown = set(data.keys()) - known_fields
    if unknown:
        logger.warning(f"Unknown fields in {yml_file.name}: {', '.join(unknown)}")

    filtered_data = {k: v for k, v in data.items() if k in known_fields}

    # Create config with metadata
    config = EvaluatorConfig(
        **filtered_data,
        source="local",
        config_file=str(yml_file),
    )

    return config
```

### Discovery Implementation

```python
import logging

logger = logging.getLogger(__name__)

def discover_local_evaluators(base_path: Path | None = None) -> dict[str, EvaluatorConfig]:
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

    for yml_file in sorted(local_dir.glob("*.yml")):
        try:
            config = parse_evaluator_yaml(yml_file)

            # Check for name conflicts
            if config.name in evaluators:
                logger.warning(f"Evaluator '{config.name}' in {yml_file.name} conflicts with existing; skipping")
                continue

            # Register primary name
            evaluators[config.name] = config

            # Register aliases (point to same config object)
            for alias in config.aliases:
                if alias in evaluators:
                    logger.warning(f"Alias '{alias}' conflicts with existing evaluator; skipping alias")
                    continue
                evaluators[alias] = config

        except (EvaluatorParseError, yaml.YAMLError) as e:
            logger.warning(f"Skipping {yml_file.name}: {e}")
        except Exception as e:
            logger.warning(f"Could not load {yml_file.name}: {e}")

    return evaluators
```

### Module Exports

```python
# adversarial_workflow/evaluators/__init__.py
from .config import EvaluatorConfig
from .discovery import (
    discover_local_evaluators,
    parse_evaluator_yaml,
    EvaluatorParseError,
)

__all__ = [
    "EvaluatorConfig",
    "discover_local_evaluators",
    "parse_evaluator_yaml",
    "EvaluatorParseError",
]
```

## Testing Requirements

Create `tests/test_evaluator_discovery.py` (standard pytest location, discovered automatically):

```python
import pytest
from pathlib import Path
from adversarial_workflow.evaluators.discovery import (
    parse_evaluator_yaml,
    discover_local_evaluators,
    EvaluatorParseError,
)
```

### Parser Tests

```python
def test_parse_valid_yaml(tmp_path):
    """Parse a valid evaluator YAML."""
    yml = tmp_path / "test.yml"
    yml.write_text("""
name: test
description: Test evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Evaluate this
output_suffix: TEST-EVAL
""")
    config = parse_evaluator_yaml(yml)
    assert config.name == "test"
    assert config.source == "local"

def test_parse_missing_required_field(tmp_path):
    """Error on missing required field."""
    yml = tmp_path / "invalid.yml"
    yml.write_text("name: test\n")
    with pytest.raises(EvaluatorParseError, match="Missing required fields"):
        parse_evaluator_yaml(yml)

def test_parse_invalid_name(tmp_path):
    """Error on invalid evaluator name."""
    yml = tmp_path / "bad-name.yml"
    yml.write_text("""
name: 123-invalid
description: Bad name
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test
output_suffix: TEST
""")
    with pytest.raises(EvaluatorParseError, match="Invalid evaluator name"):
        parse_evaluator_yaml(yml)

def test_parse_invalid_alias(tmp_path):
    """Error on invalid alias name."""
    yml = tmp_path / "bad-alias.yml"
    yml.write_text("""
name: valid
description: Valid name but bad alias
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test
output_suffix: TEST
aliases:
  - 123-bad
""")
    with pytest.raises(EvaluatorParseError, match="Invalid alias"):
        parse_evaluator_yaml(yml)

def test_parse_empty_prompt(tmp_path):
    """Error on empty prompt."""
    yml = tmp_path / "empty-prompt.yml"
    yml.write_text("""
name: test
description: Test
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: ""
output_suffix: TEST
""")
    with pytest.raises(EvaluatorParseError, match="prompt cannot be empty"):
        parse_evaluator_yaml(yml)

def test_parse_encoding_error(tmp_path):
    """Error on non-UTF-8 file."""
    yml = tmp_path / "bad-encoding.yml"
    yml.write_bytes(b'\xff\xfe' + "name: test".encode('utf-16-le'))
    with pytest.raises(EvaluatorParseError, match="encoding error"):
        parse_evaluator_yaml(yml)

def test_parse_empty_yaml(tmp_path):
    """Error on empty or whitespace-only YAML."""
    yml = tmp_path / "empty.yml"
    yml.write_text("   \n   \n")
    with pytest.raises(EvaluatorParseError, match="Empty or invalid"):
        parse_evaluator_yaml(yml)

def test_parse_aliases_string(tmp_path):
    """Single alias as string converts to list."""
    yml = tmp_path / "test.yml"
    yml.write_text("""
name: test
description: Test
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test
output_suffix: TEST
aliases: alt_name
""")
    config = parse_evaluator_yaml(yml)
    assert config.aliases == ["alt_name"]
```

### Discovery Tests

```python
def test_discover_no_directory(tmp_path):
    """Empty dict when no evaluators directory."""
    result = discover_local_evaluators(tmp_path)
    assert result == {}

def test_discover_evaluators(tmp_path):
    """Discover multiple evaluators."""
    eval_dir = tmp_path / ".adversarial" / "evaluators"
    eval_dir.mkdir(parents=True)

    (eval_dir / "athena.yml").write_text("""
name: athena
description: Knowledge eval
model: gemini-2.5-pro
api_key_env: GEMINI_API_KEY
prompt: You are Athena
output_suffix: KNOWLEDGE-EVAL
aliases:
  - knowledge
""")

    result = discover_local_evaluators(tmp_path)
    assert "athena" in result
    assert "knowledge" in result
    assert result["athena"] is result["knowledge"]  # Same object

def test_discover_skips_invalid(tmp_path, capsys):
    """Skip invalid YAML with warning."""
    eval_dir = tmp_path / ".adversarial" / "evaluators"
    eval_dir.mkdir(parents=True)
    (eval_dir / "bad.yml").write_text("name: incomplete\n")

    result = discover_local_evaluators(tmp_path)
    assert result == {}
    assert "Skipping bad.yml" in capsys.readouterr().out
```

## Acceptance Criteria

- [ ] `parse_evaluator_yaml()` parses valid YAML into EvaluatorConfig
- [ ] Parser validates all required fields
- [ ] Parser validates name format (alphanumeric, hyphens, underscores, starts with letter)
- [ ] Parser validates alias names with same rules as primary names
- [ ] Parser validates prompt is non-empty
- [ ] Parser handles missing/None/string/list aliases
- [ ] Parser logs warning on unknown fields (doesn't fail)
- [ ] `discover_local_evaluators()` finds all `.yml` files
- [ ] Discovery handles missing directory gracefully
- [ ] Discovery registers aliases pointing to same config
- [ ] Discovery handles name conflicts (first-wins with logging)
- [ ] Invalid YAML files logged and skipped
- [ ] Consistent logging via `logging` module (no print/warnings.warn)
- [ ] Unit tests cover all edge cases including validation
- [ ] All existing tests still pass

## Implementation Notes

- Use `yaml.safe_load()` for security (no code execution)
- `pyyaml` is already a dependency (no new deps needed)
- Sort YAML files for deterministic discovery order
- Use `logging` module consistently for warnings (not print/warnings.warn)
- Logging uses standard Python `logging.getLogger(__name__)` pattern
- Logging configuration is handled by CLI entry point (not this module)
- Name validation ensures valid CLI command names
- Name conflicts are logged and skipped (first-wins policy)
- Performance: Discovery is fast (~10-50ms) for typical usage (<10 evaluators)
- Explicit UTF-8 encoding for file reading
- Symbolic links are followed (standard Path behavior)
- File permission errors are caught and logged as warnings

## References

- Parent Epic: ADV-0013-plugin-architecture-epic.md
- Depends On: ADV-0015-evaluators-module-skeleton.md
- Proposal: docs/proposals/ADVERSARIAL-PLUGIN-IMPLEMENTATION-HANDOFF.md
