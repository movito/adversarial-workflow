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

- **BugBot (Cursor)**: 1 finding — garbled `PackageNotFoundError` message (FIXED: switched to `RuntimeError`)
- **CodeRabbit**: 2 markdownlint threads on evaluator artifacts (resolved as cosmetic)
- **Code-review evaluator** (3 rounds: Gemini Flash x2 + o1):
  - R1: Direct execution regression via relative import → FIXED (reverted to direct `importlib.metadata` call)
  - R2: 4 pre-existing concerns in other cli.py functions (not our changes)
  - R3 (o1): No correctness bugs. Single untested path (PackageNotFoundError) → FIXED (added tests + helpful RuntimeError)

## Areas for Review Focus

- **Version lookup in both files**: Both `__init__.py` and `cli.py` call `_get_version("adversarial-workflow")`. This duplicates the lookup mechanism but NOT any version string — both read from the same pyproject.toml metadata. A relative import would be DRYer but breaks direct `python adversarial_workflow/cli.py` execution (cli.py has shebang + `if __name__ == "__main__"` with no other relative imports).
- **Test fixture change**: `run_cli` now always uses `python -m adversarial_workflow.cli` instead of the `adversarial` command. This ensures version consistency but changes how CLI tests execute.
- **Post-merge**: Create git tag `v1.0.0` after merge.

## Related ADRs

- None — straightforward bug fix + version bump

---
**Ready for human review**
