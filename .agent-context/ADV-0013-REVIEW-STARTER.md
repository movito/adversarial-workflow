# ADV-0013 Review Starter: Library CLI Core

**Task**: ADV-0013 - Evaluator Library CLI Core
**Status**: Ready for Code Review (Bug Fixes Applied)
**Implementation Agent**: feature-developer
**Bug Fixes**: planner (CodeRabbit/BugBot triage)
**Branch**: `feat/adv-0013-library-cli-core` → `main`
**PR**: https://github.com/movito/adversarial-workflow/pull/20
**Date**: 2026-02-03

---

## Implementation Summary

This task implements CLI commands for browsing, installing, and updating evaluator configurations from the community [adversarial-evaluator-library](https://github.com/movito/adversarial-evaluator-library).

### Commands Implemented

1. `adversarial library list` - Browse available evaluators
   - `--provider` filter
   - `--category` filter
   - `--verbose` detailed output
   - `--no-cache` bypass cache

2. `adversarial library install <provider>/<name>` - Install evaluator
   - `--force` overwrite existing
   - Adds `_meta` provenance block

3. `adversarial library check-updates` - Check for updates

4. `adversarial library update <name>` - Update evaluator
   - `--all` update all outdated
   - `--yes` skip confirmation
   - `--diff-only` preview only

---

## Files Changed

### New Files

| File | Lines | Purpose |
|------|-------|---------|
| `adversarial_workflow/library/__init__.py` | ~40 | Module exports |
| `adversarial_workflow/library/models.py` | ~100 | Data models (EvaluatorEntry, IndexData, etc.) |
| `adversarial_workflow/library/cache.py` | ~140 | Cache management with TTL |
| `adversarial_workflow/library/client.py` | ~160 | HTTP client for fetching from GitHub |
| `adversarial_workflow/library/commands.py` | ~500 | Click CLI commands |
| `tests/test_library_client.py` | ~300 | Unit tests for client/models/cache |
| `tests/test_library_commands.py` | ~250 | Unit tests for CLI commands |
| `tests/test_library_integration.py` | ~100 | Integration tests with real network |

### Modified Files

| File | Changes |
|------|---------|
| `adversarial_workflow/cli.py` | Added `library` command group |
| `adversarial_workflow/__init__.py` | Version bump |
| `pyproject.toml` | Dependencies if any |
| `README.md` | Documentation updates if any |

---

## Test Results

```
307 passed in 7.51s
```

- 48 new tests for library module
- All existing tests pass (no regressions)
- Integration tests verified with live GitHub API

---

## Acceptance Criteria Status

### Must Have - All Complete

- [x] `adversarial library list` shows available evaluators
- [x] `adversarial library list --provider <name>` filters by provider
- [x] `adversarial library list --category <name>` filters by category
- [x] `adversarial library list --verbose` shows detailed info
- [x] `adversarial library install <provider>/<name>` copies evaluator to project
- [x] Installed evaluators include `_meta` provenance block
- [x] `adversarial library check-updates` identifies outdated evaluators
- [x] `adversarial library update <name>` shows diff and prompts before applying
- [x] `adversarial library update --all` updates all outdated evaluators
- [x] `adversarial library update --yes` skips confirmation
- [x] `adversarial library update --diff-only` shows diff without applying
- [x] Index caching with 1-hour TTL
- [x] Graceful offline handling (use cache if available)
- [x] Works with the official `adversarial-evaluator-library` repo
- [x] Unit tests for all core functionality
- [x] Integration tests for GitHub fetch

### Must NOT Have - Verified

- [x] No runtime dependency on library (copy-only model)
- [x] No breaking changes to existing CLI commands
- [x] No silent overwrites of existing files

---

## Automated Review Findings (Resolved)

CodeRabbit and BugBot identified issues that have been fixed in commit `5015207`:

| Issue | Severity | File | Resolution |
|-------|----------|------|------------|
| YAML `---` separator causes multi-document parsing | CRITICAL | `commands.py` | Strip separator before concatenation |
| Cross-provider file collisions (`fast-check.yml`) | CRITICAL | `commands.py` | Changed to `{provider}-{name}.yml` format |
| `ValueError` escapes exception handler | MAJOR | `commands.py` | Added to exception tuple |
| `HTTPError` handler unreachable (subclass of URLError) | MEDIUM | `client.py` | Reordered exception handlers |
| UTC timestamp mislabeled (naive datetime + "Z") | LOW | `commands.py` | Use `datetime.now(timezone.utc)` |
| Unused `is_online` method | MEDIUM | `client.py` | Removed |
| Unused test fixture parameters | MINOR | `test_*.py` | Fixed with underscore prefixes |

**Deferred**: Duplicated ANSI color codes (non-blocking, aesthetic only)

---

## Review Focus Areas

1. **Bug Fixes Verification**: Confirm the CodeRabbit/BugBot fixes are correct
2. **Error Handling**: Network failures, malformed responses, file I/O errors
3. **Cache Implementation**: TTL behavior, stale cache fallback
4. **Provenance Format**: `_meta` block structure per ADR-0004
5. **Test Coverage**: Edge cases, offline scenarios
6. **Code Style**: Consistency with existing codebase
7. **Security**: URL handling, file path sanitization

---

## Related Documents

- **Task Spec**: `delegation/tasks/4-in-review/ADV-0013-library-cli-core.md`
- **Handoff**: `.agent-context/ADV-0013-HANDOFF-feature-developer.md`
- **Architecture**: `docs/decisions/adr/library-refs/ADR-0004-evaluator-definition-model-routing-separation.md`
- **Interface Contract**: `docs/decisions/adr/library-refs/ADR-0005-library-workflow-interface-contract.md`

---

## How to Review

```bash
# Run tests
uv run pytest tests/test_library_*.py -v

# Try the commands
uv run adversarial library list
uv run adversarial library list --provider google --verbose
uv run adversarial library install google/gemini-flash
uv run adversarial library check-updates
```

---

**Ready for code-reviewer agent.**
