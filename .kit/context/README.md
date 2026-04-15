# `.kit/context/` — Agent Coordination Directory

**Purpose**: Real-time agent coordination, project state, and accumulated knowledge.
**Last Updated**: 2026-04-15

---

## Directory Structure

```
.kit/context/
├── agent-handoffs.json       # Current agent status and task assignments
├── current-state.json        # Project state snapshot
├── patterns.yml              # Defensive coding patterns reference
├── REVIEW-INSIGHTS.md        # Distilled knowledge from code reviews (KIT-ADR-0019)
├── AGENT-SYSTEM-GUIDE.md     # Agent architecture reference
├── README.md                 # This file
├── archive/                  # Completed task artifacts (handoffs, review starters)
├── research/                 # Pre-implementation research and analysis
├── retros/                   # Session retrospectives (one per task)
├── reviews/                  # Code review reports and evaluator output
├── templates/                # Templates for reviews and review starters
└── workflows/                # Process documentation (commit, testing, review, etc.)
```

---

## Top-Level Convention

**The top level contains only live, long-lived files.** Task-specific artifacts
(handoffs, review starters, session state) are created here during active work
and **must be moved to `archive/` during post-completion**.

| File | Updated by | Purpose |
|------|-----------|---------|
| `agent-handoffs.json` | Planner | Who is doing what right now |
| `current-state.json` | Planner | Version, metrics, pending tasks |
| `patterns.yml` | Any agent | Defensive coding rules (DK001-DK004) |
| `REVIEW-INSIGHTS.md` | Planner | Reusable knowledge extracted from reviews |
| `AGENT-SYSTEM-GUIDE.md` | Planner | Agent roles and architecture |

**If a file has a task ID prefix (e.g., `ADV-0072-HANDOFF-*.md`) and the task
is done, it belongs in `archive/`.** The planner enforces this during the
post-completion step.

---

## Subdirectories

### `archive/`
Completed handoffs and review starters. Named `{TASK-ID}-HANDOFF-{agent}.md`
or `{TASK-ID}-REVIEW-STARTER.md`. Read-only after archival.

### `research/`
Pre-implementation analysis, design explorations, and sync plans.
Created during task planning, referenced during implementation.

### `retros/`
One file per completed task: `{TASK-ID}-retro.md`. Contains what worked,
what surprised, what should change, and process action items.

### `reviews/`
Code review reports and evaluator output: `{TASK-ID}-review.md` or
`{TASK-ID}-evaluator-review.md`. May have round suffixes (`-r2`, `-round2`).

### `templates/`
Reusable templates for review starters and reviews.

### `workflows/`
Process documentation: commit protocol, testing workflow, PR sizing,
coverage requirements, etc. Updated when processes change.

---

## Housekeeping Rules

1. **Post-completion**: Move all `{TASK-ID}-*` files from top level to `archive/`
2. **No orphans**: Every file at top level must be in the table above
3. **Date prefix**: One-off files use `YYYY-MM-DD-` prefix (then archive when stale)
4. **Reviews stay in `reviews/`**: They are reference material, not archived
5. **Retros stay in `retros/`**: They are reference material, not archived
