# ADV-0052: Restructure scripts/ to core/ + local/

**Status**: Todo
**Priority**: High
**Type**: Infrastructure
**Estimated Effort**: 2–3 hours (including reference updates across ~25 files and verification)
**Created**: 2026-03-08
**Updated**: 2026-03-09
**Depends On**: ~~ASK-0042~~ — completed in agentive-starter-kit v0.4.0
**Parent**: KIT-0024 (Core Scripts Standardization)

## Summary

Adopt the `scripts/core/` + `scripts/local/` + `scripts/optional/` layout
from agentive-starter-kit v0.4.0 in adversarial-workflow. Copy 14 core scripts (13 scripts + VERSION), update all references, and
unbreak the 6 broken slash commands (+ update the 1 working command's path).

**Upstream source**: `agentive-starter-kit` tag `v0.4.0` (core scripts v1.2.0)
**Migration guide**: `docs/UPGRADE-0.4.0.md` in agentive-starter-kit

## Current State

- 6 scripts in flat `scripts/` directory (should be 14)
- **6/7 slash commands are broken** — reference scripts that don't exist
- `ci-check.sh`, `verify-setup.sh`, `project`, `validate_task_status.py` are outdated
- Full analysis: `.agent-context/research/SCRIPTS-SYNC-ANALYSIS.md`

## Scope

### 1. Create directory structure

```
scripts/
  ├── core/                        ◀── 13 scripts + VERSION (14 files) from ASK v0.4.0
  │   ├── VERSION                  (contains "1.2.0")
  │   ├── __init__.py
  │   ├── project
  │   ├── ci-check.sh
  │   ├── verify-ci.sh
  │   ├── verify-setup.sh
  │   ├── check-bots.sh
  │   ├── wait-for-bots.sh
  │   ├── gh-review-helper.sh
  │   ├── preflight-check.sh
  │   ├── check-sync.sh           ◀── NEW: verifies core scripts match upstream
  │   ├── pattern_lint.py
  │   ├── validate_task_status.py
  │   └── logging_config.py
  ├── local/                       ◀── ADW-specific (currently empty)
  │   └── .gitkeep
  ├── optional/                    ◀── Opt-in scripts (copy from ASK if needed)
  │   └── .gitkeep
  ├── .core-manifest.json
  └── README.md
```

### 2. Copy core scripts from ASK v0.4.0

Use the existing local clone at `~/Github/agentive-starter-kit` (checkout
tag `v0.4.0`) and copy all 14 files from `scripts/core/` into
`scripts/core/`. If no local clone exists, do a shallow clone:

```bash
git clone --depth 1 --branch v0.4.0 https://github.com/movito/agentive-starter-kit.git /tmp/ask-v0.4.0
```

Copy `.core-manifest.json` from ASK `scripts/.core-manifest.json`.

**No interim approach needed** — ASK-0042 is complete.

### 3. Fix `project` script path resolution

The `project` script resolves repo root via `Path(__file__).resolve()`.
After moving from `scripts/project` to `scripts/core/project`, it needs
one extra `.parent`:

```python
# Before (scripts/project):
project_dir = Path(__file__).resolve().parent.parent

# After (scripts/core/project):
project_dir = Path(__file__).resolve().parent.parent.parent
```

Two occurrences: `cmd_setup()` and `main()`. Both must be updated.

### 4. Remove old scripts from root

Delete from `scripts/` root: `ci-check.sh`, `logging_config.py`,
`validate_task_status.py`, `verify-setup.sh`, `project`, `__pycache__/`.

**Before deleting anything**, verify no Python imports reference `scripts/`
as a package:

```bash
grep -rn 'import scripts\.' --include='*.py' src/ tests/
grep -rn 'from scripts' --include='*.py' src/ tests/
```

If zero results: also delete `scripts/__init__.py` — the root `scripts/`
directory is no longer a Python package (only `scripts/core/` is).
If results found: update those imports to use `scripts.core.xxx` first.

### 5. Update all references

Files that need `./scripts/<name>` → `./scripts/core/<name>`:

| Location | Files | Count |
|----------|-------|-------|
| `.claude/commands/*.md` | check-ci, check-bots, wait-for-bots, triage-threads, preflight, commit-push-pr, start-task | 7 |
| `.claude/agents/*.md` | feature-developer, feature-developer-v3, code-reviewer, test-runner, security-reviewer, agent-creator, document-reviewer, planner, planner2, AGENT-TEMPLATE, TASK-STARTER-TEMPLATE | 11 |
| `.pre-commit-config.yaml` | pattern_lint.py path (if referenced) | 1 |
| `.agent-context/workflows/*.md` | script references | ~3 |
| `CLAUDE.md` | script paths in tables | 1 |
| `tests/` | import paths, `_script_path` definitions, mock `.parent` chains | ~2 |

**Verification grep** (run after all updates):
```bash
grep -rn 'scripts/project\b\|scripts/ci-check\|scripts/verify-\|scripts/pattern_lint\|scripts/check-bots\|scripts/wait-for\|scripts/gh-review\|scripts/preflight' \
  --include='*.md' --include='*.yml' --include='*.yaml' --include='*.py' --include='*.sh' --include='*.toml' \
  | grep -v 'scripts/core/' | grep -v 'scripts/optional/' | grep -v 'scripts/local/' | grep -v '.git/'
```

### 6. Update test mocks

```python
# Before:
mock_path.return_value.resolve.return_value.parent.parent = mock_project_dir

# After:
mock_path.return_value.resolve.return_value.parent.parent.parent = mock_project_dir
```

### 7. Verify

- All 7 slash commands execute without "file not found" errors
- `./scripts/core/ci-check.sh` passes
- `./scripts/core/project list` works
- `./scripts/core/check-sync.sh` reports sync status
- `pytest tests/ -v` passes (excluding pre-existing version test)
- `pre-commit run --all-files` passes — if DK002 lint rule flags existing
  code with `open()` without `encoding=`, those failures are **not blocking**
  for this task. Log them for a follow-up task but do not fix here
- No Python `import scripts.xxx` references remain (or all updated to `scripts.core.xxx`)

## Acceptance Criteria

- [ ] `scripts/core/` contains 14 files (13 scripts + VERSION)
- [ ] `scripts/local/` exists with `.gitkeep`
- [ ] `scripts/optional/` exists with `.gitkeep`
- [ ] `scripts/.core-manifest.json` exists and is valid JSON
- [ ] No scripts at `scripts/` root (except README.md)
- [ ] All 7 slash commands work (no "file not found")
- [ ] `./scripts/core/project list` shows tasks correctly
- [ ] CI passes
- [ ] Pre-commit hooks pass
- [ ] Verification grep returns zero results
- [ ] No `import scripts.xxx` / `from scripts` references remain (or updated)

## Known Pitfalls (from ASK migration guide)

1. **`project` path resolution** — must add extra `.parent` in two places (Step 3)
2. **Test mock chains** — `.parent.parent` → `.parent.parent.parent` (Step 6)
3. **`ci-check.sh` internal paths** — uses `$SCRIPT_DIR` which auto-resolves correctly
4. **DK002 lint rule** — new rule flags `open()` without `encoding=`. **Out of scope** for this task — address in a follow-up if `pattern_lint.py` flags existing code
5. **Non-core script references** — `start-daemons.sh` and `test-critical.sh` are referenced in agent files but don't exist. **Decision**: remove these references (they are aspirational, not implemented). Do NOT create placeholder scripts. Run a broader grep for any `./scripts/` references that aren't covered by the core/local/optional migration to catch other orphaned references (e.g., `create-agent.sh` is referenced in `agent-creator.md` under `.agent-context/scripts/` — unrelated path, leave as-is)
6. **`check-sync.sh` operation** — compares local `scripts/core/` against upstream by reading `.core-manifest.json` and checking file checksums. Requires either `ASK_REPO` env var pointing to a local ASK clone, or falls back to GitHub API. Informational only — does not modify files

## Notes

- Detailed research: `.agent-context/research/ADW-UPGRADE-PLAN.md`
- Cross-project analysis: `.agent-context/research/SCRIPTS-SYNC-ANALYSIS.md`
- Architecture design: `.agent-context/research/CORE-SCRIPTS-DESIGN.md`
- ASK migration guide: `docs/UPGRADE-0.4.0.md` in agentive-starter-kit repo
