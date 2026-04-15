# Review Starter: ADV-0071

**Task**: ADV-0071 - Fix Version Management + Release 1.0.0
**Task File**: `.kit/tasks/4-in-review/ADV-0071-fix-version-management-release-1.0.0.md`
**Branch**: feature/ADV-0071-fix-version-management -> main
**PR**: https://github.com/movito/adversarial-workflow/pull/67

## Implementation Summary

- Removed hardcoded version fallback strings (`"0.9.9"`) from `__init__.py` and `cli.py` that drifted from `pyproject.toml` (`0.9.10`), causing `test_version_flag` to fail in subprocess environments
- Made `pyproject.toml` the single source of truth: `importlib.metadata.version()` reads installed metadata
- `__version__` defined once in `__init__.py`, imported in `cli.py` via `from . import __version__` (DRY)
- Fixed `run_cli` test fixture: replaced `shutil.which("adversarial")` PATH search with `sys.executable` to avoid stale system-wide installs
- Bumped version to 1.0.0 with CHANGELOG section covering ADV-0065 through ADV-0070 structural cleanup series
- Added version footer to README

## Files Changed

- `adversarial_workflow/__init__.py` (modified) — removed try/except fallback, bare importlib.metadata import
- `adversarial_workflow/cli.py` (modified) — removed local `__version__`, imports from package
- `pyproject.toml` (modified) — version 0.9.10 -> 1.0.0
- `tests/conftest.py` (modified) — fixed `cli_python` and `run_cli` fixtures
- `CHANGELOG.md` (modified) — added [1.0.0] section
- `README.md` (modified) — added version footer

## Test Results

- 530 tests passing
- 66% coverage (unchanged — minimal code change)
- `ci-check.sh` fully green (format, lint, pattern lint, tests)

## Automated Review Summary

- **BugBot**: No findings
- **CodeRabbit**: 1 thread (markdownlint on evaluator input artifact) — resolved as cosmetic on non-shipped content
- **Code-review evaluator** (Gemini Flash): FAIL verdict with 3 findings, all triaged as by-design:
  1. Direct `python cli.py` execution fails — expected Python packaging behavior, never supported
  2. `PackageNotFoundError` propagation — intentional design choice per task spec
  3. `sys.executable` fixture assumes same environment — improvement over previous behavior

## Areas for Review Focus

- **Circular import safety**: `cli.py` does `from . import __version__` while `__init__.py` does `from .cli import ...`. This works because `__version__` is set BEFORE the `.cli` import in `__init__.py`. Verify this ordering is robust.
- **Test fixture change**: `run_cli` now always uses `python -m adversarial_workflow.cli` instead of the `adversarial` command. This ensures version consistency but changes how CLI tests execute.
- **Post-merge**: Create git tag `v1.0.0` after merge.

## Related ADRs

- None — straightforward bug fix + version bump

---
**Ready for human review**
