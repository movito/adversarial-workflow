# ADW Scripts Upgrade Plan

**Date**: 2026-03-08
**Status**: Ready for execution
**Related**: SCRIPTS-SYNC-ANALYSIS.md, CORE-SCRIPTS-DESIGN.md

## Goal

Bring adversarial-workflow's `scripts/` folder to the `core/` + `local/` structure defined in CORE-SCRIPTS-DESIGN.md. After this, all 7 slash commands work, and the project is ready for automated sync PRs from agentive-starter-kit.

## Strategy: Two-Phase Upgrade

The full core restructure (Phase 1 in CORE-SCRIPTS-DESIGN.md) needs to happen in agentive-starter-kit first. But we can't wait — 6/7 slash commands are broken **now**.

**Phase A** (immediate): Copy scripts into `scripts/core/` using best available versions. Update all references. Unbreak slash commands.

**Phase B** (after ASK restructure): Receive the first automated sync PR from agentive-starter-kit, which will normalize everything to the canonical versions.

This plan covers Phase A only.

## Source Selection

For each script, we pick the **best available version** across repos:

| Script | Source | Rationale |
|--------|--------|-----------|
| `project` | agentive-starter-kit | Most feature-complete (44KB), has evaluator lib integration |
| `ci-check.sh` | agentive-starter-kit | Has pattern lint step, newer (2026-02-27) |
| `verify-ci.sh` | dispatch-kit | Newer (2026-02-26), more robust |
| `verify-setup.sh` | Either (identical) | Same file |
| `check-bots.sh` | agentive-starter-kit | Newer (2026-02-27) |
| `wait-for-bots.sh` | agentive-starter-kit | Newer (2026-02-27) |
| `gh-review-helper.sh` | Either (identical) | Same file |
| `preflight-check.sh` | agentive-starter-kit | Newer (2026-02-27) |
| `pattern_lint.py` | dispatch-kit | Newer (2026-03-01), more rules |
| `validate_task_status.py` | agentive-starter-kit | Specific exception types |
| `logging_config.py` | Current (identical) | Already up to date |
| `__init__.py` | Either (identical) | Same file |

## Target Structure

```
scripts/
  ├── core/                        ◀── 12 scripts synced from upstream
  │   ├── VERSION                  ◀── "0.1.0" (pre-release, before ASK restructure)
  │   ├── project
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
  │   └── __init__.py
  ├── local/                       ◀── ADW-specific (currently empty, ready for future use)
  │   └── .gitkeep
  ├── .core-manifest.json
  └── README.md                    ◀── updated to explain structure
```

## Execution Plan

### Single PR: `chore/ADW-scripts-core-structure`

**Branch**: `chore/ADW-scripts-core-structure`
**Effort**: ~45 minutes

#### Step 1: Create directory structure

```bash
mkdir -p scripts/core scripts/local
```

#### Step 2: Move existing scripts into core/

```bash
mv scripts/ci-check.sh scripts/core/
mv scripts/logging_config.py scripts/core/
mv scripts/validate_task_status.py scripts/core/
mv scripts/verify-setup.sh scripts/core/
```

Note: `scripts/project` moves too, but we replace it with the ASK version.
Note: `scripts/README.md` stays at root (updated to explain structure).

#### Step 3: Copy missing + upgraded core scripts

```bash
ASK=/Users/broadcaster_three/Github/agentive-starter-kit
DK=/Users/broadcaster_three/Github/dispatch-kit

# From agentive-starter-kit
cp $ASK/scripts/check-bots.sh       scripts/core/
cp $ASK/scripts/wait-for-bots.sh    scripts/core/
cp $ASK/scripts/gh-review-helper.sh scripts/core/
cp $ASK/scripts/preflight-check.sh  scripts/core/
cp $ASK/scripts/__init__.py         scripts/core/
cp $ASK/scripts/ci-check.sh         scripts/core/       # upgrade
cp $ASK/scripts/verify-setup.sh     scripts/core/       # upgrade
cp $ASK/scripts/validate_task_status.py scripts/core/   # upgrade
cp $ASK/scripts/project             scripts/core/       # upgrade (21KB → 44KB)

# From dispatch-kit
cp $DK/scripts/verify-ci.sh         scripts/core/
cp $DK/scripts/pattern_lint.py      scripts/core/
```

#### Step 4: Make executable + create VERSION

```bash
chmod +x scripts/core/*.sh scripts/core/project
echo "0.1.0" > scripts/core/VERSION
touch scripts/local/.gitkeep
```

#### Step 5: Remove old scripts from root

```bash
rm scripts/ci-check.sh scripts/logging_config.py \
   scripts/validate_task_status.py scripts/verify-setup.sh \
   scripts/project
```

(Only remove after step 3 copies are confirmed.)

#### Step 6: Create manifest

Create `scripts/.core-manifest.json`:
```json
{
  "core_version": "0.1.0",
  "source": "agentive-starter-kit",
  "source_repo": "movito/agentive-starter-kit",
  "note": "Pre-restructure sync. Sources are best-of from ASK + DK. Will normalize to ASK-only after ASK Phase 1.",
  "synced_at": "2026-03-08",
  "scripts": {
    "project": { "source": "agentive-starter-kit", "version": "latest" },
    "ci-check.sh": { "source": "agentive-starter-kit", "version": "latest" },
    "verify-ci.sh": { "source": "dispatch-kit", "version": "latest" },
    "verify-setup.sh": { "source": "agentive-starter-kit", "version": "latest" },
    "check-bots.sh": { "source": "agentive-starter-kit", "version": "latest" },
    "wait-for-bots.sh": { "source": "agentive-starter-kit", "version": "latest" },
    "gh-review-helper.sh": { "source": "agentive-starter-kit", "version": "latest" },
    "preflight-check.sh": { "source": "agentive-starter-kit", "version": "latest" },
    "pattern_lint.py": { "source": "dispatch-kit", "version": "latest" },
    "validate_task_status.py": { "source": "agentive-starter-kit", "version": "latest" },
    "logging_config.py": { "source": "local", "version": "current" },
    "__init__.py": { "source": "agentive-starter-kit", "version": "latest" }
  }
}
```

#### Step 7: Update all references

These files reference `./scripts/` paths and need updating to `./scripts/core/`:

**Slash commands** (`.claude/commands/`):
- `check-ci.md` → `./scripts/core/verify-ci.sh`
- `check-bots.md` → `./scripts/core/check-bots.sh`
- `wait-for-bots.md` → `./scripts/core/wait-for-bots.sh`
- `triage-threads.md` → `./scripts/core/gh-review-helper.sh`
- `preflight.md` → `./scripts/core/preflight-check.sh`
- `commit-push-pr.md` → `./scripts/core/preflight-check.sh`
- `start-task.md` → `./scripts/core/project`

**Pre-commit config** (`.pre-commit-config.yaml`):
- `validate_task_status.py` → `scripts/core/validate_task_status.py`
- Add `pattern_lint.py` hook → `scripts/core/pattern_lint.py`

**Agent definitions** (`.claude/agents/`):
- Any references to `./scripts/project` → `./scripts/core/project`
- Any references to `./scripts/ci-check.sh` → `./scripts/core/ci-check.sh`

**Other**:
- `scripts/README.md` — rewrite to explain `core/` + `local/` structure

#### Step 8: Verify

```bash
# Structure correct
ls scripts/core/*.sh scripts/core/*.py scripts/core/project scripts/core/VERSION

# Count: should be 10 shell/python + project + VERSION + __init__ = 13 files
ls scripts/core/ | wc -l

# All scripts executable
ls -la scripts/core/*.sh scripts/core/project

# Slash commands work
./scripts/core/verify-ci.sh feature/ADV-0051-evaluator-setup
./scripts/core/check-bots.sh --help 2>&1 | head -3
./scripts/core/preflight-check.sh --help 2>&1 | head -3

# CI passes
./scripts/core/ci-check.sh

# Tests pass
pytest tests/ -v

# Pattern lint doesn't break existing code
python3 scripts/core/pattern_lint.py adversarial/ tests/

# Task management still works
./scripts/core/project list
```

#### Step 9: Commit and PR

**Files to commit**:
```
scripts/core/          (12 scripts + VERSION)
scripts/local/.gitkeep
scripts/.core-manifest.json
scripts/README.md      (updated)
.claude/commands/*.md  (updated paths)
.pre-commit-config.yaml (updated paths + new hook)
```

**Files to delete**:
```
scripts/ci-check.sh
scripts/logging_config.py
scripts/validate_task_status.py
scripts/verify-setup.sh
scripts/project
```

**PR title**: `chore: Restructure scripts to core/ + local/ layout`

**PR body**:
```
## Summary
Restructures `scripts/` into `core/` (synced from upstream) + `local/`
(project-specific) layout. Adds 7 missing core scripts, upgrades 4
existing ones, and updates all slash command + pre-commit references.

This unbreaks 6/7 broken slash commands and prepares the repo for
automated sync PRs from agentive-starter-kit.

## What changed
- 7 new scripts in `scripts/core/` (check-bots, wait-for-bots, gh-review-helper,
  preflight-check, verify-ci, pattern_lint, __init__)
- 4 upgraded scripts (ci-check, verify-setup, validate_task_status, project)
- All slash commands updated to reference `scripts/core/` paths
- .pre-commit-config.yaml updated with new paths + pattern lint hook
- Added .core-manifest.json for future sync tracking

## Test plan
- [ ] All slash commands execute without "file not found"
- [ ] `./scripts/core/ci-check.sh` passes
- [ ] `pytest tests/ -v` passes
- [ ] Pre-commit hooks pass
- [ ] `./scripts/core/project list` works
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Path references missed somewhere | Medium | Medium | Grep for `scripts/` (without `core/`) after migration |
| ASK `project` has ASK-specific behavior | Medium | High | Diff carefully; test `project list` and `project start` |
| `pattern_lint.py` flags existing code | Medium | Low | Run against codebase before committing |
| `ci-check.sh` has different lint steps | Low | Medium | Run full CI before committing |
| Bot reviews flag copied scripts | High | Low | Dismiss as "upstream sync" |
| Pre-commit hooks break | Low | High | Run `pre-commit run --all-files` before committing |

## Acceptance Criteria

- [ ] `scripts/core/` contains 12 scripts + VERSION file
- [ ] `scripts/local/` exists with `.gitkeep`
- [ ] `scripts/.core-manifest.json` exists and is valid JSON
- [ ] No scripts remain at `scripts/` root (except README.md)
- [ ] All 7 slash commands execute without "file not found" errors
- [ ] `./scripts/core/ci-check.sh` passes
- [ ] `pytest tests/ -v` passes (excluding pre-existing version test)
- [ ] `pre-commit run --all-files` passes
- [ ] `./scripts/core/project list` shows tasks correctly
- [ ] No references to old paths remain (`grep -r 'scripts/ci-check\|scripts/verify-ci\|scripts/check-bots\|scripts/project' .claude/ .pre-commit-config.yaml`)

## Follow-Up Tasks

After this PR merges:
1. **ASK-0001**: Restructure agentive-starter-kit `scripts/` to `core/` + `local/` + `optional/`
2. **ASK-0002**: Create `sync-core-scripts.yml` GitHub Action in agentive-starter-kit
3. **DK-XXXX**: Restructure dispatch-kit `scripts/` to match
4. **AEL-XXXX**: Restructure adversarial-evaluator-library `scripts/` to match
5. **ADV-XXXX**: Receive first automated sync PR, normalize to ASK-canonical versions
