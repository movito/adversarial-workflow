# ADV-0069 Handoff: Root Declutter + Manifest Upgrade

**Task**: `.kit/tasks/2-todo/ADV-0069-root-declutter-manifest-upgrade.md`
**Agent**: feature-developer-v5
**Created**: 2026-04-14

## Mission

Two housekeeping items, one atomic PR:
1. Upgrade `scripts/.core-manifest.json` from v1.2.0 (flat) to v2.0.0 (tiered)
2. Declutter the repo root: delete stale files, move docs to `docs/guides/`, archive audit results

## Critical Context

1. **Manifest upgrade guide**: `~/Github/agentive-starter-kit/docs/MANIFEST-UPGRADE-GUIDE.md` —
   follow this step by step. Cross-reference the upstream manifest to ensure file lists match.

2. **Upstream manifest for reference**: `~/Github/agentive-starter-kit/scripts/.core-manifest.json` —
   this is the canonical source. Our manifest should mirror its `files` structure with the same
   tier names and file lists, adjusted for any files we don't have.

3. **We are a kit repo** — `opted_in` should include both `commands_optional` and `kit_builder`.

4. **`adversarial_workflow/cli.py` is OUT OF SCOPE** — do NOT change any Python source code.
   The CLI references some of these docs (SETUP.md, QUICK_START.md) in user-facing output.
   That's a separate concern.

5. **`README.md` link updates are critical** — the README links to QUICK_START.md, SETUP.md,
   UPGRADE.md, and AGENT_INTEGRATION.md. All those links must update to `docs/guides/` paths.

6. **Historical references are OK** — done tasks, retros, changelogs describe the past. Don't
   rewrite them.

## Step-by-Step

### 1. Create branch
```bash
git checkout -b feature/ADV-0069-root-declutter
./scripts/core/project start ADV-0069
```

### 2. Manifest upgrade
```bash
# Read upstream manifest for reference
cat ~/Github/agentive-starter-kit/scripts/.core-manifest.json

# Replace our manifest with v2.0.0 tiered format
# See task spec Phase 1 for target JSON
```

### 3. Delete stale files
```bash
git rm setup.py
git rm EVALUATOR-QA-RESPONSE.txt
git rm tasks/review-task-setup-005.md
```

### 4. Move docs
```bash
mkdir -p docs/guides
git mv AGENT_INTEGRATION.md docs/guides/AGENT-INTEGRATION.md
git mv QUICK_START.md docs/guides/QUICK-START.md
git mv SETUP.md docs/guides/SETUP.md
git mv UPGRADE.md docs/guides/UPGRADE.md
```

### 5. Move audit archive
```bash
mkdir -p .kit/context/archive/audit-results
git mv audit-results/* .kit/context/archive/audit-results/
```

### 6. Update references
```bash
# Find all references to moved/deleted files
grep -rn 'QUICK_START\|AGENT_INTEGRATION\|SETUP\.md\|UPGRADE\.md\|EVALUATOR-QA\|setup\.py' \
  --include='*.md' . | grep -v '.git/' | grep -v '.kit/tasks/5-done' | grep -v '.kit/tasks/8-archive' | grep -v '.kit/context/retros'

# Key file: README.md — update all doc links
# Also check: CLAUDE.md, docs/guides/*.md (cross-references within moved docs)
```

### 7. Verify
```bash
# Manifest validates
python3 -c "
import json
with open('scripts/.core-manifest.json') as f:
    m = json.load(f)
assert isinstance(m['files'], dict)
print(f'v{m[\"core_version\"]} — {sum(len(v) for v in m[\"files\"].values())} files across {len(m[\"files\"])} tiers')
print(f'Opted in: {m.get(\"opted_in\", [])}')
"

pytest tests/ -v
pre-commit run --all-files
./scripts/core/ci-check.sh
```

## What NOT to Touch

- `adversarial_workflow/*.py` — CLI source code
- `adversarial_workflow/templates/` — consumer scaffolding templates
- `tests/*.py` — no test changes needed
- Historical content in `.kit/tasks/5-done/`, `.kit/context/retros/`, `CHANGELOG.md`
- `LICENSE` — stays at root (standard)
- `uv.lock` — stays at root (lock file)

## Evaluation Result

**Verdict**: REVISION_SUGGESTED (cosmetic — clarify inline manifest is reference, not canonical)
**Log**: `.adversarial/logs/ADV-0069-root-declutter-manifest-upgrade--arch-review-fast.md`
**Assessment**: Effectively approved. Finding is about labeling the inline JSON example.
