## ADV-0048 — Fix find_task_file Boundary Matching (PR #46)

**Date**: 2026-03-11
**Agent**: feature-developer-v3 (manual execution)
**Scorecard**: 1 thread, 0 regressions, 1 fix round, 1 commit

### What Worked

1. **Minimal scope kept it fast** — Single function replacement with clear before/after in the spec. No ambiguity, no architectural decisions. Start-to-PR in under 10 minutes.
2. **Inline boundary testing** — Testing the fix with a Python snippet that exercised `ADV-4` vs `ADV-0048` caught the exact scenario described in the bug. More targeted than pytest for a non-importable script.
3. **BugBot thread was easy to triage** — False positive about duplicate task files (git tracked it as a rename). Quick to verify with `git diff main --name-status` and resolve.

### What Was Surprising

1. **No CI triggered** — The GitHub Actions workflow has a `paths` filter limited to `adversarial_workflow/**`, `tests/**`, and `pyproject.toml`. Changes to `scripts/core/` don't trigger CI at all. This means script bugs can ship without any automated validation.
2. **`scripts/core/project` is untestable by CI** — Even if the paths filter included `scripts/**`, pytest doesn't test any functions in the script. It's a standalone file, not an importable module.

### What Should Change

1. **Add `scripts/**` to CI paths filter** — Even if pytest doesn't cover scripts directly, it ensures the full test suite runs when scripts change (guards against indirect breakage).
2. **Consider making `find_task_file` importable** — Extract core logic from `scripts/core/project` into a testable module, or add a `tests/test_project_script.py` that imports the function directly. The boundary matching bug would have been caught by a simple unit test.

### Permission Prompts Hit

None.

### Process Actions Taken

- [ ] Add `scripts/**` to `.github/workflows/test-package.yml` paths filter
- [ ] Consider adding tests for `scripts/core/project` functions (find_task_file, move_task, etc.)
