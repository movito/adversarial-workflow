# ADV-0068 Handoff: Migrate to .kit/ Directory Layout

**Task**: `delegation/tasks/2-todo/ADV-0068-kit-migration.md`
**Agent**: feature-developer-v5
**Created**: 2026-04-13

## Mission

Move builder infrastructure (`.agent-context/`, `delegation/`, `agents/` launchers, builder
templates) into a `.kit/` directory, then update all path references. Single atomic PR.

## Critical Context

1. **Reference project already migrated**: `~/Github/adversarial-evaluator-library` — look at its
   `.kit/` structure, `.claude/agents/`, and `scripts/core/` for the target state.

2. **`.adversarial/` stays at root** — the `adversarial` CLI hardcodes this path. Only update
   `task_directory` in `.adversarial/config.yml` from `delegation/tasks/` to `.kit/tasks/`.

3. **`adversarial_workflow/cli.py` is OUT OF SCOPE** — do NOT change any Python source code in
   `adversarial_workflow/`. The CLI's `init`/`health`/`reconfigure` commands reference
   `.agent-context/` and `delegation/` for consumer project scaffolding. Those stay as-is.

4. **`scripts/core/project` is THE critical file** — it's a large Python script (~1200 lines) with
   ~6 hardcoded `delegation/tasks` references and `~3 .agent-context` references. This drives all
   task management (`start`, `move`, `complete`, `list`). Every reference must update.

5. **`scripts/core/validate_task_status.py`** — line 105 has `"delegation/tasks/"` string that must
   become `".kit/tasks/"`.

6. **Historical references are OK** — files in `retros/`, `5-done/`, `8-archive/`, `CHANGELOG.md`
   describe the past. Don't rewrite history.

## Step-by-Step

### 1. Create branch
```bash
git checkout -b feature/ADV-0068-kit-migration
./scripts/core/project start ADV-0068
```

### 2. Create skeleton
```bash
mkdir -p .kit/{adr,context/{reviews,retros,templates,workflows,archive,research},docs,launchers,skills,tasks/{1-backlog,2-todo,3-in-progress,4-in-review,5-done,6-canceled,7-blocked,8-archive,9-reference/templates},templates}
```

### 3. Move files (git mv)

Move in this order:
1. `.agent-context/` subdirectories → `.kit/context/` subdirectories
2. `.agent-context/` root files → `.kit/context/`
3. `delegation/tasks/` → `.kit/tasks/`
4. `delegation/handoffs/` → `.kit/context/archive/`
5. `agents/{launch,onboarding,preflight}` → `.kit/launchers/`
6. `.claude/agents/{AGENT-TEMPLATE,OPERATIONAL-RULES,TASK-STARTER-TEMPLATE}.md` → `.kit/templates/`
7. Remove empty `delegation/`, `.agent-context/`, `agents/`

### 4. Bulk path rewrites

Use sed (or Python script) to replace paths. Order: most specific first.

Target files: `.claude/agents/*.md`, `.claude/commands/*.md`, `.claude/skills/*/SKILL.md`,
`scripts/core/project`, `scripts/core/validate_task_status.py`, `scripts/core/preflight-check.sh`,
`.adversarial/config.yml`, `.pre-commit-config.yaml`, `CLAUDE.md`, `README.md`, `QUICK_START.md`,
`SETUP.md`, `AGENT_INTEGRATION.md`, `docs/**/*.md`

**Do NOT edit**: `adversarial_workflow/*.py`, `tests/*.py`, files in `.kit/context/archive/`,
files in `.kit/tasks/5-done/`, files in `.kit/tasks/8-archive/`, `.kit/context/retros/`

### 5. Manual edits

- **`CLAUDE.md`**: Rewrite the directory structure section to show `.kit/` layout
- **`scripts/core/project`**: Verify each path reference individually
- **`.pre-commit-config.yaml`**: Update task status hook file pattern

### 6. Verify

```bash
pytest tests/ -v
pre-commit run --all-files
adversarial list-evaluators
./scripts/core/project list
./scripts/core/ci-check.sh
# Grep for stale references:
grep -r 'delegation/tasks\|\.agent-context' --include='*.md' --include='*.py' --include='*.sh' --include='*.yml' . | grep -v '.git/' | grep -v '.kit/' | grep -v 'adversarial_workflow/' | grep -v archive | grep -v retro | grep -v 5-done | grep -v 8-archive
```

## Key Files

| File | Why It Matters |
|------|----------------|
| `scripts/core/project` | Task management — lines 67, 130, 150, 252-257, 1062 |
| `scripts/core/validate_task_status.py` | Pre-commit hook — line 105 |
| `.adversarial/config.yml` | `task_directory` setting |
| `CLAUDE.md` | Directory structure section |
| `.pre-commit-config.yaml` | Hook file patterns |
| `.claude/agents/planner2.md` | Most path references of any agent |

## What NOT to Touch

- `adversarial_workflow/*.py` — CLI source code (consumer-facing)
- `adversarial_workflow/templates/` — Consumer project scaffolding
- `tests/*.py` — Tests test the CLI, not our project layout
- `.adversarial/` directory itself — only edit config.yml's task_directory
- `.serena/` — Serena config
- Historical content in done/archive/retro files

## Evaluation Result

**Verdict**: APPROVED (arch-review-fast, 2026-04-13)
**Log**: `.adversarial/logs/ADV-0068-kit-migration--arch-review-fast.md`
