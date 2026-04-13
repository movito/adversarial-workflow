# Review Starter: ADV-0026

**Task**: ADV-0026 - Fix Subprocess Test Environment Issues
**Task File**: `delegation/tasks/4-in-review/ADV-0026-fix-subprocess-test-environment.md`
**Branch**: fix/adv-0026-subprocess-test-env → main
**PR**: https://github.com/movito/adversarial-workflow/pull/14

## Implementation Summary

Added `cli_python` and `run_cli` fixtures to `conftest.py` to fix tests that failed when run with system pytest. The issue was that `sys.executable` pointed to pytest's isolated Python environment which didn't have `adversarial_workflow` installed. The fix detects if the `adversarial` command is available on PATH and uses it directly, falling back to `python -m` in venv environments.

- Added 2 new fixtures: `cli_python` (interpreter detection) and `run_cli` (subprocess helper)
- Updated 49 subprocess calls across 4 test files to use the new fixture
- Fixed a flaky test that had incorrect expectations for dotenv behavior

## Files Changed

### Modified Files
- `tests/conftest.py` - Added `cli_python` and `run_cli` fixtures (+42 lines)
- `tests/test_env_loading.py` - Replaced 8 subprocess calls with `run_cli`
- `tests/test_cli.py` - Replaced 10 subprocess calls with `run_cli`, added dynamic version check
- `tests/test_cli_dynamic_commands.py` - Replaced 25 subprocess calls with `run_cli`
- `tests/test_list_evaluators.py` - Replaced 6 subprocess calls with `run_cli`

### No New Files
### No Deleted Files

## Test Results

```
pytest tests/ -v
============================= 174 passed in 6.17s ==============================

Verified with both:
- .venv/bin/python -m pytest (venv pytest) ✅
- pytest (system pytest) ✅
```

## Areas for Review Focus

1. **`cli_python` fixture logic**: Verify the detection logic is sound - it uses `shutil.which("adversarial")` to check if the command is on PATH and returns `None` to signal using the command directly vs returning `sys.executable` for venv usage.

2. **`run_cli` fixture interface**: Check if the API is intuitive - it takes `args` as a list and passes through `**kwargs` to `subprocess.run()`. Example: `run_cli(["check"], cwd=tmp_path, env=env)`

3. **Test for unusual .env entries**: Updated to accept both "2 variables" and "3 variables" due to dotenv version differences in how lines without `=` are handled. Is this the right approach or should we pin dotenv behavior?

## Related Documentation

- **Task file**: `delegation/tasks/4-in-review/ADV-0026-fix-subprocess-test-environment.md`
- **Handoff**: `.agent-context/ADV-0026-HANDOFF-feature-developer.md`

## Pre-Review Checklist (Implementation Agent)

Before requesting review, verify:

- [x] All acceptance criteria from task file are implemented
- [x] Tests written and passing (174 tests)
- [x] CI passes - All 12 jobs green
- [x] Task moved to `4-in-review/`
- [x] No debug code or console.logs left behind
- [x] Docstrings for public APIs (fixtures have docstrings)

## CodeRabbit/Bugbot Status

- CodeRabbit feedback on MY code: ✅ All 3 nitpicks addressed
- Remaining comments are for `scripts/project` (different scope, tracked as ADV-0028)

---

**Ready for code-reviewer agent in new tab**

To start review:
1. Open new Claude Code tab
2. Run: `agents/launch code-reviewer`
3. Reviewer will auto-detect this starter file
