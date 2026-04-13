# Core Scripts Design — How Shared Scripts Should Work

**Date**: 2026-03-08
**Status**: Approved (decisions locked 2026-03-08)
**Related**: SCRIPTS-SYNC-ANALYSIS.md, ADW-UPGRADE-PLAN.md

## Decisions (Locked)

1. **`project` is core** — standardized across all repos, parameterized via `pyproject.toml`
2. **Directory structure**: `scripts/core/` + `scripts/local/` in every repo
3. **Automated sync PRs** — GitHub Action in agentive-starter-kit opens PRs in downstream repos on core changes

## Problem

Four repos maintain independent copies of ~15 shared scripts. No sync mechanism exists. Drift is pervasive: 13/15 shared files have diverged between just dispatch-kit and agentive-starter-kit.

## Design Principles

1. **Single source of truth** — one canonical location per script
2. **Explicit versioning** — scripts carry version metadata, repos pin versions
3. **Copy, don't link** — repos own their copies (no git submodules, no runtime fetches)
4. **Parameterize, don't fork** — scripts adapt via config, not per-project branches
5. **Detect drift** — tooling that flags when a local copy diverges from upstream
6. **Automate sync** — GitHub Actions open PRs in downstream repos when core changes

## Architecture

### Source of Truth: agentive-starter-kit

agentive-starter-kit is the **template repo** and canonical source for all core scripts. dispatch-kit, adversarial-workflow, and adversarial-evaluator-library are downstream consumers.

### Directory Layout (all repos)

```
scripts/
  ├── core/                        ◀── synced from agentive-starter-kit (DO NOT EDIT locally)
  │   ├── VERSION                  ◀── semver for the core bundle
  │   ├── ci-check.sh
  │   ├── verify-ci.sh
  │   ├── verify-setup.sh
  │   ├── check-bots.sh
  │   ├── wait-for-bots.sh
  │   ├── gh-review-helper.sh
  │   ├── preflight-check.sh
  │   ├── pattern_lint.py
  │   ├── validate_task_status.py
  │   ├── logging_config.py
  │   ├── project                  ◀── standardized task management CLI
  │   └── __init__.py
  ├── local/                       ◀── project-specific scripts (never synced)
  │   ├── arch_check.py            ◀── example: dispatch-kit only
  │   └── ...
  ├── .core-manifest.json          ◀── tracks installed core version + checksums
  └── README.md
```

**Key rules**:
- `scripts/core/` is **read-only** in downstream repos — all edits happen in agentive-starter-kit
- `scripts/local/` is **project-specific** — never synced, never overwritten
- Existing `scripts/*.sh` and `scripts/*.py` at the root are migrated into `core/` or `local/`

### Upstream Layout (agentive-starter-kit only)

```
scripts/
  ├── core/                        ◀── same as downstream
  ├── local/                       ◀── ASK-specific scripts
  │   ├── bootstrap.sh
  │   ├── create-agent.sh
  │   └── setup-dev.sh
  ├── optional/                    ◀── scripts downstream projects can opt into
  │   ├── linear_sync_utils.py
  │   ├── sync_tasks_to_linear.py
  │   ├── create-agent.sh
  │   └── setup-dev.sh
  ├── .core-manifest.json
  └── README.md
```

### Manifest File

Each repo tracks its core version via `scripts/.core-manifest.json`:

```json
{
  "core_version": "1.0.0",
  "source": "agentive-starter-kit",
  "source_repo": "movito/agentive-starter-kit",
  "synced_at": "2026-03-08T12:00:00Z",
  "checksums": {
    "core/ci-check.sh": "sha256:abc123...",
    "core/verify-ci.sh": "sha256:def456...",
    "core/project": "sha256:789ghi..."
  }
}
```

The manifest enables:
1. **Drift detection** — compare local checksums to upstream
2. **Sync PRs** — GitHub Action reads manifest to know what to update
3. **Audit trail** — when was this repo last synced, from what version

### Sync Mechanism — Three Layers

**Layer 1: Automated sync PRs (primary)**

A GitHub Action in agentive-starter-kit triggers on pushes to `scripts/core/`:

1. Reads list of downstream repos from a config file
2. For each downstream repo:
   - Clones it, creates branch `chore/core-scripts-sync-v{VERSION}`
   - Copies `scripts/core/` contents
   - Updates `.core-manifest.json`
   - Opens PR with diff summary
3. Downstream maintainer reviews and merges

```yaml
# .github/workflows/sync-core-scripts.yml (in agentive-starter-kit)
on:
  push:
    paths: ['scripts/core/**']
    branches: [main]

jobs:
  sync:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        repo:
          - movito/dispatch-kit
          - movito/adversarial-workflow
          - movito/adversarial-evaluator-library
    steps:
      - uses: actions/checkout@v4
      - name: Sync to ${{ matrix.repo }}
        run: ./scripts/sync-to-downstream.sh ${{ matrix.repo }}
        env:
          GH_TOKEN: ${{ secrets.CROSS_REPO_TOKEN }}
```

**Layer 2: Manual sync with drift check (fallback)**

```bash
./scripts/core/check-sync.sh                  # compare local vs upstream
./scripts/core/check-sync.sh --apply           # pull latest core from upstream
./scripts/core/check-sync.sh --apply --force   # overwrite even if local changes detected
```

**Layer 3: `project sync-scripts` subcommand (convenience)**

```bash
./scripts/core/project sync-scripts            # alias for check-sync.sh
```

### Git subtree — Rejected

Too complex for this use case. Subtrees create merge noise and confuse contributors.

## Core Script Requirements

For a script to be "core", it must be:

1. **Generic** — no hardcoded project names, paths, or configs
2. **Parameterized** — adapts via environment variables, flags, or a config file
3. **Self-contained** — no dependencies beyond standard tools (bash, python3, git, gh)
4. **Versioned** — carries a metadata header with version, origin, last-updated

### Parameterization Points

Scripts that currently have project-specific values need parameterization:

| Script | Current Hardcoding | Proposed Solution |
|--------|-------------------|-------------------|
| `ci-check.sh` | Target directories (`src/`, `scripts/`) | Read from `pyproject.toml [tool.ci-check]` or default to `.` |
| `ci-check.sh` | Pattern lint step (present in DK/ASK, absent in ADW) | Run if `pattern_lint.py` exists, skip otherwise |
| `verify-setup.sh` | Python version range, project name | Read from `pyproject.toml [project] requires-python` |
| `project` | `EVALUATOR_LIBRARY_VERSION`, Linear integration | Feature flags via env vars or `pyproject.toml` section |
| `preflight-check.sh` | Gate list (evaluator gate may not apply to all) | Config file or skip missing gates gracefully |

### Metadata Header Standard

Every core script should carry:

```bash
# ---
# name: verify-ci.sh
# description: Check GitHub Actions CI/CD status
# version: 1.0.0
# origin: agentive-starter-kit
# origin-version: 0.5.0
# last-updated: 2026-03-08
# requires: gh
# ---
```

Python scripts use a docstring or comment block:

```python
# ---
# name: pattern_lint.py
# description: Project pattern linter (DK rules)
# version: 1.0.0
# origin: agentive-starter-kit
# origin-version: 0.5.0
# last-updated: 2026-03-08
# requires: python3
# ---
```

## The "Core Bundle" — What's In, What's Out

### IN — Core Bundle (every agentive project, in `scripts/core/`)

| # | Script | Why | Slash Command |
|---|--------|-----|:-------------:|
| 1 | `project` | Task management CLI; `/start-task` | `/start-task` |
| 2 | `ci-check.sh` | Local CI mirror; pre-push hook | — |
| 3 | `verify-ci.sh` | GitHub Actions status | `/check-ci` |
| 4 | `verify-setup.sh` | Dev onboarding; sanity check | — |
| 5 | `check-bots.sh` | PR bot review status | `/check-bots` |
| 6 | `wait-for-bots.sh` | Poll for bot reviews | `/wait-for-bots` |
| 7 | `gh-review-helper.sh` | PR thread management (GraphQL) | `/triage-threads` |
| 8 | `preflight-check.sh` | 7-gate quality verification | `/preflight` |
| 9 | `pattern_lint.py` | Code quality linter (DK rules) | — (pre-commit) |
| 10 | `validate_task_status.py` | Task status/folder validation | — (pre-commit) |
| 11 | `logging_config.py` | Shared logging utility | — (import) |
| 12 | `__init__.py` | Package marker | — |

**12 scripts. 6 slash commands depend on them.**

`project` is the most complex (~40KB) but is standardized via parameterization:
- Evaluator library version: read from `pyproject.toml [tool.adversarial] library_version`
- Linear integration: enabled only if `LINEAR_API_KEY` is set
- Task folder structure: standardized across all repos (`delegation/tasks/`)

### OPTIONAL (in agentive-starter-kit `scripts/optional/`, copy to `scripts/local/` if needed)

| Script | Why Optional |
|--------|-------------|
| `linear_sync_utils.py` | Only for Linear-integrated projects |
| `sync_tasks_to_linear.py` | Only for Linear-integrated projects |
| `create-agent.sh` | Only for projects that scaffold agents |
| `setup-dev.sh` | Project-specific dev setup |

### LOCAL (in `scripts/local/`, never synced)

| Script | Repo | Why |
|--------|------|-----|
| `arch_check.py` | dispatch-kit | Domain boundary validation |
| `lint-all.sh` | dispatch-kit | Pattern lint wrapper for `src/` |
| `verify-v0.4.0.sh` | evaluator-library | Version migration check |
| `bootstrap.sh` | agentive-starter-kit | First-run project setup |

## Migration Path

### Phase 1: Establish the core in agentive-starter-kit

**Repo**: agentive-starter-kit
**Branch**: `chore/scripts-core-restructure`
**Effort**: ~2 hours

1. Create `scripts/core/` directory with `VERSION` file (start at `1.0.0`)
2. Move the 12 core scripts into `scripts/core/`
3. Move ASK-specific scripts (`bootstrap.sh`) into `scripts/local/`
4. Move optional scripts into `scripts/optional/`
5. Parameterize hardcoded values in core scripts (see Parameterization Points)
6. Add metadata headers to all core scripts
7. Create `scripts/.core-manifest.json`
8. Create `scripts/core/check-sync.sh`
9. Update all internal references (`pre-commit-config.yaml`, slash commands, agent definitions) to use `scripts/core/` paths
10. Update `bootstrap.sh` to install new structure in new projects
11. Create `.github/workflows/sync-core-scripts.yml`

### Phase 2: Migrate downstream repos

**Per-repo effort**: ~1 hour each

For each downstream repo (dispatch-kit, adversarial-workflow, adversarial-evaluator-library):

1. Create `scripts/core/` and `scripts/local/`
2. Copy core scripts from agentive-starter-kit `scripts/core/`
3. Move project-specific scripts to `scripts/local/`
4. Create `scripts/.core-manifest.json`
5. Update all references to use new paths:
   - `.claude/commands/*.md` — slash commands
   - `.pre-commit-config.yaml` — hooks
   - `.claude/agents/*.md` — agent definitions
   - Any CI workflows
6. Verify all slash commands work
7. Delete old flat scripts at `scripts/` root (after confirming no references remain)

### Phase 3: Ongoing maintenance

1. All core script changes happen in agentive-starter-kit first
2. Bump `scripts/core/VERSION` on each change
3. GitHub Action opens sync PRs in downstream repos automatically
4. Downstream maintainer reviews and merges sync PRs
5. If a downstream project needs a core script change:
   - PR to agentive-starter-kit first
   - Wait for sync PR to propagate
   - Never edit `scripts/core/` locally

### Phase 4: Maturity

Once stable:
1. Add checksum verification to pre-commit (warn if core scripts modified locally)
2. Add `/check-sync` slash command for manual drift detection
3. Consider extracting core scripts into a standalone repo if the ecosystem grows beyond 4 repos

## Slash Command Path Updates

All slash commands need their script paths updated after migration:

| Command | Old Path | New Path |
|---------|----------|----------|
| `/check-ci` | `./scripts/verify-ci.sh` | `./scripts/core/verify-ci.sh` |
| `/check-bots` | `./scripts/check-bots.sh` | `./scripts/core/check-bots.sh` |
| `/wait-for-bots` | `./scripts/wait-for-bots.sh` | `./scripts/core/wait-for-bots.sh` |
| `/triage-threads` | `./scripts/gh-review-helper.sh` | `./scripts/core/gh-review-helper.sh` |
| `/preflight` | `./scripts/preflight-check.sh` | `./scripts/core/preflight-check.sh` |
| `/commit-push-pr` | `./scripts/preflight-check.sh` | `./scripts/core/preflight-check.sh` |
| `/start-task` | `./scripts/project` | `./scripts/core/project` |
