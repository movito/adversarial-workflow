# ADV-0015 Review Starter

## Quick Context

Review the EvaluatorConfig dataclass implementation - the foundation for the plugin architecture.

**Branch**: `feature/adv-0015-evaluator-config`
**PR**: https://github.com/movito/adversarial-workflow/pull/7
**Commits**:
- `6cd3ef8` - "feat(evaluators): Add EvaluatorConfig dataclass for plugin architecture"
- `abea4b9` - "fix(build): Use package auto-discovery to include evaluators subpackage"

## Files to Review

1. `adversarial_workflow/evaluators/__init__.py` (9 lines)
2. `adversarial_workflow/evaluators/config.py` (49 lines)
3. `tests/test_evaluator_config.py` (135 lines)
4. `pyproject.toml` (package discovery fix)

## Review Checklist

### 1. EvaluatorConfig Dataclass (HIGH)

**File**: `adversarial_workflow/evaluators/config.py`

Verify the dataclass has correct structure:

```python
@dataclass
class EvaluatorConfig:
    # Required fields (6)
    name: str
    description: str
    model: str
    api_key_env: str
    prompt: str
    output_suffix: str

    # Optional fields with defaults (4)
    log_prefix: str = ""
    fallback_model: str | None = None
    aliases: list[str] = field(default_factory=list)
    version: str = "1.0.0"

    # Metadata fields (2)
    source: str = "builtin"
    config_file: str | None = None
```

**Review questions**:
- Are all 6 required fields present and correctly typed?
- Does `aliases` use `field(default_factory=list)` to avoid mutable default?
- Are type hints using Python 3.10+ syntax (`str | None` vs `Optional[str]`)?
- Is `from __future__ import annotations` present for forward compatibility?

### 2. Module Exports (MEDIUM)

**File**: `adversarial_workflow/evaluators/__init__.py`

Verify clean public API:

```python
from .config import EvaluatorConfig

__all__ = ["EvaluatorConfig"]
```

**Review questions**:
- Is `EvaluatorConfig` exported in `__all__`?
- Can it be imported as `from adversarial_workflow.evaluators import EvaluatorConfig`?

### 3. Test Coverage (HIGH)

**File**: `tests/test_evaluator_config.py`

Verify tests cover:

| Test | Purpose |
|------|---------|
| `test_required_fields_only` | Create config with minimum fields |
| `test_default_values` | Verify all optional field defaults |
| `test_with_all_optional_fields` | Create config with all fields |
| `test_aliases_not_shared_between_instances` | Mutable default safety |
| `test_equality` | Dataclass equality works |
| `test_inequality` | Different configs are not equal |

**Review questions**:
- Do tests cover all required fields?
- Is the mutable default test verifying `field(default_factory=list)` works correctly?
- Are there any missing edge cases?

### 4. Package Discovery Fix (HIGH)

**File**: `pyproject.toml`

Verify package auto-discovery:

```toml
# OLD (broken for subpackages):
[tool.setuptools]
packages = ["adversarial_workflow"]

# NEW (includes all subpackages):
[tool.setuptools.packages.find]
where = ["."]
include = ["adversarial_workflow*"]
```

**Review questions**:
- Will this include `adversarial_workflow.evaluators` in pip installs?
- Does the glob pattern `adversarial_workflow*` match all subpackages?

## Bot Review Findings (Already Addressed)

### Cursor Bot (Fixed ✅)
- **High Severity**: Package not included in distribution - Fixed with auto-discovery

### CodeRabbit (Nitpicks - Optional)
1. Consider `Literal["builtin", "local"]` for `source` field type safety
2. Consider `Path | None` instead of `str | None` for `config_file`
3. Consider `frozen=True` for immutability
4. Remove unused `pytest` import in tests
5. Add negative test cases (missing required fields)

These are optional enhancements for future iterations.

## Commands

```bash
# Checkout the branch
git fetch origin
git checkout feature/adv-0015-evaluator-config

# View all changes
git diff main...feature/adv-0015-evaluator-config

# Run tests
source .venv/bin/activate
pytest tests/test_evaluator_config.py -v

# Verify import works
python -c "from adversarial_workflow.evaluators import EvaluatorConfig; print('OK')"

# Check PR status
gh pr view 7 --json state,reviews

# View in browser
gh pr view 7 --web
```

## Expected Outcome

- [ ] EvaluatorConfig has all 12 fields correctly defined
- [ ] Module exports are clean (`__all__` defined)
- [ ] All 6 tests pass
- [ ] Package discovery includes subpackages
- [ ] No regressions in existing 72 tests
- [ ] PR ready for approval
