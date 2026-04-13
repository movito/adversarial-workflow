# Scripts Sync Analysis — Cross-Project Comparison

**Date**: 2026-03-08
**Context**: ADV-0051 revealed `verify-ci.sh` missing from adversarial-workflow. Investigation uncovered a larger sync gap.

## Repos Analyzed

| Repo | Role | Script Count |
|------|------|:---:|
| **agentive-starter-kit** | Template / upstream reference | 17 |
| **dispatch-kit** | Downstream project (most evolved) | 18 |
| **adversarial-evaluator-library** | Library (minimal by design) | 11 |
| **adversarial-workflow** | Downstream project (under-synced) | 6 |

## The Sync Problem

All four repos copy scripts individually with no shared package or sync mechanism. The current pattern:

1. Scripts originate in **dispatch-kit** (or agentive-starter-kit for the template)
2. Scripts embed metadata headers (`origin: dispatch-kit`, `version: 1.0.0`)
3. `bootstrap.sh` in agentive-starter-kit copies the full `scripts/` directory to new projects
4. After initial bootstrap, each repo **drifts independently**

Result: dispatch-kit and agentive-starter-kit have diverged on **13 of 15 shared files**. adversarial-workflow was bootstrapped from an older version and never caught up.

## Script Inventory — Full Matrix

### Tier 1: Core Infrastructure (every project needs these)

| Script | Purpose | DK | ASK | AEL | ADW | Generic? |
|--------|---------|:--:|:---:|:---:|:---:|:--------:|
| `ci-check.sh` | Local CI mirror (format, lint, test) | ✅ | ✅ | ✅ | ✅* | Semi — targets differ |
| `verify-ci.sh` | Check GitHub Actions status | ✅ | ✅ | ✅ | ❌ | Yes |
| `verify-setup.sh` | Verify dev environment | ✅ | ✅ | ✅ | ✅* | Semi — Python version range |
| `project` | Task management CLI | ✅ | ✅ | ✅ | ✅* | Semi — evaluator version, features |
| `__init__.py` | Package marker | ✅ | ✅ | ✅ | ❌ | Yes |

*\* = present but outdated*

### Tier 2: PR Automation (needed for agent workflow)

| Script | Purpose | DK | ASK | AEL | ADW | Generic? |
|--------|---------|:--:|:---:|:---:|:---:|:--------:|
| `check-bots.sh` | Query BugBot/CodeRabbit status | ✅ | ✅ | ❌ | ❌ | Yes |
| `wait-for-bots.sh` | Poll check-bots.sh with backoff | ✅ | ✅ | ❌ | ❌ | Yes |
| `gh-review-helper.sh` | GraphQL helpers for PR threads | ✅ | ✅ | ❌ | ❌ | Yes |
| `preflight-check.sh` | 7-gate pre-handoff verification | ✅ | ✅ | ❌ | ❌ | Yes |

### Tier 3: Code Quality (needed for pre-commit and CI)

| Script | Purpose | DK | ASK | AEL | ADW | Generic? |
|--------|---------|:--:|:---:|:---:|:---:|:--------:|
| `pattern_lint.py` | DK-pattern linter (DK001-DK003) | ✅ | ✅ | ❌ | ❌ | Yes |
| `validate_task_status.py` | Task status/folder validation | ✅ | ✅ | ✅ | ✅* | Yes |
| `logging_config.py` | Shared logging setup | ✅ | ✅ | ✅ | ✅ | Yes |

### Tier 4: Dev Setup & Scaffolding

| Script | Purpose | DK | ASK | AEL | ADW | Generic? |
|--------|---------|:--:|:---:|:---:|:---:|:--------:|
| `setup-dev.sh` | Dev environment bootstrap | ✅ | ✅ | ❌ | ❌ | Semi |
| `create-agent.sh` | Agent definition scaffolding | ✅ | ✅ | ❌ | ❌ | Yes |
| `bootstrap.sh` | First-run project setup | ❌ | ✅ | ❌ | ❌ | ASK-only |

### Tier 5: External Integrations (optional per project)

| Script | Purpose | DK | ASK | AEL | ADW | Generic? |
|--------|---------|:--:|:---:|:---:|:---:|:--------:|
| `linear_sync_utils.py` | Linear API utilities | ✅ | ✅ | ✅ | ❌ | Yes |
| `sync_tasks_to_linear.py` | Sync tasks to Linear | ✅ | ✅ | ✅ | ❌ | Yes |

### Tier 6: Project-Specific (not for sync)

| Script | Purpose | Repo |
|--------|---------|------|
| `arch_check.py` | Domain/CLI module boundary validation | DK only |
| `lint-all.sh` | Pattern lint wrapper for `src/` | DK only |
| `verify-v0.4.0.sh` | Version-specific migration check | AEL only |

## Slash Command → Script Dependencies

Every slash command in `.claude/commands/` maps to a script:

| Command | Script Required | Status in ADW |
|---------|----------------|:-------------:|
| `/check-ci` | `verify-ci.sh` | **BROKEN** — script missing |
| `/check-bots` | `check-bots.sh` | **BROKEN** — script missing |
| `/wait-for-bots` | `wait-for-bots.sh` | **BROKEN** — script missing |
| `/triage-threads` | `gh-review-helper.sh` | **BROKEN** — script missing |
| `/preflight` | `preflight-check.sh` | **BROKEN** — script missing |
| `/commit-push-pr` | `preflight-check.sh` | **BROKEN** — script missing |
| `/start-task` | `project` | Works (older version) |

**6 of 7 slash commands are broken** due to missing scripts.

## Cross-Script Call Graph

```
wait-for-bots.sh ──calls──▶ check-bots.sh
ci-check.sh ──calls──▶ pattern_lint.py
bootstrap.sh ──calls──▶ setup-dev.sh
preflight-check.sh ──reads──▶ (git, gh CLI — no script deps)
```

## File Drift Between DK and ASK

Starter-kit and dispatch-kit have diverged on most shared files:

| Script | Identical? | Newer In |
|--------|:----------:|----------|
| `check-bots.sh` | No | ASK (2026-02-27) |
| `ci-check.sh` | No | ASK (2026-02-27) |
| `gh-review-helper.sh` | **Yes** | — |
| `pattern_lint.py` | No | DK (2026-03-01) |
| `preflight-check.sh` | No | ASK (2026-02-27) |
| `project` | No | DK (2026-03-08) |
| `verify-ci.sh` | No | DK (2026-02-26) |
| `verify-setup.sh` | **Yes** | — |
| `wait-for-bots.sh` | No | ASK (2026-02-27) |

## Root Cause

No shared package or sync mechanism exists. Each repo maintains its own copy. The embedded metadata headers were designed for tracking but there's no tooling that reads them to detect drift.

## Recommendations

See companion documents:
- `CORE-SCRIPTS-DESIGN.md` — How the common core should work
- `ADW-UPGRADE-PLAN.md` — Plan for upgrading adversarial-workflow
