# ADV-0035: Evaluator Runner Test Coverage

**Status**: Todo
**Priority**: High
**Created**: 2026-02-07
**Type**: Testing
**Estimated Effort**: 3-4 hours

---

## Problem Statement

`evaluators/runner.py` has 64% test coverage. This module handles the core evaluation execution logic and should have comprehensive testing.

## Current State

```
adversarial_workflow/evaluators/runner.py   164     59    64%

Missing lines: 76-80, 84, 96-108, 185-186, 211-218, 231-262,
               298-301, 306-307, 320-325, 330, 335-340
```

**Target**: Increase runner.py coverage to 85%+

## Scope

- `run_evaluator()` function - main entry point
- `_check_file_size()` - output validation
- `_report_verdict()` - verdict reporting
- Aider subprocess handling
- Error handling paths
- Timeout handling

## Acceptance Criteria

- [ ] `run_evaluator()` has tests for:
  - [ ] Successful evaluation
  - [ ] Evaluator not found
  - [ ] API key missing
  - [ ] Aider failure (non-zero exit)
  - [ ] Timeout handling
- [ ] `_check_file_size()` has tests for:
  - [ ] Valid output file
  - [ ] Empty output file
  - [ ] Missing output file
- [ ] `_report_verdict()` has tests for:
  - [ ] All verdict types (APPROVED, NEEDS_REVISION, etc.)
- [ ] Error paths covered:
  - [ ] Lines 76-80: Aider not found
  - [ ] Lines 96-108: Subprocess errors
  - [ ] Lines 231-262: Output validation failures
  - [ ] Lines 320-340: Timeout/cleanup
- [ ] Overall runner.py coverage reaches 85%+

## Implementation Notes

### Test Structure

```python
# tests/test_evaluator_runner.py (extend existing)

class TestRunEvaluator:
    def test_aider_not_found(self, ...):
        """Test error when aider is not installed."""
        ...

    def test_api_key_missing(self, ...):
        """Test error when API key env var is missing."""
        ...

    def test_aider_timeout(self, ...):
        """Test timeout handling."""
        ...

class TestCheckFileSize:
    def test_empty_output(self, ...):
        ...

    def test_missing_output(self, ...):
        ...

class TestReportVerdict:
    @pytest.mark.parametrize("verdict", ["APPROVED", "NEEDS_REVISION", "REJECTED"])
    def test_verdict_types(self, verdict, ...):
        ...
```

### Mocking Strategy

```python
@pytest.fixture
def mock_aider(mocker):
    """Mock aider subprocess."""
    mock_run = mocker.patch('subprocess.run')
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    return mock_run

@pytest.fixture
def mock_which(mocker):
    """Mock shutil.which for aider detection."""
    return mocker.patch('shutil.which', return_value='/usr/bin/aider')
```

### Priority Lines to Cover

| Lines | Description | Priority |
|-------|-------------|----------|
| 76-80 | Aider not found error | High |
| 96-108 | Subprocess error handling | High |
| 231-262 | Output validation | Medium |
| 320-340 | Timeout/cleanup | Medium |
| 185-186, 211-218 | Edge cases | Low |

## Related

- ADV-0033: CLI Core Commands Test Coverage
- Existing tests: `tests/test_evaluator_runner.py`

---

**Notes**: Most of the uncovered lines are error handling paths. Focus on testing failure scenarios.
