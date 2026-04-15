# ADV-0071 Handoff: Fix Version Management + Release 1.0.0

**Task**: `.kit/tasks/2-todo/ADV-0071-fix-version-management-release-1.0.0.md`
**Agent**: feature-developer-v5
**Created**: 2026-04-14

## Mission

Fix the hardcoded version fallback strings that cause `test_version_flag` to fail
in subprocess environments, then bump the project to 1.0.0.

## Critical Context

### The Problem

Both `adversarial_workflow/__init__.py` and `adversarial_workflow/cli.py` have:

```python
try:
    from importlib.metadata import version as _get_version
    __version__ = _get_version("adversarial-workflow")
except Exception:
    __version__ = "0.9.9"  # ← STALE (should be 0.9.10)
```

When `ci-check.sh` runs pytest, the `adversarial --version` subprocess may use a
different Python environment or stale editable install, causing the fallback to
trigger. The test then compares in-process metadata (`0.9.10`) against subprocess
output (`0.9.9`) → mismatch → FAIL.

### The Fix (Evaluator-Approved)

**Option A — Remove try/except entirely:**

```python
from importlib.metadata import version as _get_version
__version__ = _get_version("adversarial-workflow")
```

Python 3.10+ always has `importlib.metadata`. If the package isn't installed,
`PackageNotFoundError` propagates — which is correct for a pip-installed CLI tool.

**DRY requirement** (from evaluator): Define `__version__` ONLY in `__init__.py`.
In `cli.py`, import it: `from . import __version__`.

### The Tricky Part

Previous attempts to fix this on main failed because:

1. Even after removing the fallback, `ci-check.sh` subprocess still picked up
   a stale `adversarial` binary
2. The `run_cli` fixture in `tests/conftest.py` (line ~189) spawns `adversarial`
   as a subprocess — the PATH resolution matters
3. You may need to ensure `pip install -e .` runs before tests, or investigate
   how `ci-check.sh` sets up the environment

**This is why the task is on a feature branch, not a direct fix on main.**

## Implementation Order

1. **Fix version in `__init__.py`** — remove try/except, bare import
2. **Fix version in `cli.py`** — remove local definition, import from package
3. **Run `pip install -e ".[dev]"`** — ensure local install is current
4. **Run `pytest tests/test_cli.py::TestCLISmoke::test_version_flag -v`** — must pass
5. **Run `./scripts/core/ci-check.sh`** — must pass (this is the real test)
6. **Bump `pyproject.toml` to `1.0.0`**
7. **Reinstall**: `pip install -e ".[dev]"`
8. **Write CHANGELOG `[1.0.0]` section** (content in task spec)
9. **Add version footer to README.md**
10. **Run full test suite + ci-check.sh again**

## Key Files

| File | What to do |
|------|-----------|
| `adversarial_workflow/__init__.py` (L15-20) | Remove try/except, bare `importlib.metadata` import |
| `adversarial_workflow/cli.py` (L31-36) | Remove local `__version__`, import from `__init__` |
| `pyproject.toml` (L8) | Bump `version = "0.9.10"` → `"1.0.0"` |
| `CHANGELOG.md` | Add `[1.0.0]` section (content drafted in task spec) |
| `README.md` | Add version footer |
| `tests/test_cli.py` (~L17) | Verify `test_version_flag` passes |
| `tests/conftest.py` (~L189) | Investigate `run_cli` fixture if subprocess issues persist |

## Evaluation History

- **arch-review-fast** (Gemini 2.5 Flash): REVISION_SUGGESTED
  - Single finding: DRY the version definition (define once in `__init__.py`, import in `cli.py`)
  - Already addressed in implementation plan above
  - All other dimensions rated positively

## Branch Naming

```bash
git checkout -b feature/ADV-0071-fix-version-management
./scripts/core/project start ADV-0071
```

## Success Criteria

- [ ] No hardcoded version fallback in `__init__.py` or `cli.py`
- [ ] `pyproject.toml` is the single source of truth
- [ ] `test_version_flag` passes in `ci-check.sh` (not just standalone pytest)
- [ ] Version bumped to 1.0.0
- [ ] CHANGELOG written for 1.0.0
- [ ] All tests pass, CI passes on GitHub
