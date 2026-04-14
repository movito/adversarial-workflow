# ADV-0053: Migrate from Black+flake8 to Ruff

**Status**: Done
**Priority**: High
**Type**: Infrastructure
**Estimated Effort**: 1.5 hours
**Created**: 2026-03-09
**Blocks**: ADV-0052 (scripts core restructure needs clean CI)

## Summary

Replace Black + isort + flake8 with Ruff as the unified formatter and
linter. This aligns adversarial-workflow with dispatch-kit and
agentive-starter-kit, and is a prerequisite for ADV-0052's `ci-check.sh`
to pass cleanly.

## Current State

- **Formatter**: Black 23.12.1
- **Import sorting**: isort 5.13.2
- **Linter**: flake8 7.1.1
- **Line-length conflict**: `pyproject.toml` says 100, `.pre-commit-config.yaml` says 88
- **Missing hook**: `pattern_lint.py` not in `.pre-commit-config.yaml`
- **No CI linting**: GitHub Actions runs zero code quality checks

Full analysis: `.agent-context/research/LINTING-MODERNIZATION-PLAN.md`

## Target State

- **Formatter + Linter**: Ruff >=0.14.7 (all-in-one)
- **Line-length**: 100 (consistent everywhere)
- **Pattern lint**: In pre-commit config, pointing to `scripts/core/pattern_lint.py`
- **DK002 violations**: Fixed (add `encoding="utf-8"`)

## Scope

### 1. Update `pyproject.toml`

```toml
# Remove these sections:
# [tool.black]
# [tool.isort]

# Add:
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
external = ["DK001", "DK002", "DK003", "DK004"]
select = ["E", "F", "W", "I", "N", "B", "SIM", "ARG", "UP", "S", "RUF"]
ignore = ["E203", "S101"]

# Update dev dependencies:
# Remove: black, isort, flake8
# Add: ruff>=0.14.7
```

### 2. Update `.pre-commit-config.yaml`

- Remove Black, isort, flake8 hooks
- Add `ruff-pre-commit` hooks (ruff + ruff-format)
- Add `pattern-lint` local hook → `scripts/core/pattern_lint.py`
- Note: `pattern_lint.py` doesn't exist on main yet (arrives with ADV-0052).
  Use `scripts/pattern_lint.py` if it exists, otherwise skip this hook
  addition and let ADV-0052 add it

### 3. Auto-format all Python files

```bash
ruff format .
ruff check --fix .
```

### 4. Fix DK002 violations

Add `encoding="utf-8"` to all `.write_text()`, `.read_text()`, and
`open()` calls flagged by `pattern_lint.py`. These are mechanical fixes
across `tests/` and `adversarial_workflow/`.

Note: `pattern_lint.py` may not exist on main yet. If so, skip this step
— ADV-0052 will bring it in and DK002 fixes can be done then or in a
follow-up.

### 5. Update `scripts/ci-check.sh`

Replace Black/isort/flake8 steps with Ruff equivalents:

```bash
# Step 1: ruff format --check .
# Step 2: ruff check .
# Step 3: pattern_lint.py (keep as-is)
# Step 4: pytest (keep as-is)
```

Note: `ci-check.sh` on main is the old flat version. Update it here, and
ADV-0052 will copy the core version on top. Alternatively, just update
`pyproject.toml` and `.pre-commit-config.yaml` here, and let ADV-0052's
`ci-check.sh` handle the rest.

### 6. Verify

- `ruff format --check .` passes
- `ruff check .` passes
- `pytest tests/ -v` passes
- `pre-commit run --all-files` passes

## Acceptance Criteria

- [ ] No Black, isort, or flake8 in `pyproject.toml` dev dependencies
- [ ] `[tool.ruff]` configured in `pyproject.toml`
- [ ] `.pre-commit-config.yaml` uses ruff-pre-commit hooks
- [ ] Line-length is consistently 100 everywhere
- [ ] `ruff format --check .` passes
- [ ] `ruff check .` passes
- [ ] All tests pass
- [ ] Pre-commit hooks pass

## Notes

- This is a prerequisite for ADV-0052 (scripts restructure)
- Ruff migration is mechanical and low-risk — mostly auto-fixable
- dispatch-kit reference: `~/Github/dispatch-kit/pyproject.toml`
- Research: `.agent-context/research/LINTING-MODERNIZATION-PLAN.md`
