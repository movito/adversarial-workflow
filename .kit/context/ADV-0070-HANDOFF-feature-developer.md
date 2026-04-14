# ADV-0070 Handoff: Docs Folder Cleanup

**Task**: `.kit/tasks/2-todo/ADV-0070-docs-folder-cleanup.md`
**Agent**: feature-developer-v5
**Evaluation**: APPROVED (arch-review-fast)

## Mission

Consolidate `docs/` from 9 subdirectories to 4 (`adr/`, `archive/`, `guides/`, `reference/`). This is a file-move + path-update task — no new code.

## Critical Context

### What Moves Where

The task spec has the full table, but the key structural change is:

```
docs/decisions/adr/  →  docs/adr/       (flatten the decisions/ nesting)
docs/decisions/archive/ + docs/internal/ + docs/project-history/ + docs/proposals/ + docs/roadmap/
                     →  docs/archive/    (consolidate all historical content)
docs/examples/athena.yml  →  docs/reference/athena.yml
docs/CUSTOM_EVALUATORS.md →  docs/guides/CUSTOM-EVALUATORS.md
```

### Delete First

```bash
git rm "docs/proposals/ADVERSARIAL-WORKFLOW-ENV-LOADING copy.md"
```

The duplicate has a space + "copy" in the filename. Delete it BEFORE moving `docs/proposals/` to archive.

### Path References (~12 active files)

Bulk replace `docs/decisions/adr/` → `docs/adr/` in these files:

| File | What to update |
|------|----------------|
| `.claude/agents/planner.md` | ADR links |
| `.claude/agents/planner2.md` | ADR links |
| `.claude/agents/code-reviewer.md` | ADR links |
| `.claude/agents/feature-developer.md` | ADR links |
| `.claude/agents/powertest-runner.md` | ADR links |
| `.kit/templates/AGENT-TEMPLATE.md` | ADR path template |
| `.kit/templates/OPERATIONAL-RULES.md` | ADR path |
| `.kit/context/workflows/ADR-CREATION-WORKFLOW.md` | ADR directory reference |
| `.kit/context/workflows/AGENT-CREATION-WORKFLOW.md` | ADR path |
| `.kit/context/workflows/PR-SIZE-WORKFLOW.md` | ADR path |
| `.adversarial/docs/EVALUATION-WORKFLOW.md` | ADR link |
| `docs/reference/TERMINOLOGY.md` | ADR link |

**Leave historical refs alone** — anything in `.kit/tasks/5-done/`, `.kit/tasks/8-archive/`, `.kit/context/retros/`, `.kit/context/archive/`, or `docs/archive/` itself.

### docs/README.md Rewrite

The current `docs/README.md` indexes 9 directories. Rewrite it to reflect the 4-folder target structure with correct relative links.

### docs/adr/README.md

After moving, update any self-referential path from `docs/decisions/adr/` to `docs/adr/`.

## What NOT To Do

1. **Don't touch consumer-facing paths** — `adversarial_workflow/cli.py` references to `delegation/tasks/` are for `adversarial init` (consumer projects), not this repo.
2. **Don't update historical files** — done tasks, retros, archive content should keep their original references.
3. **Don't use `git add -A`** — stage files explicitly by category (lesson from ADV-0068).

## Verification

```bash
# After all moves:
pytest tests/ -v
pre-commit run --all-files
./scripts/core/ci-check.sh

# Stale reference check (active files only):
grep -r 'docs/decisions/' --include='*.md' . \
  | grep -v '.git/' | grep -v '.kit/tasks/5-done' | grep -v '.kit/tasks/8-archive' \
  | grep -v '.kit/context/retros' | grep -v '.kit/context/archive' | grep -v 'docs/archive/'
# Should return 0 results
```

## Preflight Type

This is a `--type docs` task (no new code, no tests to write). Use:

```bash
./scripts/core/project start ADV-0070
git checkout -b feature/ADV-0070-docs-folder-cleanup
```

## Evaluation Notes

- **arch-review-fast**: APPROVED
- Single finding: consider formalizing docs/ structure guidelines to prevent future drift → nice-to-have, not blocking
