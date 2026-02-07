# ADV-0036: Library Module Test Coverage

**Status**: Todo
**Priority**: Medium
**Created**: 2026-02-07
**Type**: Testing
**Estimated Effort**: 3-4 hours

---

## Problem Statement

The `library/` module has moderate test coverage that could be improved:
- `cache.py`: 71%
- `client.py`: 78%
- `commands.py`: 67%

These modules handle library integration and should have comprehensive testing.

## Current State

```
adversarial_workflow/library/cache.py      86     25    71%
adversarial_workflow/library/client.py     89     20    78%
adversarial_workflow/library/commands.py  513    171    67%
```

**Target**:
- cache.py: 85%+
- client.py: 85%+
- commands.py: 80%+

## Scope

### cache.py (71% → 85%)
- Cache initialization
- Cache read/write
- Cache invalidation
- TTL handling
- Error handling

### client.py (78% → 85%)
- API requests
- Response parsing
- Error handling
- Retry logic

### commands.py (67% → 80%)
- Install logic
- Update logic
- List/search logic
- Provenance tracking

## Acceptance Criteria

### cache.py
- [ ] Test cache miss scenarios
- [ ] Test cache expiration (TTL)
- [ ] Test cache corruption handling
- [ ] Test concurrent access (if applicable)
- [ ] Coverage reaches 85%+

### client.py
- [ ] Test successful API responses
- [ ] Test network errors (timeout, connection refused)
- [ ] Test malformed responses
- [ ] Test retry behavior
- [ ] Coverage reaches 85%+

### commands.py
- [ ] Test evaluator installation flow
- [ ] Test update detection logic
- [ ] Test provenance tracking
- [ ] Test error handling paths
- [ ] Coverage reaches 80%+

## Implementation Notes

### Test Structure

```python
# tests/test_library_cache.py
class TestLibraryCache:
    def test_cache_miss(self, tmp_path):
        ...
    def test_cache_expired(self, tmp_path, freezer):
        ...
    def test_cache_corruption(self, tmp_path):
        ...

# tests/test_library_client.py
class TestLibraryClient:
    def test_network_error(self, mock_requests):
        ...
    def test_malformed_response(self, mock_requests):
        ...

# tests/test_library_commands.py (extend existing)
class TestInstallLogic:
    def test_install_with_dependencies(self, ...):
        ...
```

### Mocking Strategy

```python
@pytest.fixture
def mock_requests(mocker):
    """Mock HTTP requests for offline testing."""
    return mocker.patch('requests.get')

@pytest.fixture
def freezer(mocker):
    """Freeze time for TTL testing."""
    return mocker.patch('time.time', return_value=1000000)
```

### Priority Lines to Cover

**cache.py:**
| Lines | Description | Priority |
|-------|-------------|----------|
| 39-41, 52, 56-57 | Cache miss handling | High |
| 80-81, 103-104 | TTL logic | Medium |
| 175-184 | Error handling | Medium |

**client.py:**
| Lines | Description | Priority |
|-------|-------------|----------|
| 109, 112-115 | Request errors | High |
| 140-142, 153-156 | Response parsing | Medium |
| 201-206, 215 | Edge cases | Low |

**commands.py:**
| Lines | Description | Priority |
|-------|-------------|----------|
| 593-666 | Install logic | High |
| 698-699, 718-725 | Update logic | Medium |
| 823-838, 844-847 | Error paths | Medium |

## Related

- ADV-0034: CLI Library Commands Test Coverage
- Existing tests: `tests/test_library_*.py`

---

**Notes**: Focus on error handling and edge cases. The happy paths are likely already covered.
