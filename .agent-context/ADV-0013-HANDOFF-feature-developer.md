# ADV-0013 Handoff: Library CLI Core

**Task**: ADV-0013 - Evaluator Library CLI Core
**Agent**: feature-developer
**Created**: 2026-02-02
**Status**: Ready for implementation

---

## Context

This task implements CLI commands to browse, install, and update evaluator configurations from the community [adversarial-evaluator-library](https://github.com/movito/adversarial-evaluator-library).

**Design Philosophy**: "Copy, Don't Link" - evaluators are copied to projects, not referenced at runtime. Projects remain self-contained.

---

## Technical Details

### Library Repository (Verified)

- **URL**: https://github.com/movito/adversarial-evaluator-library
- **Index Location**: `evaluators/index.json` (NOT at root)
- **Current Version**: 1.2.0
- **Evaluators**: 18 across 4 providers (google, openai, anthropic, mistral)
- **Categories**: 6 (quick-check, deep-reasoning, adversarial, knowledge-synthesis, cognitive-diversity, code-review)

### Actual index.json Schema

```json
{
  "version": "1.2.0",
  "evaluators": [
    {
      "name": "gemini-flash",
      "provider": "google",
      "path": "evaluators/google/gemini-flash",
      "model": "gemini/gemini-2.5-flash",
      "category": "quick-check",
      "description": "Fast evaluation using Gemini 2.5 Flash"
    }
  ],
  "categories": {
    "quick-check": "Fast, cost-effective reviews",
    ...
  }
}
```

**Note**: Uses `category` (singular string), not `categories` (array).

### Evaluator YAML Structure

```yaml
name: gemini-flash
description: Fast evaluation using Gemini 2.5 Flash
model: gemini/gemini-2.5-flash
api_key_env: GEMINI_API_KEY
output_suffix: -gemini-flash.md
timeout: 180
prompt: |
  You are a document evaluator...
```

### Raw URLs for Fetching

```python
# Index
INDEX_URL = "https://raw.githubusercontent.com/movito/adversarial-evaluator-library/main/evaluators/index.json"

# Evaluator config
EVALUATOR_URL = "https://raw.githubusercontent.com/movito/adversarial-evaluator-library/main/evaluators/{provider}/{name}/evaluator.yml"
```

---

## Implementation Approach

### Recommended File Structure

```
adversarial_workflow/
├── cli.py                    # Add: @cli.group() def library(): ...
├── library/                  # NEW MODULE
│   ├── __init__.py          # Exports
│   ├── client.py            # LibraryClient class - HTTP, caching
│   ├── commands.py          # Click commands: list, install, check-updates, update
│   ├── models.py            # Pydantic/dataclass models: IndexData, EvaluatorEntry
│   └── cache.py             # Cache management (TTL, invalidation)
```

### Key Classes

```python
# library/client.py
class LibraryClient:
    def __init__(self, base_url: str = DEFAULT_LIBRARY_URL, cache_dir: Path = DEFAULT_CACHE_DIR):
        ...

    async def fetch_index(self, no_cache: bool = False) -> IndexData:
        """Fetch index.json with caching."""
        ...

    async def fetch_evaluator(self, provider: str, name: str) -> dict:
        """Fetch evaluator.yml content."""
        ...

# library/models.py
@dataclass
class EvaluatorEntry:
    name: str
    provider: str
    path: str
    model: str
    category: str
    description: str

@dataclass
class IndexData:
    version: str
    evaluators: list[EvaluatorEntry]
    categories: dict[str, str]
```

### Provenance Metadata

When installing, prepend this to the YAML AND add `model_requirement` field:

```yaml
# Installed from adversarial-evaluator-library
# Source: {provider}/{name}
# Version: {index_version}
# Installed: {timestamp}
#
# To check for updates: adversarial library check-updates
# To update: adversarial library update {name}
#
# Feel free to edit this file - it's yours now!

_meta:
  source: adversarial-evaluator-library
  source_path: {provider}/{name}
  version: "{index_version}"
  installed: "{timestamp}"

name: {name}
description: {description}

# Legacy fields (Phase 1 backwards compatibility)
model: {model}
api_key_env: {api_key_env}

# Phase 2 ready (model routing layer - ADR-0004)
model_requirement:
  family: {family}      # Extract from model string or index
  tier: {tier}          # Extract from model string or index
  min_version: "{version}"

{rest_of_original_yaml}
```

**IMPORTANT (ADR-0004)**: Include BOTH `model`+`api_key_env` AND `model_requirement` for forwards/backwards compatibility. See `docs/decisions/adr/library-refs/ADR-0004-evaluator-definition-model-routing-separation.md`.

---

## Starting Points

### 1. Create the library module

```bash
mkdir -p adversarial_workflow/library
touch adversarial_workflow/library/__init__.py
```

### 2. Add library command group to cli.py

Look at existing command groups in `cli.py` for patterns. Add near the end:

```python
@cli.group()
def library():
    """Browse and install evaluators from the community library."""
    pass

# Import commands to register them
from adversarial_workflow.library import commands  # noqa
```

### 3. Existing dependencies available

- `aiohttp` - Already in pyproject.toml for HTTP requests
- `pyyaml` - Already available for YAML parsing
- Click - Already used for CLI

---

## Testing Approach

### Unit Tests (Mock HTTP)

```python
# tests/test_library_client.py
@pytest.fixture
def mock_index_response():
    return {
        "version": "1.2.0",
        "evaluators": [...],
        "categories": {...}
    }

async def test_fetch_index_caches_result(mock_aiohttp, mock_index_response):
    client = LibraryClient()
    # First call fetches
    result1 = await client.fetch_index()
    # Second call uses cache
    result2 = await client.fetch_index()
    assert mock_aiohttp.get.call_count == 1
```

### Integration Tests (Real Network)

Mark with `@pytest.mark.network` and skip in CI:

```python
@pytest.mark.network
async def test_fetch_real_index():
    client = LibraryClient()
    index = await client.fetch_index(no_cache=True)
    assert index.version
    assert len(index.evaluators) > 0
```

---

## Acceptance Criteria Checklist

From the task spec - implement in this order:

1. [ ] `adversarial library list` - basic listing
2. [ ] `adversarial library list --provider <name>` - filter by provider
3. [ ] `adversarial library list --category <name>` - filter by category
4. [ ] `adversarial library list --verbose` - detailed output
5. [ ] `adversarial library install <provider>/<name>` - basic install
6. [ ] Provenance `_meta` block in installed files
7. [ ] `adversarial library check-updates` - compare versions
8. [ ] `adversarial library update <name>` - with diff preview
9. [ ] `adversarial library update --all` - update all outdated
10. [ ] `adversarial library update --yes` - skip confirmation
11. [ ] `adversarial library update --diff-only` - preview only
12. [ ] Index caching with 1-hour TTL
13. [ ] Graceful offline handling
14. [ ] Unit tests
15. [ ] Integration tests

---

## Evaluation History

- **Round 1**: NEEDS_REVISION - Missing error handling details
- **Round 2**: NEEDS_REVISION - Requested more implementation specifics
- **Coordinator Decision**: APPROVED - Remaining concerns are implementation-level details

---

## Resources

- **Task Spec**: `delegation/tasks/2-todo/ADV-0013-library-cli-core.md`
- **Original Proposal**: `docs/proposals/AWF-evaluator-library-cli-integration.md`
- **Library Repo**: https://github.com/movito/adversarial-evaluator-library
- **Existing CLI**: `adversarial_workflow/cli.py`
- **Existing Evaluators Module**: `adversarial_workflow/evaluators/`
