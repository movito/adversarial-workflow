# ADV-0034: CLI Library Commands Test Coverage

**Status**: Todo
**Priority**: Medium
**Created**: 2026-02-07
**Type**: Testing
**Estimated Effort**: 4-6 hours
**Depends On**: ADV-0033

---

## Problem Statement

The CLI library commands (`adversarial library *`) lack comprehensive test coverage. These commands are critical for the evaluator library integration feature.

## Scope

**Library Commands** (this task):
- `library install` - Install evaluators from library
- `library list` - List available evaluators
- `library list-installed` - List installed evaluators
- `library update` - Update installed evaluators
- `library search` - Search evaluators
- `library info` - Get evaluator details

**Out of scope**:
- Core CLI commands (ADV-0033)
- Agent commands (future task)

## Current State

```
adversarial_workflow/cli.py           1693   1062    37%
adversarial_workflow/library/commands.py  513    171    67%
```

**Target**:
- cli.py library section: 60%+ coverage
- library/commands.py: 80%+ coverage

## Acceptance Criteria

- [ ] `library install` has tests for:
  - [ ] Install single evaluator
  - [ ] Install multiple evaluators
  - [ ] Install by category
  - [ ] Already installed handling
  - [ ] Network error handling
- [ ] `library list` has tests for:
  - [ ] List all evaluators
  - [ ] Filter by category
  - [ ] Filter by provider
  - [ ] `--verbose` flag
- [ ] `library list-installed` has tests for:
  - [ ] Empty state (none installed)
  - [ ] With installed evaluators
  - [ ] Provenance display
- [ ] `library update` has tests for:
  - [ ] Update available
  - [ ] Already up-to-date
  - [ ] Update specific evaluator
- [ ] `library search` has tests for:
  - [ ] Search by name
  - [ ] Search by keyword
  - [ ] No results handling
- [ ] `library info` has tests for:
  - [ ] Valid evaluator
  - [ ] Unknown evaluator
- [ ] library/commands.py coverage reaches 80%+

## Implementation Notes

### Test Structure

```python
# tests/test_cli_library.py

class TestLibraryInstall:
    def test_install_single_evaluator(self, cli_runner, mock_library_client):
        ...
    def test_install_already_installed(self, ...):
        ...

class TestLibraryList:
    def test_list_all(self, ...):
        ...
    def test_list_by_category(self, ...):
        ...

class TestLibraryUpdate:
    ...
```

### Mocking Strategy

```python
@pytest.fixture
def mock_library_client(mocker):
    """Mock the library client for offline testing."""
    client = mocker.patch('adversarial_workflow.library.client.LibraryClient')
    client.return_value.list_evaluators.return_value = [...]
    return client
```

### Key Areas

| Lines | Function | Priority |
|-------|----------|----------|
| 596-790 | `library install` | High |
| 816-867 | `library list` | High |
| 884-957 | `library list-installed` | Medium |
| 966-1006 | `library update` | Medium |
| 1019-1039 | `library search` | Low |
| 1093-1114 | `library info` | Low |

## Related

- ADV-0033: CLI Core Commands Test Coverage (Phase 1)
- ADV-0036: Library Module Test Coverage

---

**Notes**: Use mocked library client to avoid network dependencies. Focus on CLI behavior, not library internals.
