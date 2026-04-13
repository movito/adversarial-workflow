# ADV-0016 Review Starter

## Quick Context

Review the YAML parsing and evaluator discovery implementation - enables users to define custom evaluators in `.adversarial/evaluators/*.yml` files.

**Branch**: `feature/adv-0016-evaluator-discovery`
**PR**: https://github.com/movito/adversarial-workflow/pull/8
**Commits**:
- `c6c15bb` - "feat(evaluators): Add YAML parsing and evaluator discovery"
- `7a1c57c` - "fix(evaluators): Add type validation for required fields and aliases"

## Files to Review

1. `adversarial_workflow/evaluators/discovery.py` (190 lines)
2. `adversarial_workflow/evaluators/__init__.py` (19 lines - updated exports)
3. `tests/test_evaluator_discovery.py` (418 lines - 29 test cases)

## Review Checklist

### 1. parse_evaluator_yaml Function (HIGH)

**File**: `adversarial_workflow/evaluators/discovery.py:26-133`

Verify YAML parsing with proper validation:

```python
def parse_evaluator_yaml(yml_file: Path) -> EvaluatorConfig:
    # 1. UTF-8 encoding enforcement
    # 2. Empty YAML detection
    # 3. Required field validation (6 fields)
    # 4. Type validation (all required fields must be strings)
    # 5. Name format validation (CLI-safe)
    # 6. Alias normalization and validation
    # 7. Empty prompt detection
    # 8. Unknown field warnings
```

**Review questions**:
- Are all 6 required fields validated: `name`, `description`, `model`, `api_key_env`, `prompt`, `output_suffix`?
- Does type validation catch YAML quirks (`yes` → bool, `123` → int)?
- Is the name regex correct: `^[a-zA-Z][a-zA-Z0-9_-]*$`?
- Are non-string aliases properly rejected?
- Is logging using lazy `%`-style formatting (not f-strings)?

### 2. discover_local_evaluators Function (HIGH)

**File**: `adversarial_workflow/evaluators/discovery.py:136-190`

Verify discovery logic:

```python
def discover_local_evaluators(base_path: Path | None = None) -> dict[str, EvaluatorConfig]:
    # 1. Default to cwd if base_path is None
    # 2. Return empty dict if no .adversarial/evaluators/ directory
    # 3. Glob *.yml files in sorted order
    # 4. Parse each file, skip invalid with warning
    # 5. Handle name conflicts (first wins)
    # 6. Register aliases pointing to same config object
```

**Review questions**:
- Does it return `{}` when directory doesn't exist (not raise)?
- Are files processed in sorted order for determinism?
- Do aliases point to the same config object (`config["alias"] is config["name"]`)?
- Is exception handling appropriate? (`EvaluatorParseError`, `yaml.YAMLError`, `OSError`)

### 3. EvaluatorParseError Exception (LOW)

**File**: `adversarial_workflow/evaluators/discovery.py:22-23`

```python
class EvaluatorParseError(Exception):
    """Raised when evaluator YAML is invalid."""
```

**Review questions**:
- Is the exception properly exported in `__init__.py`?
- Is the docstring sufficient?

### 4. Module Exports (MEDIUM)

**File**: `adversarial_workflow/evaluators/__init__.py`

Verify public API:

```python
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

### 5. Test Coverage (HIGH)

**File**: `tests/test_evaluator_discovery.py`

Verify 29 test cases cover:

| Category | Tests |
|----------|-------|
| Valid YAML parsing | 2 (basic + all fields) |
| Required field validation | 1 |
| Name format validation | 2 (number prefix, special chars) |
| Alias validation | 4 (invalid format, non-string int, non-string bool, format) |
| Prompt validation | 2 (empty, whitespace) |
| Type validation | 2 (bool field, int field) |
| Encoding/empty | 4 (encoding, empty, whitespace-only, invalid) |
| Alias normalization | 3 (string→list, list, none) |
| Unknown fields | 1 |
| Discovery | 10 (no dir, empty, single, multiple, aliases, invalid skip, conflicts, cwd default, non-yml ignored) |

**Review questions**:
- Are edge cases for YAML type coercion tested (`yes` → bool, `123` → int)?
- Is alias conflict handling tested?
- Is the "first file wins" conflict resolution tested?

## PR Review Findings (Already Addressed)

### Round 1 Findings (Fixed in `7a1c57c` ✅)

1. **Non-string aliases bypass validation** - Now explicitly checked
2. **Missing type validation for required fields** - Added string type enforcement
3. **Unnecessary `pass` in exception** - Removed
4. **F-string logging** - Converted to lazy `%`-style
5. **Broad `Exception` catch** - Narrowed to `OSError`

## Commands

```bash
# Checkout the branch
git fetch origin
git checkout feature/adv-0016-evaluator-discovery

# View all changes
git diff main...feature/adv-0016-evaluator-discovery

# Run tests
source .venv/bin/activate
pytest tests/test_evaluator_discovery.py -v

# Run all tests
pytest tests/ -v

# Verify imports work
python -c "
from adversarial_workflow.evaluators import (
    EvaluatorConfig,
    EvaluatorParseError,
    discover_local_evaluators,
    parse_evaluator_yaml,
)
print('All imports OK')
"

# Manual discovery test
mkdir -p .adversarial/evaluators
cat > .adversarial/evaluators/test.yml << 'EOF'
name: test
description: Test evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: TEST
EOF

python -c "
from adversarial_workflow.evaluators import discover_local_evaluators
result = discover_local_evaluators()
print(f'Found: {list(result.keys())}')
"
rm -f .adversarial/evaluators/test.yml

# Check PR status
gh pr view 8 --json state,reviews

# View in browser
gh pr view 8 --web
```

## Expected Outcome

- [ ] `parse_evaluator_yaml` validates all required fields and types
- [ ] `discover_local_evaluators` handles missing directory gracefully
- [ ] Aliases point to same config object (not copies)
- [ ] Name/alias conflicts logged and handled (first wins)
- [ ] All 29 tests pass
- [ ] No regressions in existing 78 tests (107 total)
- [ ] PR ready for approval
