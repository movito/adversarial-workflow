# ADV-0063: Fix triage-threads consecutive-quote security prompt

**Status**: Backlog
**Priority**: Low
**Created**: 2026-03-19
**Type**: Chore
**Estimated Effort**: 30 min

---

## Problem Statement

The `/triage-threads` slash command fires a manual-approval prompt during
autonomous loop execution even though `Bash(gh *)` is already in the project
allow list. The prompt reads:

> Command contains consecutive quote characters at word start (potential
> obfuscation). Do you want to proceed?

This breaks full autonomy for the `/loop 10m /triage-threads` pattern.

## Root Cause

Claude Code has a **two-layer permission system**:

1. **Allow list** (`settings.json` → `permissions.allow`) — already has
   `Bash(gh *)`, so no missing rule.
2. **Pattern-based security heuristic** — fires on any command containing
   consecutive quote characters at a word boundary (`'"...`), *regardless* of
   allow-list rules.

The offending command in `/triage-threads` (`.claude/commands/triage-threads.md`):

```bash
gh pr view --json number,url,headRefOid --jq '"PR #\(.number) | URL: \(.url) | HEAD: \(.headRefOid)"'
```

The `'"PR` substring (single-quote immediately followed by double-quote at
word start) is what triggers the heuristic.

## Fix

Rewrite the first `gh pr view` call in `triage-threads.md` to avoid
consecutive-quote patterns. Options:

**Option A — separate jq fields (simplest):**
```bash
gh pr view --json number --jq '.number'
gh pr view --json url --jq '.url'
gh pr view --json headRefOid --jq '.headRefOid'
```
Then assemble the string in subsequent lines of the command description.

**Option B — use `@sh` or a different quoting style:**
```bash
gh pr view --json number,url,headRefOid --jq '[.number,.url,.headRefOid] | @tsv'
```

**Option C — single field, hardcode PR number in loop prompt:**
Not a fix to the command, but the loop caller can pass the PR number
explicitly: `/loop 10m triage-threads for PR 55` to skip the `gh pr view`
lookup step.

Option A is the clearest fix with no ambiguity.

## Scope

- Edit: `.claude/commands/triage-threads.md`
- No code changes, no tests required
- Must verify the rewritten command doesn't trigger the heuristic

## Acceptance Criteria

- [ ] `/triage-threads` runs the `gh pr view` step without a manual-approval
  prompt when `Bash(gh *)` is in the allow list
- [ ] Loop `CronCreate 10m /triage-threads` completes at least one full round
  (gather → triage → optional fix → resolve) with zero manual approvals

## Notes

- Discovered during ADV-0035 bot-triage loop (2026-03-19)
- Workflow freeze policy: do not fix during an active feature task
- Related: `SKIP_TESTS=1 git *` allow-list entry added in ADV-0058 for a
  similar (but different) permission issue
