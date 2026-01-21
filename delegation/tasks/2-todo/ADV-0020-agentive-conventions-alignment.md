# ADV-0020: Align with Agentive Starter Kit Conventions

**Status**: Todo
**Priority**: High
**Estimated Effort**: 2-3 hours
**Created**: 2026-01-22

## Summary

The adversarial-workflow project has diverged from agentive-starter-kit conventions, causing:
- Handoff files mixed with task specs in `delegation/tasks/`
- Missing `./scripts/project` CLI for task management
- Stale state files (`current-state.json` shows v0.4.0, actual is v0.5.0)
- Planner agent missing key protocols (Task Starter, Code Review, CI verification)

This task realigns the project with established conventions.

## Background

**Current State Analysis** (2026-01-22):

| Issue | Current | Target |
|-------|---------|--------|
| Planner agent | 149 lines (minimal) | ~400+ lines with protocols |
| Handoff files | In `delegation/tasks/*/` | `.agent-context/` |
| Review starters | In `delegation/tasks/*/` | `.agent-context/` |
| `scripts/project` | Missing | Task lifecycle CLI |
| `current-state.json` | v0.4.0, dated 2025-11-28 | v0.5.0, current |
| `agent-handoffs.json` | All "idle", stale | Reflects actual state |

**Files to Relocate**:
```
delegation/tasks/2-todo/ADV-0017-STARTER.md → .agent-context/ADV-0017-HANDOFF-feature-developer.md
delegation/tasks/5-done/ADV-0016-STARTER.md → .agent-context/archive/ADV-0016-HANDOFF-feature-developer.md
delegation/tasks/5-done/ADV-0016-REVIEW-STARTER.md → .agent-context/archive/ADV-0016-REVIEW-STARTER.md
delegation/tasks/5-done/ADV-0015-STARTER.md → .agent-context/archive/ADV-0015-HANDOFF-feature-developer.md
delegation/tasks/5-done/ADV-0015-REVIEW-STARTER.md → .agent-context/archive/ADV-0015-REVIEW-STARTER.md
delegation/tasks/5-done/ADV-0014-STARTER.md → .agent-context/archive/ADV-0014-HANDOFF-feature-developer.md
delegation/tasks/5-done/ADV-0014-REVIEW-STARTER.md → .agent-context/archive/ADV-0014-REVIEW-STARTER.md
```

## Requirements

### Phase 1: File Reorganization

1. **Create `.agent-context/archive/`** for completed task handoffs
2. **Move misplaced files** from task folders to `.agent-context/`
3. **Rename files** to follow convention: `*-STARTER.md` → `*-HANDOFF-feature-developer.md`
4. **Update `current-state.json`** with accurate version and date
5. **Update `agent-handoffs.json`** to reflect actual state

### Phase 2: Planner Agent Update

Update `.claude/agents/planner.md` to include:

1. **Task Starter Protocol** - Where handoffs go, naming conventions
2. **Code Review Workflow** - Review process, verdict handling
3. **Task Lifecycle Commands** - Document manual process (no scripts/project yet)
4. **CI Verification** - How to verify CI passes

### Phase 3: Infrastructure (Optional, Future)

Consider adding later:
- `scripts/project` CLI (port from thematic-2)
- `delegation/templates/` folder
- Linear sync integration

## Implementation Plan

### Step 1: Create Archive Structure

```bash
mkdir -p .agent-context/archive
mkdir -p .agent-context/reviews  # if not exists
```

### Step 2: Relocate Files

```bash
# Active task (in 2-todo)
mv delegation/tasks/2-todo/ADV-0017-STARTER.md .agent-context/ADV-0017-HANDOFF-feature-developer.md

# Completed tasks (to archive)
mv delegation/tasks/5-done/ADV-0016-STARTER.md .agent-context/archive/ADV-0016-HANDOFF-feature-developer.md
mv delegation/tasks/5-done/ADV-0016-REVIEW-STARTER.md .agent-context/archive/ADV-0016-REVIEW-STARTER.md
mv delegation/tasks/5-done/ADV-0015-STARTER.md .agent-context/archive/ADV-0015-HANDOFF-feature-developer.md
mv delegation/tasks/5-done/ADV-0015-REVIEW-STARTER.md .agent-context/archive/ADV-0015-REVIEW-STARTER.md
mv delegation/tasks/5-done/ADV-0014-STARTER.md .agent-context/archive/ADV-0014-HANDOFF-feature-developer.md
mv delegation/tasks/5-done/ADV-0014-REVIEW-STARTER.md .agent-context/archive/ADV-0014-REVIEW-STARTER.md
```

### Step 3: Update State Files

**current-state.json**:
```json
{
  "project": "adversarial-workflow",
  "version": "0.5.0",
  "phase": "development",
  "last_updated": "2026-01-22",
  "status": {
    "overall": "healthy",
    "tests": "passing",
    "ci": "configured",
    "documentation": "needs-update"
  },
  "priorities": [
    "Complete plugin architecture (ADV-0017 to ADV-0019)",
    "Release v0.6.0 with custom evaluators"
  ],
  "recent_changes": [
    "v0.5.0: Released with bundled aider-chat",
    "ADV-0015: EvaluatorConfig dataclass",
    "ADV-0016: Evaluator discovery"
  ]
}
```

### Step 4: Update Planner Agent

Add these sections to `.claude/agents/planner.md`:

```markdown
## Task Starter Protocol

When assigning tasks to implementation agents:

### Step 1: Create Handoff File

Create `.agent-context/[TASK-ID]-HANDOFF-[agent-type].md` with:
- Implementation guidance
- Code examples
- Resources and references

### Step 2: Update agent-handoffs.json

### Step 3: Communicate Assignment

**File Locations**:
| File Type | Location |
|-----------|----------|
| Task spec | `delegation/tasks/[folder]/ADV-XXXX.md` |
| Handoff | `.agent-context/ADV-XXXX-HANDOFF-[agent].md` |
| Review starter | `.agent-context/ADV-XXXX-REVIEW-STARTER.md` |
| Reviews | `.agent-context/reviews/ADV-XXXX-review.md` |

## Code Review Workflow

After implementation complete:
1. Implementation agent creates `.agent-context/ADV-XXXX-REVIEW-STARTER.md`
2. User invokes code-reviewer in new tab
3. Review written to `.agent-context/reviews/`
4. Verdict: APPROVED → move to done, CHANGES_REQUESTED → fix and re-review
```

## Acceptance Criteria

### Must Have
- [ ] All STARTER files moved out of `delegation/tasks/`
- [ ] `.agent-context/archive/` contains completed task handoffs
- [ ] `current-state.json` shows v0.5.0 and current date
- [ ] Planner agent includes Task Starter Protocol section
- [ ] Planner agent includes file location table

### Should Have
- [ ] `agent-handoffs.json` updated with recent activity
- [ ] Planner includes Code Review Workflow section

## Success Metrics

**Quantitative**:
- 0 STARTER/HANDOFF files in `delegation/tasks/`
- Planner agent > 250 lines (from 149)

**Qualitative**:
- Clear separation between task specs and handoffs
- Future tasks follow correct conventions

## Notes

- This is a housekeeping task - no code changes to the package
- Does NOT include porting `scripts/project` (separate task if needed)
- Does NOT include Linear sync setup (not needed for this project)

---

**Related**: thematic-2 conventions, agentive-starter-kit
