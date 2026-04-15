# Task Completion Protocol

**Purpose**: Standard process for completing implementation tasks
**Agents**: Planner (post-completion), feature-developer (handoff creation)
**Last Updated**: 2026-04-15

---

## When to Use

- After PR is merged and task is done
- Before marking task as complete in `.kit/tasks/5-done/`

---

## Feature-Developer Checklist (Before Merge)

1. ✅ All acceptance criteria met
2. ✅ All tests passing (no regressions)
3. ✅ CI/CD green on GitHub
4. ✅ Bot reviews addressed (CodeRabbit, BugBot)
5. ✅ Evaluator review run and findings dispositioned
6. ✅ Review starter created at `.kit/context/{TASK-ID}-REVIEW-STARTER.md`
7. ✅ Retro written at `.kit/context/retros/{TASK-ID}-retro.md`
8. ✅ Task moved to `4-in-review/`

---

## Planner Post-Completion Checklist (After Merge)

1. ✅ Move task to `5-done/`: `./scripts/core/project complete {TASK-ID}`
2. ✅ Update `agent-handoffs.json` — agent status, recent_completions, pending_tasks
3. ✅ Extract review insights → append to `REVIEW-INSIGHTS.md` (KIT-ADR-0019)
4. ✅ **Archive task artifacts** — move from `.kit/context/` top level to `archive/`:
   ```bash
   git mv .kit/context/{TASK-ID}-HANDOFF-*.md .kit/context/archive/
   git mv .kit/context/{TASK-ID}-REVIEW-STARTER.md .kit/context/archive/
   ```
5. ✅ Update `current-state.json` if project state changed (version, metrics)
6. ✅ Commit all post-completion changes to main
7. ✅ Verify CI passes on main

**Rule**: No task-specific files (`{TASK-ID}-*`) should remain at `.kit/context/`
top level after post-completion. See `.kit/context/README.md` for the top-level
convention.

---

## Handoff Document Format

### Filename
```
.kit/context/{TASK-ID}-HANDOFF-{agent-type}.md
```

### Required Sections

```markdown
## Task Summary
Brief description of the task and its purpose

## Implementation Guidance
Detailed technical guidance for the implementing agent

## Acceptance Criteria
Checkboxes from the task spec

## Key Files
- path/to/file.py — what to modify and why

## Notes
Evaluation history, dependencies, edge cases
```

---

## Review Starter Format

### Filename
```
.kit/context/{TASK-ID}-REVIEW-STARTER.md
```

### Required Sections

See template: `.kit/context/templates/review-starter-template.md`

---

## Related Workflows

- [TESTING-WORKFLOW.md](./TESTING-WORKFLOW.md) — verify tests before completion
- [COMMIT-PROTOCOL.md](./COMMIT-PROTOCOL.md) — commit changes properly
- [COVERAGE-WORKFLOW.md](./COVERAGE-WORKFLOW.md) — coverage requirements
- [Evaluation Workflow](../../.adversarial/docs/EVALUATION-WORKFLOW.md) — pre-assignment evaluation
