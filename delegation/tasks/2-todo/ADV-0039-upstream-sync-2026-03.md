# ADV-0039: Upstream Sync from agentive-starter-kit (March 2026)

**Status**: Todo
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 2-4 hours
**Created**: 2026-03-06

## Related Tasks

**Depends On**: None
**Blocks**: None

## Overview

Pull updates from agentive-starter-kit (upstream) into adversarial-workflow. The last
sync was 2025-01-26 at commit `5407d4e`. Since then, **74 commits** have landed upstream
adding slash commands, skills, new agents, scripts, and workflow infrastructure.

**Context**: ADR-0013 tracks the alignment relationship. `current-state.json` records
the last sync point. This is a selective file-copy operation — not a git merge — because
the two repos have diverged significantly with no shared git ancestry.

## Sync Baseline

| Field | Value |
|-------|-------|
| Upstream repo | `movito/agentive-starter-kit` |
| Upstream branch | `main` |
| Last sync date | 2025-01-26 |
| Last sync commit | `5407d4e` |
| Commits since sync | 74 |
| Upstream HEAD (at planning) | `0c68f0f` |

## Phased Implementation Plan

### Phase 1: Commands, Skills, New Agents (Highest Value, Lowest Risk)

**Rationale**: These are entirely new directories/files in adversarial-workflow. No
conflict risk — pure additions.

#### 1A. Slash Commands (`.claude/commands/`)

Copy all 10 command files wholesale from upstream. These are new — we have no
`.claude/commands/` directory at all.

| Command | Purpose |
|---------|---------|
| `check-bots.md` | Check bot review status (CodeRabbit, BugBot) |
| `check-ci.md` | Check GitHub Actions CI status |
| `check-spec.md` | Validate task spec completeness |
| `commit-push-pr.md` | Guided commit + push + PR creation |
| `preflight.md` | Pre-push validation checks |
| `retro.md` | Post-task retrospective |
| `start-task.md` | Initialize a task (branch + status) |
| `status.md` | Show project/task status overview |
| `triage-threads.md` | Triage PR review threads |
| `wait-for-bots.md` | Wait for bot reviews to complete |

**Action**: `mkdir -p .claude/commands && cp upstream/.claude/commands/*.md .claude/commands/`

**Post-copy review**: Scan for hardcoded references to `agentive-starter-kit` or `ASK-`
task prefixes and replace with `adversarial-workflow` / `ADV-` where appropriate.

#### 1B. Skills (`.claude/skills/`)

Copy all 5 skill directories from upstream. We have no `.claude/skills/` directory.

| Skill | Purpose |
|-------|---------|
| `bot-triage/SKILL.md` | Automated bot review triage |
| `code-review-evaluator/SKILL.md` | Run code review via evaluator |
| `pre-implementation/SKILL.md` | Pre-implementation planning |
| `review-handoff/SKILL.md` | Prepare review for handoff |
| `self-review/SKILL.md` | Self-review before submitting |

**Action**: `cp -r upstream/.claude/skills/ .claude/skills/`

**Post-copy review**: Same branding/prefix scan as 1A.

#### 1C. New Agent Definitions (`.claude/agents/`)

Add agents that exist upstream but not locally. Do NOT overwrite existing agents.

| Agent | Action | Notes |
|-------|--------|-------|
| `bootstrap.md` | **ADD** | New — project bootstrap agent |
| `powertest-runner.md` | **ADD** | New — advanced test runner |
| `tycho.md` | **ADD** | New — day-to-day project management |

**Action**: Copy only these 3 files. Do not touch existing agents.

#### 1D. Updated Agent Definitions (`.claude/agents/`)

These agents exist in both repos and have been modified upstream. Requires a
**diff review** before overwriting.

| Agent | Local Size | Upstream Size | Risk |
|-------|-----------|---------------|------|
| `feature-developer-v3.md` | 14.8KB | Upstream modified | **HIGH** — we have local edits |
| `planner2.md` | 26.3KB | Upstream modified | **HIGH** — we have local edits |
| `AGENT-TEMPLATE.md` | 10.7KB | Upstream modified | Medium |
| `OPERATIONAL-RULES.md` | 2.9KB | Upstream modified | Low |
| `TASK-STARTER-TEMPLATE.md` | 9.9KB | Upstream modified | Low |
| `agent-creator.md` | 15.7KB | Upstream modified | Medium |
| `ci-checker.md` | 7.2KB | Upstream modified | Low |
| `code-reviewer.md` | 12.0KB | Upstream modified | Medium — ours is larger |
| `document-reviewer.md` | 8.6KB | Upstream modified | Low |
| `feature-developer.md` | 16.6KB | Upstream modified | Medium |
| `onboarding.md` | 19.3KB | Upstream modified | Low |
| `planner.md` | 23.0KB | Upstream modified | Medium |
| `security-reviewer.md` | 5.5KB | Upstream modified | Low |
| `test-runner.md` | 7.0KB | Upstream modified | Low |

**Action**: For each file, run `diff` between local and upstream. Decide per-file:
- If local has no meaningful custom edits: replace with upstream version
- If local has custom edits: merge manually, preserving our customizations
- `code-reviewer.md` and `pypi-publisher.md`: preserve ours (unique to this project)

**Critical files requiring manual merge**:
- `feature-developer-v3.md` — both repos have modified this significantly
- `planner2.md` — both repos have modified this significantly

---

### Phase 2: Scripts (Medium Value, Low-Medium Risk)

#### 2A. New Scripts

Scripts that exist upstream but not locally. Pure additions.

| Script | Purpose |
|--------|---------|
| `scripts/bootstrap.sh` | Project bootstrap |
| `scripts/check-bots.sh` | Check bot review status |
| `scripts/create-agent.sh` | Agent creation utility |
| `scripts/gh-review-helper.sh` | GitHub review helper |
| `scripts/pattern_lint.py` | Defensive coding linter |
| `scripts/preflight-check.sh` | Pre-push checks |
| `scripts/setup-dev.sh` | Dev environment setup |
| `scripts/wait-for-bots.sh` | Wait for bot reviews |

**Action**: Copy these 8 files. Make executable (`chmod +x`).

**Post-copy review**: Check for hardcoded project names or paths.

#### 2B. Updated Scripts

Scripts that exist in both repos and have upstream modifications.

| Script | Notes |
|--------|-------|
| `scripts/ci-check.sh` | Compare and merge |
| `scripts/project` | Compare and merge — may have local customizations |
| `scripts/validate_task_status.py` | Compare and merge |
| `scripts/verify-setup.sh` | Compare and merge |

**Action**: Diff each file and merge changes.

#### 2C. Scripts to Skip

| Script | Reason |
|--------|--------|
| `scripts/linear_sync_utils.py` | Linear-specific, we don't use Linear |
| `scripts/sync_tasks_to_linear.py` | Linear-specific |
| `scripts/verify-ci.sh` | Evaluate if needed |

**Decision needed**: Do we want Linear sync infrastructure? Previous decision was no.

#### 2D. New Test Files

| Test | Purpose |
|------|---------|
| `tests/conftest.py` | Shared test fixtures |
| `tests/test_create_agent.py` | Tests for create-agent.sh |
| `tests/test_pattern_lint.py` | Tests for pattern_lint.py |
| `tests/test_project_script.py` | Tests for scripts/project |
| `tests/test_uv_detection.py` | Tests for uv detection |
| `tests/integration/__init__.py` | Integration test package |
| `tests/integration/test_concurrent_agent_creation.py` | Concurrent agent tests |

**Action**: Copy test files that correspond to scripts we're pulling. Skip tests for
scripts we're not pulling.

---

### Phase 3: Settings, Config, CLAUDE.md (Medium Value, Needs Care)

#### 3A. `.claude/settings.json` — MERGE, Do Not Replace

Our settings.json has Serena MCP permissions that upstream doesn't have.
Upstream has richer Bash permissions we want.

**Current local** (key items):
```json
{
  "permissions": {
    "allow": [
      "mcp__serena__activate_project",
      "mcp__serena__read_file",
      ... (Serena MCP permissions)
    ]
  }
}
```

**Upstream additions we want**:
```json
{
  "permissions": {
    "allow": [
      "Bash(git *)",
      "Bash(gh *)",
      "Bash(pytest *)",
      "Bash(./scripts/*)",
      "Bash(python* scripts/*.py*)",
      "Bash(black *)",
      "Bash(isort *)",
      "Bash(flake8 *)",
      "Bash(adversarial *)",
      "Bash(ruff *)",
      "Bash(pre-commit *)",
      "Read", "Write", "Edit", "MultiEdit",
      "Glob", "Grep", "Skill", "WebFetch", "Task"
    ],
    "deny": [
      "Bash(git push --force*)",
      "Bash(git push -f*)",
      "Bash(git reset --hard*)",
      "Bash(git clean*)",
      "Bash(git branch -D*)",
      "Bash(rm -rf*)",
      "Bash(rm -r *)",
      "Bash(gh repo delete*)",
      "Bash(pip install*)",
      "Bash(uv add*)",
      "Bash(curl*|*curl*)",
      "Bash(wget*)"
    ]
  }
}
```

**Action**: Merge both permission sets. Keep all Serena permissions + add upstream
Bash/tool permissions + add deny list.

**Note**: We also have `settings.local.json` — check if that's affected.

#### 3B. `CLAUDE.md` — CREATE with Adaptation

Upstream has a root-level `CLAUDE.md` that provides architecture overview for all
agents. We don't have one. This is high-value context.

**Action**: Copy from upstream, then adapt:
- Replace "Agentive Starter Kit" with "adversarial-workflow"
- Update directory structure to reflect our actual layout
- Add our project-specific sections (adversarial CLI, evaluator system)
- Preserve upstream's Python rules, branching, task workflow sections

#### 3C. `.coderabbitignore` — ADD

**Action**: Copy from upstream. Prevents CodeRabbit from reviewing irrelevant files.

#### 3D. `.pre-commit-config.yaml` — MERGE

Upstream has added `pattern-lint` and `validate-task-status` hooks.

**Action**: Diff and merge new hooks into our config.

#### 3E. `.gitignore` — MERGE

**Action**: Diff and add any new entries.

#### 3F. `pyproject.toml` — REVIEW

Upstream may have added new dev dependencies (e.g., black 26.1.0).

**Action**: Review diff, selectively adopt dependency updates.

---

### Phase 4: Workflow & Documentation (Lower Priority)

#### 4A. New Workflows

| File | Purpose |
|------|---------|
| `.agent-context/workflows/EVALUATOR-LIBRARY-WORKFLOW.md` | Evaluator library usage |
| `.agent-context/workflows/PR-SIZE-WORKFLOW.md` | PR size management |
| `.agent-context/workflows/RESEARCH-QUALITY-STANDARDS.md` | Research quality |
| `.agent-context/workflows/WORKFLOW-FREEZE-POLICY.md` | Workflow freeze policy |

**Action**: Copy these 4 files.

#### 4B. Updated Workflows

| File | Notes |
|------|-------|
| `.agent-context/workflows/AGENT-CREATION-WORKFLOW.md` | Diff and merge |
| `.agent-context/workflows/COMMIT-PROTOCOL.md` | Diff and merge |

#### 4C. Patterns File

| File | Purpose |
|------|---------|
| `.agent-context/patterns.yml` | Defensive coding patterns |

**Action**: Copy from upstream. This is referenced by `pattern_lint.py`.

#### 4D. Documentation

| File | Purpose | Action |
|------|---------|--------|
| `docs/LINEAR-SYNC-BEHAVIOR.md` | Linear sync reference | Copy if we want Linear docs |
| `docs/tmux-tips.md` | Tmux usage tips | Copy |
| `.adversarial/docs/EVALUATION-WORKFLOW.md` | Updated eval workflow | Diff and merge |

#### 4E. GitHub Workflows

| File | Notes |
|------|-------|
| `.github/workflows/test.yml` | May have CI improvements |

**Action**: Diff and selectively merge.

---

### Phase 5: Housekeeping & Tracking Update

After all phases complete:

1. **Update `current-state.json`**: Set `starter_kit_sync.last_synced` to today,
   update `source_commit` to upstream HEAD at time of sync
2. **Update ADR-0013**: Mark newly aligned items, update comparison matrix
3. **Update CHANGELOG.md**: Add entry under `[Unreleased]`
4. **Run tests**: `pytest tests/ -v` to verify nothing broke
5. **Run pre-commit**: `pre-commit run --all-files`
6. **Run CI check**: `./scripts/ci-check.sh`

---

## Exclusion List (Do NOT Pull)

These upstream files are project-specific to agentive-starter-kit and should NOT
be copied:

| Category | Files | Reason |
|----------|-------|--------|
| Task handoffs | `.agent-context/ASK-*` (~20 files) | Upstream task history |
| Task reviews | `.agent-context/reviews/ASK-*` (~10 files) | Upstream review history |
| Task specs | `delegation/tasks/*/ASK-*` (~30 files) | Upstream task specs |
| Session handovers | `.agent-context/2025-*-SESSION-*` | Upstream session logs |
| Miriad research | `.agent-context/research/miriad/` | Upstream-specific research |
| Curriculum docs | `docs/archive/agentive-development/` (~80 files) | Upstream curriculum |
| Starter kit ADRs | `docs/decisions/starter-kit-adr/KIT-ADR-002*` | Upstream ADRs |
| Dispatch config | `.dispatch/config.yml` | dispatch-kit specific |
| Env templates | `.env.example`, `.env.template` | We have our own |
| Upstream changes doc | `docs/UPSTREAM-CHANGES-2025-01-28.md` | Upstream internal doc |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| settings.json merge breaks permissions | Medium | High | Test in new Claude Code session after merge |
| Agent definition merge loses local edits | Medium | High | Diff every file, manual merge for high-risk agents |
| Scripts reference wrong project name | Low | Low | grep for `agentive-starter-kit` and `ASK-` post-copy |
| Pre-commit hooks fail after new hooks added | Medium | Medium | Run `pre-commit run --all-files` after merge |
| Test suite breaks from new test dependencies | Low | Medium | Run `pytest` after each phase |

## Execution Strategy

- **Do this on main** — these are infrastructure/coordination files, not feature code
- **Commit after each phase** — allows easy rollback if something breaks
- **Clone upstream to `/tmp/`** — work from a fresh clone, not a stale local copy
- **Run full validation after each phase** before proceeding to next

## Acceptance Criteria

### Must Have
- [ ] All 10 slash commands available (`.claude/commands/`)
- [ ] All 5 skills available (`.claude/skills/`)
- [ ] New agents added (bootstrap, powertest-runner, tycho)
- [ ] Missing scripts added and executable
- [ ] settings.json merged (Serena + upstream permissions)
- [ ] CLAUDE.md created and adapted for adversarial-workflow
- [ ] `current-state.json` sync tracking updated
- [ ] ADR-0013 updated
- [ ] All tests passing
- [ ] Pre-commit hooks passing

### Should Have
- [ ] Updated agent definitions (non-critical ones) merged
- [ ] New workflows copied
- [ ] `patterns.yml` added
- [ ] `.coderabbitignore` added

### Nice to Have
- [ ] GitHub workflows updated
- [ ] Feature-developer-v3 and planner2 carefully merged

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| Phase 1: Commands, skills, new agents | 30-45 min | [ ] |
| Phase 1D: Agent diffs & merges | 30-60 min | [ ] |
| Phase 2: Scripts | 20-30 min | [ ] |
| Phase 3: Settings, CLAUDE.md, config | 30-45 min | [ ] |
| Phase 4: Workflows & docs | 15-20 min | [ ] |
| Phase 5: Housekeeping & validation | 15-20 min | [ ] |
| **Total** | **2-4 hours** | [ ] |

## References

- **Upstream repo**: https://github.com/movito/agentive-starter-kit
- **ADR-0013**: `docs/decisions/adr/0013-agentive-starter-kit-alignment.md`
- **Sync tracking**: `.agent-context/current-state.json` -> `starter_kit_sync`
- **Previous sync**: ADV-0027 (2025-01-26)

---

**Template Version**: 2.0.0
**Project**: adversarial-workflow
**Last Updated**: 2026-03-06
