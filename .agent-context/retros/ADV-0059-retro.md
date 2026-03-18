## ADV-0059 — GitHub Actions Paths Filter & CI Alignment (PR #51)

**Date**: 2026-03-17
**Agent**: feature-developer-v3
**Scorecard**: 7 threads, 0 regressions, 3 bot rounds, 5 commits

### What Worked

1. **Self-validating PR** — The PR touches `.github/workflows/**` which wouldn't have triggered CI before the change. CI triggering on this PR proved the paths filter works immediately.
2. **BugBot caught a real silent failure** — `pattern_lint.py` expects individual `.py` file paths, not a directory. Passing `adversarial_workflow/` would have silently linted zero files and exited 0. The task spec itself had this wrong, so without BugBot it would have shipped broken.
3. **Fast execution** — Config-only change with clear spec. Implementation was 3 edits across 2 files. Total wall-clock dominated by bot wait times, not coding.

### What Was Surprising

1. **Task spec had a real bug** — The spec's proposed YAML for pattern lint (`python3 scripts/core/pattern_lint.py adversarial_workflow/`) was wrong. The script needs `find | xargs` to expand the directory. This is the same bug BugBot caught, showing the spec was never tested.
2. **Task spec Error Handling section contradicted the Acceptance Criteria** — Error Handling said "all three steps fail CI" but Acceptance Criteria said "advisory". CodeRabbit caught this inconsistency.
3. **Bot wait times were long** — BugBot took ~15 minutes on some re-scans. CodeRabbit was also slow on initial review (~10 min). Most session time was spent waiting.

### What Should Change

1. **Task specs should validate proposed YAML** — The pattern lint command in the spec was wrong. Specs proposing exact CLI commands should be tested before writing the task.
2. **Task specs should not have contradictory sections** — The Error Handling section contradicted Notes and Acceptance Criteria on pattern lint advisory behavior. Spec authors should cross-check sections.
3. **Consider a "doc-only" bot review mode** — Round 3 produced 4 threads all on review artifacts and task spec docs, none on production code. These were all trivially resolved but added ~10 min of bot wait time.

### Permission Prompts Hit

None.

### Process Actions Taken

- [ ] Consider adding spec validation step to task creation workflow (test proposed CLI commands)
- [ ] Track bot wait times — if consistently >10 min, consider async notification instead of polling
