## ADV-0043 — Sync Agent Definitions from Upstream (PR #43)

**Date**: 2026-03-10
**Agent**: feature-developer-v3 (manual execution in main thread)
**Scorecard**: 3 threads, 0 regressions, 1 fix round (all resolved without code changes), 1 commit

### What Worked

1. **Verbatim copy strategy** — The handoff file provided exact `cp` commands and a clear list of 11 files. No ambiguity, execution took minutes.
2. **Protected file verification** — Running `git diff --name-only | grep` immediately after copy confirmed no protected files were touched. Simple and effective.
3. **Upstream-sync bot dismissal strategy** — Task spec pre-authorized dismissing bot findings as upstream's concern, which made triage instant. All 3 threads resolved without code changes.

### What Was Surprising

1. **CI fails on main too** — The DK002 pattern lint violations (~100 instances) fail `ci-check.sh` even on main. This was already noted in memory but worth flagging again — it means CI is currently broken for all branches.
2. **BugBot found a real issue** — The `local-app` path references in `test-runner.md` are genuinely wrong for downstream projects. Filed upstream issue #34. Not a blocker for this sync, but a real finding.

### What Should Change

1. **Fix CI on main** — DK002 violations make `ci-check.sh` useless as a gate. Either fix the ~100 violations or downgrade DK002 to a warning. Currently every task has to note "CI failure is pre-existing."
2. **Upstream sync tasks should skip spec-check/evaluator gates** — For verbatim copy tasks, the full feature-developer-v3 workflow (spec-check, evaluator, preflight) is overkill. A lighter "sync" workflow would be more appropriate.

### Permission Prompts Hit

None.

### Process Actions Taken

- [ ] Fix DK002 violations on main so CI is a meaningful gate again
- [ ] Consider a lightweight "sync" workflow for upstream copy tasks
- [ ] Track upstream issue movito/agentive-starter-kit#34 for local-app path fix
