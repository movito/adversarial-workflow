# Linting Modernization Plan: Black+flake8 → Ruff

**Date**: 2026-03-09
**Context**: Discovered during ADV-0052 (scripts core restructure)
**Status**: Planning

## Problem Statement

ADV-0052 copied core scripts from agentive-starter-kit v0.4.0, which uses
Ruff as its formatter/linter. adversarial-workflow still uses
Black + isort + flake8. This causes:

1. `ci-check.sh` fails Black formatting on `pattern_lint.py` (Ruff-formatted upstream)
2. `pattern_lint.py` DK002 rule flags ~100 existing `.write_text()` / `open()` calls
3. Pre-commit config is missing the `pattern_lint` hook entirely

## Current State (adversarial-workflow)

### Toolchain
| Tool | Version | Purpose |
|------|---------|---------|
| Black | 23.12.1 | Formatter |
| isort | 5.13.2 | Import sorting |
| flake8 | 7.1.1 | Linter |

### Configuration Bugs Found

1. **Line-length mismatch**:
   - `pyproject.toml [tool.black]`: `line-length = 100`
   - `.pre-commit-config.yaml` Black args: `--line-length=88`
   - `.pre-commit-config.yaml` isort args: `--line-length=88`
   - Result: pre-commit and `ci-check.sh` disagree on formatting

2. **Missing pre-commit hook**: `pattern_lint.py` is not in
   `.pre-commit-config.yaml` — DK rules never run on commit

3. **No CI linting**: `.github/workflows/test-package.yml` does not run
   any formatting or linting checks

## Target State (matching dispatch-kit + ASK)

### Toolchain
| Tool | Version | Purpose |
|------|---------|---------|
| Ruff | >=0.14.7 | Formatter + Linter + Import sorting (all-in-one) |

### Configuration (from dispatch-kit)
```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
external = ["DK001", "DK002", "DK003"]
select = ["E", "F", "W", "I", "N", "B", "SIM", "ARG", "UP", "S", "RUF"]
ignore = ["E203", "S101"]
```

### Pre-commit (from dispatch-kit)
```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.14.7
  hooks:
    - id: ruff
      name: Lint with Ruff
      args: [--fix]
    - id: ruff-format
      name: Format with Ruff

- repo: local
  hooks:
    - id: pattern-lint
      name: Check for common code patterns (DK rules)
      entry: python3 scripts/core/pattern_lint.py
      language: system
      types: [python]
      stages: [pre-commit]
```

## Migration Plan

### Phase 1: Switch formatter + linter to Ruff

**Files to modify:**

1. **`pyproject.toml`**
   - Remove `[tool.black]` and `[tool.isort]` sections
   - Add `[tool.ruff]` and `[tool.ruff.lint]` sections
   - Replace dev dependencies: `black`, `isort`, `flake8` → `ruff>=0.14.7`

2. **`.pre-commit-config.yaml`**
   - Remove Black, isort, flake8 hooks
   - Add `ruff-pre-commit` hooks (ruff + ruff-format)
   - Add `pattern-lint` local hook pointing to `scripts/core/pattern_lint.py`

3. **`scripts/core/ci-check.sh`**
   - Replace Black check with `ruff format --check .`
   - Replace isort check with (removed, built into ruff)
   - Replace flake8 check with `ruff check .`
   - Keep pattern_lint step as-is

### Phase 2: Auto-fix existing code

4. **Run `ruff format .`** to reformat all Python files
   - This will touch most `.py` files — expect a large diff
   - Ruff format is Black-compatible but not identical

5. **Run `ruff check --fix .`** to auto-fix lint issues

6. **Fix DK002 violations** — add `encoding="utf-8"` to all flagged calls
   - `ruff` can't auto-fix these (custom rule), but they're mechanical
   - ~100 violations across `tests/` and `adversarial_workflow/`

### Phase 3: Verify

7. `ruff format --check .` passes
8. `ruff check .` passes
9. `./scripts/core/ci-check.sh` passes
10. `pytest tests/ -v` passes
11. `pre-commit run --all-files` passes

## Scope & Branching Decision

### Option A: Separate branch (recommended)

- Create `chore/ADV-XXXX-ruff-migration` from `main`
- ADV-0052 gets a minimal quick-fix (run `black` on `pattern_lint.py`)
- ADV-0052 merges first, then Ruff migration follows
- **Pro**: Clean separation, smaller PRs, easier review
- **Con**: Two PRs, temporary inconsistency

### Option B: Extend ADV-0052

- Do it all on `feature/ADV-0052-scripts-core-restructure`
- **Pro**: One PR, consistent from the start
- **Con**: Scope creep (scripts restructure + linting modernization),
  very large diff, harder to review

### Option C: Ruff migration first, then ADV-0052

- Create Ruff migration branch from `main`, merge first
- Then rebase ADV-0052 on top
- **Pro**: ADV-0052 lands cleanly with no formatting issues
- **Con**: Blocks ADV-0052 on a separate task

### Recommendation: Option C

The Ruff migration is a prerequisite for clean CI on ADV-0052. If we do
it first:
- ADV-0052's `ci-check.sh` will pass without workarounds
- `pattern_lint.py` will already be correctly formatted
- DK002 violations will already be fixed
- No quick-fix hacks needed

The Ruff migration is mechanical and low-risk — mostly auto-fixable.

## Effort Estimate

- Ruff migration: ~1 hour (mostly auto-fix + verify)
- Includes DK002 fixes: ~30 minutes (mechanical `encoding="utf-8"` additions)
- Total: ~1.5 hours

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Ruff formats differently than Black | Certain | Low | One-time reformat, review diff |
| Ruff catches new lint errors | Medium | Low | Fix or configure ignores |
| Tests break due to formatting | Very Low | Low | Run full suite before merge |
| DK002 fixes break behavior | Very Low | Very Low | `encoding="utf-8"` is Python default on most platforms |
