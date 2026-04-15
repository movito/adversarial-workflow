## ADV-0071 — Fix Version Management + Release 0.9.11 (PR #67)

**Date**: 2026-04-15
**Agent**: feature-developer-v5
**Scorecard**: 7 threads, 0 regressions, 3 fix rounds, 10 commits

### What Worked

1. **3-round evaluator pipeline caught a real regression** — Round 1 (Gemini Flash) flagged that `from . import __version__` in `cli.py` broke direct script execution (`python adversarial_workflow/cli.py`). This was a genuine correctness bug introduced by our DRY refactor that unit tests wouldn't catch. Reverted to direct `importlib.metadata` call.
2. **BugBot found the garbled PackageNotFoundError** — `PackageNotFoundError.__str__` formats `args[0]` as a package name, producing mangled output like "No package metadata was found for adversarial-workflow is not installed." Switching to `RuntimeError` was the right fix.
3. **`sys.executable` fixture fix** was the root cause — The `shutil.which("adversarial")` in `cli_python` was finding `/opt/homebrew/bin/adversarial` (stale system install) instead of the venv binary. This single change fixed the long-standing `test_version_flag` failure documented in MEMORY.md.
4. **Test evaluations before release** — Running ad-hoc evaluations against backlog tasks surfaced the verdict extraction bold-markdown bug (ADV-0072) before it shipped as 1.0.0. Good decision to downgrade to 0.9.11.

### What Was Surprising

1. **Gemini Flash wraps verdicts in `**bold**` but o1 doesn't** — All three Gemini evaluator runs produced `**FAIL**` or `**NON_COMPLIANT**` with bold markers. o1 produced bare `FAIL`. The verdict regex had been working by luck because most evaluator runs used o1. This has been a silent bug affecting all Gemini-based evaluators.
2. **`importlib.reload()` + `mock.patch` for module-level code** — Testing import-time behavior required reloading modules with mocked dependencies. The pattern works but needs careful cleanup (`importlib.reload(module)` after the test) to avoid polluting other tests. Non-obvious testing technique.
3. **Session spanned 2 context windows** — The 125KB o1 input hit rate limits, requiring a focused 506-line input. The session also required `/compact` due to context length. Multi-round evaluator workflows are context-heavy.

### What Should Change

1. **Fix verdict extraction before 1.0.0** — ADV-0072 is filed. Three regex patterns to add, straightforward fix. Should be a quick task.
2. **Add evaluator output format tests to CI** — The verdict extraction regex should have a test matrix covering all model output formats (bare, bold-wrapped, list-item). Currently only tested implicitly when evaluators run.
3. **`pip install -e .` should be in the agent allow list** — The agent was blocked from reinstalling the package to refresh metadata. This caused the local `test_version_flag` to fail (cached 1.0.0 metadata vs 0.9.11 in pyproject.toml). CI handles this correctly but local dev needs the reinstall.
4. **Bot watcher agent needs reliability work** — The background monitoring agent timed out with `sleep 120` in earlier rounds. Manual `/check-bots` polling was needed as fallback. The worktree isolation is good but the polling logic is fragile.

### Permission Prompts Hit

1. **`pip install -e ".[dev]"`** — Denied. Blocked for ~30 seconds. Not in allow list. Needed to refresh package metadata after version change. Workaround: accepted that local test would fail, CI would pass.

### Process Actions Taken

- [ ] ADV-0072: Fix verdict extraction bold-markdown regex (filed in backlog)
- [ ] Add `pip install` to agent allow list (or a scoped variant like `pip install -e .`)
- [ ] Add verdict format test matrix to `tests/test_validation.py`
- [ ] Investigate bot watcher agent timeout reliability
