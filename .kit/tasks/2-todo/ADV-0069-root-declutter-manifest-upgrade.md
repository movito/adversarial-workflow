# ADV-0069: Root Declutter + Manifest Upgrade to v2.0.0

**Status**: Todo
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 2-3 hours
**Created**: 2026-04-14

## Related Tasks

**Depends On**: ADV-0068 (.kit/ migration — DONE, PR #64)
**Related**: KIT-ADR-0022 (Manifest-Based Sync Ownership)
**Related**: ADR-0008 (Tiered Manifest for Cross-Repo Sync)
**Blocks**: Future upstream sync (sync expects v2.0.0 manifest)

## Overview

Two related housekeeping items in a single atomic PR:

1. **Manifest upgrade**: Replace `scripts/.core-manifest.json` from flat v1.2.0 format to
   tiered v2.0.0 format per ADR-0008. We're a kit repo, so we opt into everything.

2. **Root declutter**: Remove stale files and move user-facing docs from root into `docs/guides/`,
   bringing the root from 15 committed files + 3 stale directories down to 9 files — matching
   the cleanliness of agentive-starter-kit.

**Context**: After ADV-0068 moved builder infrastructure into `.kit/`, the root still has
accumulated debris: a stub `setup.py`, an ancient Aider QA transcript, orphan task files,
and four user docs that belong in `docs/guides/`. The manifest is on v1.2.0 (flat, scripts-only)
while upstream has moved to v2.0.0 (tiered, with commands and builder infrastructure tracking).

**Reference**:
- Upgrade guide: `~/Github/agentive-starter-kit/docs/MANIFEST-UPGRADE-GUIDE.md`
- ADR: `~/Github/agentive-starter-kit/docs/adr/ADR-0008-tiered-manifest-sync.md`
- Target root: compare with `~/Github/agentive-starter-kit/` root

## Requirements

### Part A: Manifest Upgrade

1. Replace `scripts/.core-manifest.json` with v2.0.0 tiered format
2. Tiers: `scripts_core`, `commands_core`, `commands_optional`, `kit_builder`
3. `opted_in`: `["commands_optional", "kit_builder"]` (we are a kit repo)
4. Remove legacy `source` field (v1.x artifact, `source_repo` is the v2 equivalent)
5. Verify manifest parses correctly (validation script in upgrade guide)

### Part B: Root Declutter

#### Delete (4 items)

| File | Reason |
|------|--------|
| `setup.py` | Stub — `pyproject.toml` handles everything via PEP 621 |
| `EVALUATOR-QA-RESPONSE.txt` | Aider session log from Oct 2025, no ongoing value |
| `tasks/review-task-setup-005.md` | Orphan task file from pre-.kit era |
| `tasks/` directory | Empty after file removal |

#### Move docs to `docs/guides/` (4 items, `git mv`)

| Source | Destination |
|--------|-------------|
| `AGENT_INTEGRATION.md` | `docs/guides/AGENT-INTEGRATION.md` |
| `QUICK_START.md` | `docs/guides/QUICK-START.md` |
| `SETUP.md` | `docs/guides/SETUP.md` |
| `UPGRADE.md` | `docs/guides/UPGRADE.md` |

#### Move audit archive to `.kit/` (1 directory, `git mv`)

| Source | Destination |
|--------|-------------|
| `audit-results/` (4 files) | `.kit/context/archive/audit-results/` |

#### Update links

- `README.md` — update any links to moved docs (e.g., `QUICK_START.md` → `docs/guides/QUICK-START.md`)
- `CLAUDE.md` — update if it references any moved files
- Any other files that reference the moved docs by path

### Target Root (After)

```
.gitignore
.pre-commit-config.yaml
CHANGELOG.md
CLAUDE.md
LICENSE
README.md
conftest.py
pyproject.toml
uv.lock
```

9 committed files. Directories: `adversarial_workflow/`, `docs/`, `scripts/`, `tests/`, plus dotdirs.

## Implementation Plan

### Phase 1: Manifest Upgrade

1. Read current manifest: `cat scripts/.core-manifest.json`
2. Replace with v2.0.0 format (see template below)
3. Verify: run validation script from upgrade guide

**Target manifest**:

```json
{
  "core_version": "2.0.0",
  "source_repo": "movito/agentive-starter-kit",
  "synced_at": "2026-04-14T00:00:00Z",
  "files": {
    "scripts_core": [
      "core/__init__.py",
      "core/check-bots.sh",
      "core/check-sync.sh",
      "core/ci-check.sh",
      "core/gh-review-helper.sh",
      "core/logging_config.py",
      "core/pattern_lint.py",
      "core/preflight-check.sh",
      "core/project",
      "core/validate_task_status.py",
      "core/verify-ci.sh",
      "core/verify-setup.sh",
      "core/wait-for-bots.sh",
      "core/VERSION"
    ],
    "commands_core": [
      "check-ci.md",
      "check-bots.md",
      "wait-for-bots.md",
      "start-task.md",
      "commit-push-pr.md",
      "preflight.md"
    ],
    "commands_optional": [
      "babysit-pr.md",
      "retro.md",
      "triage-threads.md",
      "status.md",
      "check-spec.md",
      "wrap-up.md"
    ],
    "kit_builder": [
      ".kit/templates/",
      ".kit/launchers/",
      ".kit/adr/",
      ".kit/docs/",
      ".adversarial/config.yml.template",
      ".adversarial/scripts/",
      ".adversarial/docs/",
      ".kit/context/workflows/",
      ".kit/context/templates/",
      ".kit/context/patterns.yml"
    ]
  },
  "opted_in": ["commands_optional", "kit_builder"]
}
```

**Note**: Cross-reference with upstream's manifest to ensure file lists match. The `wrap-up.md`
command may need adding to `commands_optional` if upstream has it. Check upstream's current
`.core-manifest.json` or the MANIFEST-UPGRADE-GUIDE for the canonical file list.

### Phase 2: Delete Stale Files

```bash
git rm setup.py
git rm EVALUATOR-QA-RESPONSE.txt
git rm tasks/review-task-setup-005.md
# tasks/ directory auto-removed when empty
```

### Phase 3: Move Docs

```bash
# Ensure target exists
mkdir -p docs/guides

git mv AGENT_INTEGRATION.md docs/guides/AGENT-INTEGRATION.md
git mv QUICK_START.md docs/guides/QUICK-START.md
git mv SETUP.md docs/guides/SETUP.md
git mv UPGRADE.md docs/guides/UPGRADE.md
```

### Phase 4: Move Audit Archive

```bash
mkdir -p .kit/context/archive/audit-results
git mv audit-results/* .kit/context/archive/audit-results/
# audit-results/ directory auto-removed when empty
```

### Phase 5: Update References

Search for links to moved/deleted files and update them:

```bash
# Find references to moved docs
grep -r 'AGENT_INTEGRATION\|QUICK_START\|SETUP\.md\|UPGRADE\.md' \
  --include='*.md' --include='*.py' --include='*.yml' . \
  | grep -v '.git/' | grep -v '.kit/tasks/5-done' | grep -v '.kit/tasks/8-archive'

# Find references to deleted files
grep -r 'setup\.py\|EVALUATOR-QA-RESPONSE\|tasks/review-task' \
  --include='*.md' . | grep -v '.git/'

# Find references to audit-results
grep -r 'audit-results' --include='*.md' . | grep -v '.git/'
```

Key files to update:
- `README.md` — likely links to QUICK_START.md, SETUP.md, UPGRADE.md
- `CLAUDE.md` — may reference some of these
- `docs/guides/*.md` — cross-references between moved docs

### Phase 6: Verify

```bash
# Manifest validates
python3 -c "
import json
with open('scripts/.core-manifest.json') as f:
    m = json.load(f)
assert isinstance(m['files'], dict), 'files should be a dict'
assert 'scripts_core' in m['files']
assert 'commands_core' in m['files']
print(f'v{m[\"core_version\"]} — {sum(len(v) for v in m[\"files\"].values())} files across {len(m[\"files\"])} tiers')
print(f'Opted in: {m.get(\"opted_in\", [])}')
"

# Tests pass
pytest tests/ -v

# Pre-commit hooks pass
pre-commit run --all-files

# Local CI
./scripts/core/ci-check.sh

# No broken links (spot check)
grep -r 'QUICK_START\.md\|SETUP\.md\b' README.md
# Should find docs/guides/ paths, not root paths
```

## TDD Workflow

No new code — this is file moves, deletes, and a config file rewrite. Existing test suite
serves as regression gate.

### Test Requirements
- [ ] All existing tests pass (no source code changes)
- [ ] Pre-commit hooks pass
- [ ] Manifest validation script passes
- [ ] Coverage: N/A (no new code)

## Acceptance Criteria

### Must Have
- [ ] `scripts/.core-manifest.json` at v2.0.0 with tiered format
- [ ] `opted_in` includes `commands_optional` and `kit_builder`
- [ ] `setup.py` deleted
- [ ] `EVALUATOR-QA-RESPONSE.txt` deleted
- [ ] `tasks/` directory removed
- [ ] `AGENT_INTEGRATION.md` → `docs/guides/AGENT-INTEGRATION.md`
- [ ] `QUICK_START.md` → `docs/guides/QUICK-START.md`
- [ ] `SETUP.md` → `docs/guides/SETUP.md`
- [ ] `UPGRADE.md` → `docs/guides/UPGRADE.md`
- [ ] `audit-results/` → `.kit/context/archive/audit-results/`
- [ ] `README.md` links updated to new doc locations
- [ ] All tests pass
- [ ] Single atomic PR

### Should Have
- [ ] Git history preserved via `git mv` for moved docs
- [ ] No stale references to deleted/moved files in active files
- [ ] Historical references in done tasks / retros left as-is
- [ ] `CLAUDE.md` updated if it references any moved files

## Success Metrics

### Quantitative
- Root committed files: 15 → 9
- Root committed directories: 3 stale removed (`tasks/`, `audit-results/`, empty after moves)
- Manifest version: 1.2.0 → 2.0.0
- Test pass rate: 100%

### Qualitative
- Root matches agentive-starter-kit cleanliness
- Manifest ready for future upstream sync

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| Manifest upgrade | 15 min | [ ] |
| Delete stale files | 10 min | [ ] |
| Move docs + archive | 15 min | [ ] |
| Update references | 30 min | [ ] |
| Verify + CI | 30 min | [ ] |
| Bot review rounds | 1 hour | [ ] |
| **Total** | **~2.5 hours** | [ ] |

## References

- **Manifest upgrade guide**: `~/Github/agentive-starter-kit/docs/MANIFEST-UPGRADE-GUIDE.md`
- **ADR-0008**: `~/Github/agentive-starter-kit/docs/adr/ADR-0008-tiered-manifest-sync.md`
- **Reference root**: `~/Github/agentive-starter-kit/` (target cleanliness)
- **Testing**: `pytest tests/ -v`
- **Pre-commit**: `pre-commit run --all-files`
- **Local CI**: `./scripts/core/ci-check.sh`

---

**Template Version**: 2.0.0
**Project**: adversarial-workflow
**Last Updated**: 2026-04-14
