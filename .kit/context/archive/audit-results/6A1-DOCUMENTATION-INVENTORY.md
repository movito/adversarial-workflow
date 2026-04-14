# Phase 6A.1: Documentation Inventory

**Date**: 2025-10-15
**Task**: Complete inventory of files requiring terminology review
**Total Files**: 16 files
**Total Lines**: 7,731 lines

---

## File Categories

### A. High-Priority Documentation (User-Facing)

Files users see first and most frequently. **CRITICAL** for clarity.

| File | Lines | Priority | Notes |
|------|-------|----------|-------|
| `README.md` | 421 | **CRITICAL** | Main package doc, first impression |
| `docs/EXAMPLES.md` | 1,128 | **HIGH** | Usage examples users follow |
| `docs/WORKFLOW_PHASES.md` | 1,462 | **HIGH** | Core workflow explanation |
| `docs/INTERACTION_PATTERNS.md` | 569 | **MEDIUM** | Advanced patterns |
| `docs/TOKEN_OPTIMIZATION.md` | 630 | **MEDIUM** | Cost optimization guide |
| `docs/TROUBLESHOOTING.md` | 1,003 | **HIGH** | Users come here when confused |

**Subtotal**: 6 files, 5,213 lines

### B. Templates (Generated for Users)

Files that become user configuration. Also **CRITICAL**.

| File | Lines | Priority | Notes |
|------|-------|----------|-------|
| `templates/evaluate_plan.sh.template` | 155 | **CRITICAL** | Phase 1 script, user-facing prompts |
| `templates/review_implementation.sh.template` | 226 | **CRITICAL** | Phase 3 script, phantom work detection |
| `templates/validate_tests.sh.template` | 238 | **CRITICAL** | Phase 4 script, test validation |
| `templates/config.yml.template` | 23 | **HIGH** | Configuration file |
| `templates/README.template` | 51 | **MEDIUM** | Instructions in .adversarial/ |
| `templates/example-task.md.template` | 111 | **MEDIUM** | Example task for quickstart |

**Subtotal**: 6 files, 804 lines (note: .env.example and .aider.conf.yml not counted - minimal content)

### C. Python Code (CLI Messages)

User-facing messages in Python code.

| File | Lines | Priority | Notes |
|------|-------|----------|-------|
| `adversarial_workflow/cli.py` | 1,055 | **HIGH** | Interactive prompts, error messages |

**Subtotal**: 1 file, 1,055 lines

**Note**: Only user-facing strings need update, not variable names or logic.

### D. Historical/Reference Documents

Created during development, lower priority.

| File | Lines | Priority | Notes |
|------|-------|----------|-------|
| `PHASE-3-COMPLETION-SUMMARY.md` | 443 | **LOW** | Historical record |
| `EVALUATOR-QA-REQUEST.md` | 216 | **LOW** | QA specification (internal) |

**Subtotal**: 2 files, 659 lines

### E. External Analysis (Not in Package)

| File | Lines | Priority | Notes |
|------|-------|----------|-------|
| `delegation/tasks/analysis/ADVERSARIAL-WORKFLOW-INDEPENDENCE-ANALYSIS.md` | 495 | **MEDIUM** | Referenced in docs, should update |

**Note**: This file is outside `adversarial-workflow/` directory but may be referenced.

---

## Priority Summary

| Priority | Files | Lines | Percentage |
|----------|-------|-------|------------|
| **CRITICAL** | 4 | 1,038 | 13.4% |
| **HIGH** | 5 | 3,291 | 42.6% |
| **MEDIUM** | 5 | 1,364 | 17.7% |
| **LOW** | 2 | 659 | 8.5% |
| **TOTAL** | 16 | 7,731 | 100% |

---

## Terminology Search Strategy

### Phase 6A.2 Will Search For:

**Primary Terms** (require review):
1. "Coordinator" (expect ~50-100 occurrences)
2. "Evaluator" (expect ~100-150 occurrences)
3. "agent" (lowercase, expect ~30-50 occurrences)
4. "Agent" (capitalized, expect ~20-30 occurrences)

**Compound Terms** (high priority):
5. "Coordinator agent"
6. "Evaluator agent"
7. "feature-developer agent"
8. "implementation agent"
9. "Coordinator-Evaluator"

**Context Terms** (need clarification):
10. "infrastructure"
11. "persistent"
12. "system" (when referring to agents)

### Expected Replacement Targets

Based on Evaluator feedback, expect to find:

**In README.md**:
- "Coordinator-Evaluator pattern" → "Author-Reviewer workflow"
- Multiple phase descriptions with old terminology

**In Script Templates**:
- Echo statements with "Coordinator" and "Evaluator"
- Comments referencing agents
- Prompt text with agent language

**In docs/WORKFLOW_PHASES.md**:
- Phase descriptions using old terminology
- Workflow explanations with agent metaphors

**In cli.py**:
- User-facing error messages
- Interactive prompts
- Help text

---

## Platform Messaging Search Strategy

### Phase 6A.3 Will Search For:

**Platform Terms**:
1. "Windows"
2. "macOS"
3. "Linux"
4. "WSL"
5. "platform"
6. "Unix"
7. "bash"

**Expected Locations**:
- README.md "Platform Support" section (already exists)
- docs/TROUBLESHOOTING.md (platform-specific issues)
- cli.py (need to add platform detection)
- templates/README.template (platform requirements)

---

## User Journey Mapping Strategy

### Phase 6A.4 Will Trace:

**Stage 1: Discovery**
- README.md first impression
- Feature list and claims
- Quick Start section

**Stage 2: Installation**
- `pip install adversarial-workflow`
- `adversarial init` or `adversarial quickstart`
- API key setup

**Stage 3: First Usage**
- Creating first task
- Running first evaluation
- Understanding output

**Stage 4: Troubleshooting**
- Common errors
- Confusion points
- Documentation searches

---

## File Modification Estimates

### Phase 6B Workload Prediction

Based on line counts and expected terminology density:

**Heavy modifications** (>50 changes):
- README.md (421 lines) - ~30-50 terminology updates
- docs/WORKFLOW_PHASES.md (1,462 lines) - ~80-100 updates
- docs/EXAMPLES.md (1,128 lines) - ~40-60 updates

**Moderate modifications** (20-50 changes):
- templates/evaluate_plan.sh.template (155 lines) - ~25-30 updates
- templates/review_implementation.sh.template (226 lines) - ~30-35 updates
- templates/validate_tests.sh.template (238 lines) - ~30-35 updates
- cli.py (1,055 lines) - ~40-50 updates (user-facing strings only)

**Light modifications** (<20 changes):
- docs/INTERACTION_PATTERNS.md (569 lines) - ~10-15 updates
- docs/TOKEN_OPTIMIZATION.md (630 lines) - ~15-20 updates
- docs/TROUBLESHOOTING.md (1,003 lines) - ~15-20 updates
- templates/config.yml.template (23 lines) - ~2-3 updates
- templates/README.template (51 lines) - ~5-10 updates
- templates/example-task.md.template (111 lines) - ~5-10 updates

**Total Estimated Changes**: ~350-450 terminology updates across all files

---

## Tools for Audit

### Automated Search Commands

```bash
# Count occurrences of deprecated terms
cd adversarial-workflow
grep -r "Coordinator" --include="*.md" --include="*.template" --include="*.py" | wc -l
grep -r "Evaluator" --include="*.md" --include="*.template" --include="*.py" | wc -l
grep -ri "agent" --include="*.md" --include="*.template" --include="*.py" | wc -l

# Find specific compound terms
grep -rn "Coordinator agent" --include="*.md" --include="*.template"
grep -rn "Evaluator agent" --include="*.md" --include="*.template"
grep -rn "Coordinator-Evaluator" --include="*.md" --include="*.template"

# Platform terms
grep -rn "Windows" --include="*.md" --include="*.py"
grep -rn "WSL" --include="*.md"
```

---

## Completion Criteria for 6A.1

- [x] Complete inventory of all files (16 files identified)
- [x] Line counts for all files (7,731 lines total)
- [x] Priority assignments (CRITICAL/HIGH/MEDIUM/LOW)
- [x] Search strategy defined
- [x] Modification estimates calculated
- [x] Tools for audit specified

**Status**: ✅ COMPLETE

**Time Taken**: ~10 minutes
**Next**: Phase 6A.2 - Metaphor Confusion Audit (30 min)

---

## Notes

1. **Scope is manageable**: 7,731 lines across 16 files is thorough but achievable in Phase 6B timeframe
2. **Priority targeting**: Focusing on CRITICAL and HIGH priority files (4,329 lines, 56% of total) will deliver maximum impact
3. **Automation potential**: Many replacements can be semi-automated with context review
4. **Testing requirement**: All code examples in docs must be tested after changes

---

**Document Status**: COMPLETE
**Next Document**: 6A2-TERMINOLOGY-AUDIT.md (Metaphor confusion audit)
