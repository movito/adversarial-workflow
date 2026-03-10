# Scripts Directory

Scripts are organized into three tiers following the agentive-starter-kit convention.

## Directory Structure

```
scripts/
  core/          # Synced from agentive-starter-kit (DO NOT edit directly)
  local/         # Project-specific scripts (not synced)
  optional/      # Opt-in scripts copied from ASK as needed
  .core-manifest.json   # Tracks core script versions and sync state
```

## Core Scripts (`scripts/core/`)

These scripts are synced from [agentive-starter-kit](https://github.com/movito/agentive-starter-kit).
Do NOT edit them directly -- changes will be overwritten on next sync.
To check sync status: `./scripts/core/check-sync.sh`

| Script | Purpose |
|--------|---------|
| `project` | Task lifecycle CLI (start, move, complete, list) |
| `ci-check.sh` | Local CI: lint + format + tests |
| `verify-ci.sh` | Check GitHub Actions CI status |
| `verify-setup.sh` | Verify project setup (Python, venv, deps) |
| `check-bots.sh` | Check bot review status on PRs |
| `wait-for-bots.sh` | Wait for bot reviews to complete |
| `gh-review-helper.sh` | PR review thread management |
| `preflight-check.sh` | Pre-merge preflight checks |
| `check-sync.sh` | Verify core scripts match upstream |
| `pattern_lint.py` | Defensive coding pattern linter |
| `validate_task_status.py` | Task file status validation |
| `logging_config.py` | Shared logging configuration |
| `VERSION` | Core scripts version (1.2.0) |

## Local Scripts (`scripts/local/`)

Project-specific scripts that are NOT synced from upstream. Add new scripts here.

## Optional Scripts (`scripts/optional/`)

Opt-in scripts from agentive-starter-kit. Copy from ASK when needed.

## Sync Status

Current core version: **1.2.0** (from agentive-starter-kit v0.4.0)

Run `./scripts/core/check-sync.sh` to verify scripts match upstream.
