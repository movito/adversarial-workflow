# ADV-0046 Review Starter: CLAUDE.md & Sync Documentation

## PR
https://github.com/movito/adversarial-workflow/pull/49

## Summary
Docs-only PR that completes the ADV-0039 upstream sync epic (11/11 sub-tasks). Three files changed:

1. **CLAUDE.md** (new) — Project-level context for Claude Code. Adapted from upstream sync branch with corrections for Ruff tooling, `scripts/core/` paths, full agent table (includes pypi-publisher, excludes tycho).
2. **current-state.json** — Version bumped to 0.9.9, task counts updated, full sync metadata with component-by-task breakdown.
3. **ADR-0013** — Status changed to "Accepted", comparison matrix updated (most items now Aligned), sync history table added with all PRs.

## What to look for
- Does CLAUDE.md give an accurate first impression of the project?
- Are the script paths and tooling references correct?
- Is the ADR-0013 sync history complete and accurate?
- Any information that's stale or misleading?

## Bot review
- 2 CodeRabbit threads (both minor), both fixed and resolved
- Round 2 re-scan: no new findings
- BugBot: no findings

## Testing
- 493 tests pass, no regressions
- Ruff lint + format clean
- No code changes — docs/config only
