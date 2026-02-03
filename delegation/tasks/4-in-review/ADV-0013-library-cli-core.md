# ADV-0013: Evaluator Library CLI Core

**Status**: In Review
**Priority**: Medium
**Estimated Effort**: 2-3 days
**Source**: Proposal from gas-taxes project (AWF-evaluator-library-cli-integration.md)

---

## Summary

Implement core CLI commands for browsing, installing, and updating evaluator configurations from the community [adversarial-evaluator-library](https://github.com/movito/adversarial-evaluator-library). This enables evaluator sharing across projects while maintaining full local ownership of configurations.

---

## Background

### Problem Statement

Users must currently write evaluator YAML configurations from scratch, which creates:
1. High barrier to entry for new users
2. Duplicated effort across projects developing similar evaluators
3. No knowledge sharing of effective prompts and configurations
4. Discovery problem - users don't know what evaluator patterns exist

### Solution

Add a `library` subcommand group to the CLI that fetches evaluator configs from a community library. Following the "Copy, Don't Link" philosophy:
- Evaluators are **copied** to projects, not referenced at runtime
- Projects remain self-contained and work offline
- Users can customize their local copies freely
- Updates are explicit and user-controlled

### Architecture Context

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Project Configs                                   │
│  .adversarial/evaluators/*.yml                              │
│  Fully owned by project. Mix of custom + library-sourced.   │
└─────────────────────────────────────────────────────────────┘
                           ▲ copy (one-time)
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: CLI Helper ◀── THIS TASK                          │
│  adversarial library list|install|update                    │
│  Convenience layer. Not required. Manual copy works too.    │
└─────────────────────────────────────────────────────────────┘
                           ▲ fetches from
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Evaluator Library (separate repo)                 │
│  github.com/movito/adversarial-evaluator-library            │
│  Versioned, community-contributed, provider-organized.      │
└─────────────────────────────────────────────────────────────┘
```

---

## Requirements

### 1. `adversarial library list`

**Purpose**: Browse available evaluators from the library.

**Usage**:
```bash
# List all evaluators
adversarial library list

# Filter by provider
adversarial library list --provider google

# Filter by category
adversarial library list --category quick-check

# Show detailed info
adversarial library list --verbose
```

**Output Format** (default):
```
Available evaluators from adversarial-evaluator-library (v1.0.0):

PROVIDER   NAME              CATEGORY           DESCRIPTION
google     gemini-flash      quick-check        Fast initial validation
google     gemini-pro        knowledge-synthesis Large-context analysis
openai     fast-check        quick-check        GPT-4o-mini quick review
...

9 evaluators available. Use 'adversarial library install <provider>/<name>' to install.
```

**Behavior**:
- Fetches `index.json` from library repo (with caching)
- Graceful failure if network unavailable (show cached data or helpful error)
- No authentication required (public repo)

---

### 2. `adversarial library install`

**Purpose**: Copy an evaluator configuration from library to project.

**Usage**:
```bash
# Install latest version
adversarial library install google/gemini-flash

# Install specific version
adversarial library install google/gemini-flash@1.0.0

# Install multiple
adversarial library install google/gemini-flash openai/fast-check

# Force overwrite existing
adversarial library install google/gemini-flash --force
```

**Behavior**:
1. Fetch `evaluator.yml` from library repo
2. Add provenance metadata (see format below)
3. Write to `.adversarial/evaluators/<name>.yml`
4. Validate the config against schema
5. Report success with usage hint

**Provenance Metadata Format**:
```yaml
# Installed from adversarial-evaluator-library
# Source: google/gemini-flash
# Version: 1.0.0
# Installed: 2026-02-02T15:30:00Z
#
# To check for updates: adversarial library check-updates
# To update: adversarial library update google/gemini-flash
#
# Feel free to edit this file - it's yours now!

_meta:
  source: adversarial-evaluator-library
  source_path: google/gemini-flash
  version: "1.0.0"
  installed: "2026-02-02T15:30:00Z"

name: gemini-flash
description: Fast evaluation using Gemini 2.5 Flash

# Legacy fields (Phase 1 backwards compatibility)
model: gemini/gemini-2.5-flash
api_key_env: GEMINI_API_KEY

# Phase 2 ready (model routing layer - ADR-0004)
model_requirement:
  family: gemini
  tier: flash
  min_version: "2.5"

timeout: 180
output_suffix: -gemini-flash.md
prompt: |
  ...
```

**IMPORTANT (ADR-0004 Alignment)**: Installed evaluators MUST include both:
- `model` + `api_key_env` - For current workflow compatibility
- `model_requirement` - For Phase 2 resolution engine (ADV-0015)

This enables gradual migration without breaking existing installations.

**Conflict Handling**:
- If file exists and `--force` not specified: error with helpful message
- Never silently overwrite

---

### 3. `adversarial library check-updates`

**Purpose**: Check if installed library evaluators have newer versions available.

**Usage**:
```bash
# Check all installed evaluators
adversarial library check-updates

# Check specific evaluator
adversarial library check-updates gemini-flash
```

**Behavior**:
1. Scan `.adversarial/evaluators/` for files with `_meta.source` field
2. Compare `_meta.version` against library's `index.json`
3. Report available updates

**Output**:
```
Checking for evaluator updates...

EVALUATOR        INSTALLED   AVAILABLE   STATUS
gemini-flash     1.0.0       1.2.0       Update available
fast-check       1.1.0       1.1.0       Up to date
my-custom        -           -           Local only

1 update available. Run 'adversarial library update <name>' to update.
```

---

### 4. `adversarial library update`

**Purpose**: Update an installed evaluator to a newer library version.

**Usage**:
```bash
# Update specific evaluator (interactive diff review)
adversarial library update gemini-flash

# Update all outdated evaluators
adversarial library update --all

# Skip diff review (auto-accept)
adversarial library update gemini-flash --yes

# Show diff only, don't apply
adversarial library update gemini-flash --diff-only
```

**Behavior**:
1. Fetch new version from library
2. **Show diff** between current and new version
3. **Prompt for confirmation** (unless `--yes`)
4. Apply update, updating `_meta.version` and `_meta.installed`

**Local Modification Warning**:
If user has modified the file since installation, warn:
```
⚠️  Warning: Your local gemini-flash.yml has been modified since installation.
   Local changes will be overwritten by this update.

   Proceed anyway? [y/N]:
```

---

### 5. Index Caching & Offline Handling

**Caching**:
- Cache `index.json` to `~/.cache/adversarial-workflow/library-index.json`
- Default TTL: 1 hour (3600 seconds)
- Support `--no-cache` flag for debugging
- User-configurable TTL deferred to ADV-0014 (config file options)

**Offline Mode**:
- If network unavailable and cache exists: use cache with warning
- If network unavailable and no cache: error with helpful message

**GitHub Raw URLs**:
```python
# index.json (NOTE: inside evaluators/ directory)
f"https://raw.githubusercontent.com/movito/adversarial-evaluator-library/main/evaluators/index.json"

# evaluator.yml
f"https://raw.githubusercontent.com/movito/adversarial-evaluator-library/main/evaluators/{provider}/{name}/evaluator.yml"
```

**Actual index.json Schema** (verified 2026-02-02):
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
    "deep-reasoning": "Extended analysis for complexity",
    "adversarial": "Stress-testing and critical examination",
    "knowledge-synthesis": "Large-context cross-referencing",
    "cognitive-diversity": "Alternative model perspectives",
    "code-review": "Code and configuration analysis"
  }
}
```

**Note**: Actual schema uses `category` (singular string) not `categories` (array). No per-evaluator version field. 18 evaluators across 4 providers currently available.

---

## Technical Implementation

### Dependencies

- `aiohttp` - Already available (existing dependency)
- `pyyaml` - Already available (existing dependency)

### File Structure

```
adversarial_workflow/
├── cli.py                    # Add library command group
├── library/                  # NEW: Library functionality
│   ├── __init__.py
│   ├── client.py            # HTTP client, caching
│   ├── commands.py          # CLI command implementations
│   └── models.py            # Data models for index, evaluators
```

### Schema Validation

- `_meta` field must be ignored by evaluator loader (verify existing behavior)
- Validate fetched configs against existing evaluator schema before writing

### Error Handling

**Network Errors**:
- Network timeout: 10 seconds (configurable in ADV-0014)
- Single retry with exponential backoff on transient failures
- Clear error messages with suggested remediation

**Partial Downloads / Corrupted Files**:
- Validate JSON/YAML after download before processing
- If index.json is corrupt: fall back to cache with warning, or clear error if no cache
- If evaluator.yml is corrupt: abort install with clear error, do not write partial file
- Use temp file during download, only move to final location after validation

**Schema Validation Failures**:
- Validate fetched evaluator configs against existing schema before writing
- If schema validation fails:
  - Display specific validation error (which field, what's wrong)
  - Suggest: "This evaluator may be incompatible with your adversarial-workflow version"
  - Option: `--skip-validation` flag for advanced users (with warning)
  - Never write invalid config to project

**Library Structure Changes**:
- Check `version` field in index.json for compatibility
- If version > supported: warn user to upgrade adversarial-workflow
- If required fields missing from index.json: graceful degradation (show what's available)
- If evaluator path not found: clear error "Evaluator not found at expected path"

---

## Acceptance Criteria

### Must Have

- [ ] `adversarial library list` shows available evaluators
- [ ] `adversarial library list --provider <name>` filters by provider
- [ ] `adversarial library list --category <name>` filters by category
- [ ] `adversarial library list --verbose` shows detailed info
- [ ] `adversarial library install <provider>/<name>` copies evaluator to project
- [ ] Installed evaluators include `_meta` provenance block with source, version, timestamp
- [ ] `adversarial library check-updates` identifies outdated evaluators
- [ ] `adversarial library update <name>` shows diff and prompts before applying
- [ ] `adversarial library update --all` updates all outdated evaluators
- [ ] `adversarial library update --yes` skips confirmation
- [ ] `adversarial library update --diff-only` shows diff without applying
- [ ] Index caching with 1-hour TTL
- [ ] Graceful offline handling (use cache if available)
- [ ] Works with the official `adversarial-evaluator-library` repo
- [ ] Unit tests for all core functionality
- [ ] Integration tests for GitHub fetch

### Must NOT Have

- [ ] Runtime dependency on library (copy-only model)
- [ ] Breaking changes to existing CLI commands
- [ ] Silent overwrites of existing files

---

## Testing Strategy

### Unit Tests

```python
# tests/test_library_client.py
- test_parse_index_json()
- test_parse_index_json_malformed()
- test_cache_read_write()
- test_cache_expiry()
- test_provenance_metadata_format()
- test_version_comparison()
- test_diff_generation()

# tests/test_library_commands.py
- test_list_all_evaluators()
- test_list_filter_by_provider()
- test_list_filter_by_category()
- test_install_new_evaluator()
- test_install_existing_no_force()
- test_install_existing_with_force()
- test_check_updates_with_outdated()
- test_check_updates_all_current()
- test_update_applies_changes()
```

### Integration Tests

```python
# tests/test_library_integration.py
- test_fetch_real_index()  # Requires network, mark appropriately
- test_install_real_evaluator()
- test_offline_mode_with_cache()
- test_corrupted_index_fallback_to_cache()
- test_schema_validation_failure_aborts()
```

### Offline / Limited Network Testing

Tests should use mocking to simulate network conditions:

```python
# tests/test_library_offline.py
@pytest.fixture
def mock_network_failure():
    """Mock aiohttp to simulate network failure."""
    with patch('aiohttp.ClientSession.get') as mock:
        mock.side_effect = aiohttp.ClientError("Network unreachable")
        yield mock

def test_list_uses_cache_when_offline(mock_network_failure, cached_index):
    """With network down and cache available, list shows cached data with warning."""
    result = runner.invoke(cli, ['library', 'list'])
    assert result.exit_code == 0
    assert "Using cached data" in result.output
    assert "gemini-flash" in result.output  # From cache

def test_install_fails_gracefully_when_offline(mock_network_failure):
    """With network down and no cache, install gives clear error."""
    result = runner.invoke(cli, ['library', 'install', 'google/gemini-flash'])
    assert result.exit_code == 1
    assert "Network unavailable" in result.output
    assert "check your connection" in result.output.lower()
```

### Manual Testing Checklist

```bash
# Fresh project
adversarial library list
adversarial library install google/gemini-flash
ls .adversarial/evaluators/  # Verify file created
cat .adversarial/evaluators/gemini-flash.yml  # Verify _meta block

# Update flow
adversarial library check-updates
adversarial library update gemini-flash --diff-only

# Offline mode (disconnect network)
adversarial library list  # Should show cached
```

---

## Dependencies

- **External**: `adversarial-evaluator-library` repo must exist with expected structure
- **Internal**: None (uses existing dependencies)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Library repo unavailable | Medium | Robust caching, clear error messages |
| Library schema changes | Medium | Version field in index.json for compatibility checks |
| Large index.json | Low | Cache locally, lazy fetch evaluator details |

---

## Documentation Updates

As part of this task, update the following documentation:

1. **README.md**: Add "Library Integration" section with:
   - Overview of the evaluator library concept
   - Quick start: `adversarial library list` and `adversarial library install`
   - Link to full documentation

2. **CLI Help**: Ensure all commands have complete `--help` output with examples

3. **Existing evaluator docs**: Add note that library evaluators are an alternative to manual creation

---

## Related Documents

- **Proposal**: `docs/proposals/AWF-evaluator-library-cli-integration.md`
- **Library Repo**: https://github.com/movito/adversarial-evaluator-library
- **Architecture**: `docs/decisions/adr/library-refs/ADR-0004-evaluator-definition-model-routing-separation.md`
- **Follow-up Tasks**:
  - ADV-0014 (Library CLI Enhancements)
  - ADV-0015 (Model Routing Layer - Phase 1)
