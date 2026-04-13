# ADV-0068: Migrate to .kit/ Directory Layout

**Status**: In Review
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 3-5 hours
**Created**: 2026-04-13
**Parent**: KIT-ADR-0023 (Builder/Project Separation)

## Related Tasks

**Depends On**: None (all prerequisites complete)
**Blocks**: Future upstream sync tasks (sync will target .kit/ paths)

## Overview

Migrate adversarial-workflow from the legacy `delegation/` + `.agent-context/` layout to the
`.kit/` directory structure defined by KIT-ADR-0023. This separates builder infrastructure
(planning, coordination, evaluation, task management) from project code (source, tests,
implementation agents).

**Context**: The agentive-starter-kit has adopted `.kit/` as the builder layer root. The
reference migration (AEL-0013 in adversarial-evaluator-library) is complete and serves as
the template. This project has a larger footprint (~60-80 files with path references) due
to more agents, skills, and a richer task history.

**Reference project**: `~/Github/adversarial-evaluator-library` (already migrated)
**ADR**: `~/Github/agentive-starter-kit/.kit/adr/KIT-ADR-0023-builder-project-separation.md`

## Pre-Flight Survey

| Check | Result |
|-------|--------|
| `.agent-context/` | ~55 files: handoffs, reviews, retros, workflows, templates, state JSON, research, archive |
| `delegation/tasks/` | 9 status folders + README + evaluations/ (~75 task files total) |
| `delegation/handoffs/` | 8 legacy files from Oct 2025 |
| `agents/` at root | Launchers: launch, onboarding, preflight |
| `.claude/agents/` templates | AGENT-TEMPLATE.md, TASK-STARTER-TEMPLATE.md, OPERATIONAL-RULES.md |
| `scripts/core/` | Already restructured (ADV-0052) — 15 files |
| `.adversarial/` | config.yml, evaluators/, docs/, inputs/, logs/ — stays at root |
| `docs/decisions/adr/` | 15 project ADRs + library-refs/ |
| `.agent-context/` ref count | ~70 files |
| `delegation/tasks/` ref count | ~65 files |
| `agents/` (launchers) ref count | ~5 files |

## Scope

### What Moves

| Source | Destination | Method |
|--------|-------------|--------|
| `.agent-context/*` | `.kit/context/*` | `git mv` |
| `delegation/tasks/*` | `.kit/tasks/*` | `git mv` |
| `delegation/handoffs/*` | `.kit/context/archive/` | `git mv` (legacy) |
| `agents/{launch,onboarding,preflight}` | `.kit/launchers/` | `git mv` |
| `.claude/agents/AGENT-TEMPLATE.md` | `.kit/templates/` | `git mv` |
| `.claude/agents/OPERATIONAL-RULES.md` | `.kit/templates/` | `git mv` |
| `.claude/agents/TASK-STARTER-TEMPLATE.md` | `.kit/templates/` | `git mv` |

### What Stays

| Location | Reason |
|----------|--------|
| `.adversarial/` | CLI tool hardcodes this path; only update `task_directory` in config.yml |
| `.claude/agents/*.md` (all agents) | Claude Code resolves agents from `.claude/agents/` |
| `.claude/commands/*.md` | Claude Code resolves commands from `.claude/commands/` |
| `.claude/skills/` | Claude Code resolves skills from `.claude/skills/` |
| `scripts/` | Already well-separated |
| `docs/decisions/adr/` | Project ADRs stay as-is |
| `.serena/` | Serena hardcodes path |

### What Gets Created (New)

| Path | Purpose |
|------|---------|
| `.kit/adr/` | KIT ADR directory (initially just README.md) |
| `.kit/docs/` | Builder documentation |
| `.kit/skills/` | Empty placeholder (skills stay in .claude/ for now) |

## Requirements

### Functional Requirements

1. All `.agent-context/` contents moved to `.kit/context/` preserving subdirectory structure
2. All `delegation/tasks/` moved to `.kit/tasks/` preserving 1-backlog through 9-reference structure
3. Legacy `delegation/handoffs/` absorbed into `.kit/context/archive/`
4. Agent launcher scripts moved from `agents/` to `.kit/launchers/`
5. Builder templates moved from `.claude/agents/` to `.kit/templates/`
6. `scripts/core/project` updated — all `delegation/tasks` → `.kit/tasks`, `.agent-context` → `.kit/context`
7. `scripts/core/validate_task_status.py` updated — task path constant
8. `.adversarial/config.yml` updated — `task_directory: .kit/tasks/`
9. All agent definitions (~16 files) — path references updated
10. All commands referencing paths (~5 files) — updated
11. All skills referencing paths (~3 files) — updated
12. `CLAUDE.md` — directory structure section rewritten for `.kit/` layout
13. `.pre-commit-config.yaml` — validate-task-status file pattern updated
14. Zero stale references in active files (historical/archive references left as-is)
15. `scripts/core/preflight-check.sh` — path references updated

### Non-Functional Requirements
- [ ] Git history preserved via `git mv` for all moved files
- [ ] Single atomic PR (no half-migrated state)
- [ ] All existing tests pass unchanged (no Python source logic changes)
- [ ] Pre-commit hooks pass with new paths

## Implementation Plan

### Phase A: Create .kit/ Skeleton

```bash
mkdir -p .kit/{adr,context/{reviews,retros,templates,workflows,archive,research},docs,launchers,skills,tasks/{1-backlog,2-todo,3-in-progress,4-in-review,5-done,6-canceled,7-blocked,8-archive,9-reference},templates}
```

### Phase B: Move Files (git mv for history)

**Order matters** — move deepest paths first to avoid conflicts.

1. **Context subdirs first**:
   - `git mv .agent-context/workflows/* .kit/context/workflows/`
   - `git mv .agent-context/reviews/* .kit/context/reviews/`
   - `git mv .agent-context/retros/* .kit/context/retros/`
   - `git mv .agent-context/templates/* .kit/context/templates/`
   - `git mv .agent-context/research/* .kit/context/research/`
   - `git mv .agent-context/archive/* .kit/context/archive/`

2. **Context root files**:
   - `git mv .agent-context/*.md .kit/context/`
   - `git mv .agent-context/*.json .kit/context/`
   - `git mv .agent-context/*.yml .kit/context/`

3. **Tasks**:
   - `git mv delegation/tasks/* .kit/tasks/`

4. **Legacy handoffs → archive**:
   - `git mv delegation/handoffs/* .kit/context/archive/`

5. **Launchers**:
   - `git mv agents/launch .kit/launchers/`
   - `git mv agents/onboarding .kit/launchers/`
   - `git mv agents/preflight .kit/launchers/`

6. **Templates**:
   - `git mv .claude/agents/AGENT-TEMPLATE.md .kit/templates/`
   - `git mv .claude/agents/OPERATIONAL-RULES.md .kit/templates/`
   - `git mv .claude/agents/TASK-STARTER-TEMPLATE.md .kit/templates/`

7. **Clean up empty directories**:
   - Remove `delegation/`, `.agent-context/`, `agents/`

### Phase C: Rewrite Path References

Bulk sed replacements in this order (most specific first to avoid partial matches):

```bash
# 1. delegation/tasks/ → .kit/tasks/
# 2. .agent-context/workflows/ → .kit/context/workflows/
# 3. .agent-context/reviews/ → .kit/context/reviews/
# 4. .agent-context/retros/ → .kit/context/retros/
# 5. .agent-context/templates/ → .kit/context/templates/
# 6. .agent-context/archive/ → .kit/context/archive/
# 7. .agent-context/ → .kit/context/  (catch-all last)
# 8. delegation/handoffs/ → .kit/context/archive/
# 9. agents/launch → .kit/launchers/launch
# 10. agents/onboarding → .kit/launchers/onboarding
# 11. agents/preflight → .kit/launchers/preflight
```

**Files to update** (grouped by type):

| Category | Files | ~Count |
|----------|-------|--------|
| Agent definitions | `.claude/agents/planner.md`, `planner2.md`, `feature-developer*.md`, `code-reviewer.md`, `document-reviewer.md`, `security-reviewer.md`, `test-runner.md`, `powertest-runner.md`, `ci-checker.md`, `onboarding.md`, `agent-creator.md`, `pypi-publisher.md` | ~16 |
| Commands | `retro.md`, `wrap-up.md`, `start-task.md`, `status.md`, `check-spec.md` | ~5 |
| Skills | `code-review-evaluator/SKILL.md`, `review-handoff/SKILL.md`, `self-review/SKILL.md` | ~3 |
| Scripts | `scripts/core/project`, `scripts/core/validate_task_status.py`, `scripts/core/preflight-check.sh` | 3 |
| Config | `.adversarial/config.yml`, `.pre-commit-config.yaml` | 2 |
| Root docs | `CLAUDE.md`, `README.md`, `QUICK_START.md`, `SETUP.md`, `AGENT_INTEGRATION.md`, `CHANGELOG.md` | ~6 |
| Project docs | Various under `docs/` | ~10 |
| Settings | `.claude/settings.local.json` (gitignored, update locally) | 1 |

### Phase D: Manual Verification Edits

After bulk sed, manually verify:

1. **`scripts/core/project`** — Python script with ~6 hardcoded `delegation/tasks` refs and `.agent-context` refs at specific lines (67, 130, 150, 252-257, 1062). Verify each.
2. **`scripts/core/validate_task_status.py`** — line 105: `"delegation/tasks/"` → `".kit/tasks/"`
3. **`.pre-commit-config.yaml`** — task status hook file pattern
4. **`CLAUDE.md`** — Rewrite the directory structure section entirely for `.kit/` layout
5. **`.adversarial/config.yml`** — `task_directory: .kit/tasks/`
6. **Grep verification** — search for bare `delegation`, `agent-context` to catch stragglers

### Phase E: Post-Migration Verification

1. `pytest tests/ -v` — all existing tests pass
2. `pre-commit run --all-files` — hooks work with new paths
3. `adversarial list-evaluators` — CLI still works
4. `adversarial health` — expect partial pass (CLI still looks for `.agent-context/`, see out-of-scope note)
5. `./scripts/core/project list` — task listing works from `.kit/tasks/`
6. `./scripts/core/ci-check.sh` — full local CI
7. Zero stale refs: `grep -r 'delegation/tasks\|\.agent-context' --include='*.md' --include='*.py' --include='*.sh' --include='*.yml' . | grep -v '.git/' | grep -v '.kit/' | grep -v archive | grep -v retro | grep -v 5-done | grep -v 8-archive`

## Out of Scope (Future Tasks)

These are explicitly deferred:

1. **CLI code updates** (`adversarial_workflow/cli.py`) — The `init`, `reconfigure`, and `health` commands reference `.agent-context/` and `delegation/`. These are consumer-facing commands that scaffold new projects. Per KIT-ADR-0023, consumer projects don't use `.kit/`. The health check will have a minor false warning for `.agent-context/` not found. Fixing the CLI to support both layouts is a separate task.

2. **Template updates** (`adversarial_workflow/templates/agent-context/`) — Package templates for `adversarial init`. These create consumer project structure, not our own. Separate task.

3. **KIT ADR sync** — Populating `.kit/adr/` with upstream KIT ADRs is a future sync task.

4. **Test updates** — Tests that test CLI `init`/`health` behavior reference the old paths. Since we're not changing CLI code, these tests remain valid.

## TDD Workflow

This migration is primarily file moves and text edits, not logic changes. The existing test suite serves as the regression gate.

### Test Requirements
- [ ] All existing tests pass (no source code logic changes)
- [ ] `scripts/core/project start/move/complete` work with `.kit/tasks/` path
- [ ] Pre-commit hooks pass (validate-task-status finds `.kit/tasks/`)
- [ ] Coverage: N/A (no new code)

## Acceptance Criteria

### Must Have
- [ ] `.kit/context/` contains all former `.agent-context/` files
- [ ] `.kit/tasks/` contains all former `delegation/tasks/` files
- [ ] `.kit/launchers/` contains launch, onboarding, preflight
- [ ] `.kit/templates/` contains AGENT-TEMPLATE, OPERATIONAL-RULES, TASK-STARTER-TEMPLATE
- [ ] `scripts/core/project` works with `.kit/tasks/` for all subcommands
- [ ] `scripts/core/validate_task_status.py` validates `.kit/tasks/` files
- [ ] `.adversarial/config.yml` points to `.kit/tasks/`
- [ ] All existing tests pass
- [ ] Pre-commit hooks pass
- [ ] No stale `.agent-context/` or `delegation/tasks/` references in active files
- [ ] Single atomic PR
- [ ] `CLAUDE.md` directory structure updated

### Should Have
- [ ] Git history preserved via `git mv`
- [ ] Empty `delegation/`, `.agent-context/`, `agents/` directories removed
- [ ] `.kit/adr/README.md` created as placeholder
- [ ] Historical references in retros/done-tasks left as-is (they describe the past)

## Anti-Patterns to Avoid

Per reference migration (AEL-0013) and playbook lessons:

1. **Do NOT split into multiple PRs** — must land atomically
2. **Grep for bare directory names** too, not just full paths
3. **Don't trust sed for everything** — verify context-aware edits manually
4. **Do NOT move `.adversarial/` or `.serena/`** — CLI hardcoded paths
5. **Don't delete historical references** in retros/changelogs/done-tasks
6. **Don't forget `.claude/settings.local.json`** permission patterns (gitignored)
7. **Don't forget `validate_task_status.py`** hardcoded path
8. **Don't forget `scripts/core/project`** — largest single file to update (~6 refs)
9. **sed order matters** — most specific paths first, catch-all patterns last
10. **Don't update `adversarial_workflow/cli.py`** — out of scope (consumer-facing)

## Error Handling & Rollback

**Rollback strategy**: This migration uses `git mv` on a feature branch. The entire branch
can be abandoned and the PR closed with zero impact on `main`. No database migrations, no
external service changes, no published artifacts.

**Breaking change risk**: LOW. The only runtime-adjacent code changes are `scripts/core/project`
(task management script, not application code) and `validate_task_status.py` (pre-commit hook).
All other changes are in markdown, YAML, and shell scripts read by agents, not by the application.

## Success Metrics

### Quantitative
- Test pass rate: 100% (unchanged)
- Stale path references: 0 in active files
- File moves with git history: 100%

### Qualitative
- Clean separation: builder infra in `.kit/`, project code in `.claude/` + `src/`
- Ready for future upstream sync to target `.kit/` paths

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| Create skeleton + move files | 1 hour | [ ] |
| Bulk path rewrites (sed) | 1 hour | [ ] |
| Manual verification edits | 1 hour | [ ] |
| Testing + CI verification | 0.5 hours | [ ] |
| CLAUDE.md rewrite | 0.5 hours | [ ] |
| **Total** | **4 hours** | [ ] |

## References

- **KIT-ADR-0023**: `~/Github/agentive-starter-kit/.kit/adr/KIT-ADR-0023-builder-project-separation.md`
- **Reference migration**: `~/Github/adversarial-evaluator-library/.kit/tasks/5-done/AEL-0013-kit-migration.md`
- **Reference project**: `~/Github/adversarial-evaluator-library` (post-migration state)
- **Testing**: `pytest tests/ -v`
- **Pre-commit**: `pre-commit run --all-files`
- **Local CI**: `./scripts/core/ci-check.sh`

---

**Template Version**: 2.0.0
**Project**: adversarial-workflow
**Last Updated**: 2026-04-13
