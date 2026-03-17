---
description: Check all 7 completion gates before requesting human review
argument-hint: "[optional --pr PR_NUMBER --task TASK_ID --type code|docs|sync]"
---

# Preflight Check

Run all 7 completion gates and present a PASS/FAIL/SKIP table.

## Step 1: Run the preflight script

```bash
./scripts/core/preflight-check.sh $ARGUMENTS
```

The script outputs structured `GATE:<number>:<name>:PASS|FAIL|SKIP:<detail>` lines and exits 0 (all non-skipped gates pass) or 1 (any fail).

### Task type modes

Use `--type` to control which gates are checked:

- `--type code` (default for code changes): All 7 gates required
- `--type docs`: Gates 1 (CI), 5 (evaluator), 6 (review starter) skipped
- `--type sync`: Gates 5, 6 skipped; gate 1 auto-skips if no code changes

If `--type` is omitted, auto-detects: no code changes → docs, otherwise → code.

For docs-only or sync tasks, pass `--type docs` or `--type sync` to avoid false gate failures.

## Step 2: Present results

Parse the `GATE:` lines and format as a PASS/FAIL table:

| # | Gate | Status | Detail |
|---|------|--------|--------|
| 1 | CI green | PASS/FAIL/SKIP | [workflow status] |
| 2 | CodeRabbit reviewed | PASS/FAIL | [review state on latest commit] |
| 3 | BugBot reviewed | PASS/FAIL | [review state on latest commit] |
| 4 | Zero unresolved threads | PASS/FAIL | [N total, N resolved, N unresolved] |
| 5 | Evaluator review persisted | PASS/FAIL/SKIP | [file path or "missing" or "skipped"] |
| 6 | Review starter exists | PASS/FAIL/SKIP | [file path or "missing" or "skipped"] |
| 7 | Task in correct folder | PASS/FAIL | [folder/file] |

### Verdict

- If all non-skipped gates pass: **READY** — proceed with review handoff (move to `4-in-review`, notify user)
- If any fail: **NOT READY (N gates failing)** — list prescriptive actions for each failing gate:
  - Gate shows SKIP: No action needed (skipped by task type mode)
  - Gate 1 fails: "Run `/check-ci` and fix failures"
  - Gate 2 fails: "Wait for CodeRabbit (1-2 min) or run `/check-bots`"
  - Gate 3 fails: "Wait for BugBot (4-6 min) or run `/check-bots`"
  - Gate 4 fails: "Run `/triage-threads` to resolve open threads"
  - Gate 5 fails: "Run the code-review evaluator and persist output"
  - Gate 6 fails: "Create the review starter file"
  - Gate 7 fails: "Run `./scripts/core/project move <TASK-ID> in-review`"

## Post-Preflight Bot Thread Policy

Bots (CodeRabbit, BugBot) may post new threads **after** all 7 gates pass.
This happens when bots rescan on a later commit. When this occurs:

1. Triage the new threads (run `/triage-threads`)
2. Fix any genuine correctness issues
3. **Do NOT re-run full preflight** — only re-check Gate 4 (unresolved threads)
4. Style nits and hypothetical concerns posted after preflight do not block handoff

Late bot threads are triaged, not blocking. The preflight result stands.

## Step 3: Emit milestone event (fire-and-forget)

After running preflight, emit the result:

```bash
dispatch emit preflight_complete --agent feature-developer --task TASK_ID --payload '{"gates_passed":N_PASSED,"gates_failed":N_FAILED}' 2>/dev/null || true
```

Replace `TASK_ID` with the task ID, `N_PASSED` and `N_FAILED` with the actual gate counts from step 2.
