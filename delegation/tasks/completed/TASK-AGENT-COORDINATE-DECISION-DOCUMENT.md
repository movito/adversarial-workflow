# Agent Coordination System: Decision Document

**Date**: 2025-10-19
**Decision Maker**: Coordinator
**Decision**: TEMPLATE APPROACH (NOT package extraction)
**Status**: IMPLEMENTED & COMPLETE

---

## Executive Summary

**Decision**: Use **agent-roles-template repository** instead of agent-coordinate package extraction

**Rationale**:
1. **Lower effort**: 5 hours (actual) vs. 80-90 hours (package extraction estimate)
2. **Immediate value**: Users can copy templates today without waiting for package development
3. **Simpler**: No PyPI packaging, versioning, or maintenance overhead
4. **Proven demand**: The template repository solves the stated user need ("transport agent roles across projects")

---

## Background

### Original Request
User asked: "How can we make a more robust setup for agent roles that can be transported across projects?"

### Options Considered

**Option A: Package Extraction** (`agent-coordinate` PyPI package)
- Effort: 80-90 hours for full implementation
- Risk: Medium-high (unknown market size, ~5-10 users)
- Complexity: High (PyPI packaging, CLI, Python API, versioning)
- Requires: User validation (Phase -1), beta testing (Phase 0)

**Option B: Template Repository** (`agent-roles-template` on GitHub)
- Effort: 3-5 hours for repository creation
- Risk: Low (minimal investment, easy to iterate)
- Complexity: Low (markdown + JSON templates)
- Immediate: Users can copy-paste today

---

## Decision Rationale

### Why Template Repository Won

1. **Reviewer Recommendation**:
   > "Keep in adversarial-workflow until 50+ users request extraction"
   > "Ultra-minimal template repository (5 hours) vs full package (80-90 hours)"

2. **User Need Met**:
   - Users can copy `agent-handoffs.json` to new projects ✅
   - Multiple template variants provided (standard 8-role, minimal 3-role) ✅
   - Well-documented with examples ✅
   - No installation or dependencies required ✅

3. **Integration Complete**:
   - Phase 1: Created `github.com/movito/agent-roles-template` (3 hours)
   - Phase 2: Integrated template selection into `adversarial agent onboard` (2 hours)
   - Users can choose standard, minimal, custom URL, or skip during onboarding

4. **Evidence-Based**:
   - Current user base: ~5-10 people using agent coordination
   - No validation showing demand for standalone package
   - Template approach provides immediate value without validation overhead

---

## Implementation Summary

### What Was Built

**Repository**: `github.com/movito/agent-roles-template`
- Standard template (8 roles): coordinator, feature-developer, api-developer, format-developer, test-runner, document-reviewer, security-reviewer, media-processor
- Minimal template (3 roles): coordinator, developer, reviewer
- Comprehensive README with quick start and FAQ
- 2 example projects demonstrating usage
- 988 lines total, MIT License, public repository

**Integration**: `adversarial agent onboard` command
- Template selection prompt (standard/minimal/custom/skip)
- Dynamic template fetching from GitHub
- Variable substitution (PROJECT_NAME, DATE, PYTHON_VERSION)
- Fallback to built-in templates on error
- Updated documentation (README.md, QUICK_START.md, EXAMPLES.md)

### Time Investment
- **Actual**: 5 hours (3h Phase 1, 2h Phase 2)
- **Original estimate**: 6-10 hours (template approach)
- **Avoided effort**: 80-90 hours (package extraction approach)

---

## Tasks Status

### Completed
- ✅ **TASK-AGENT-TEMPLATE-INTEGRATION.md**: Phase 1 & 2 complete (5h)

### Superseded (No Longer Needed)
- ❌ **TASK-AGENT-COORDINATE-PHASE-MINUS-1-VALIDATION.md**: User validation not required for template approach
- ❌ **TASK-AGENT-COORDINATE-PHASE-0-MINIMAL-EXTRACTION.md**: Package extraction not pursued
- ✅ **TASK-AGENT-COORDINATE-DECISION-DOCUMENT.md**: This document (decision recorded)

---

## Success Metrics

### Template Repository
- ✅ Public and accessible
- ✅ Clear documentation (README)
- ✅ Multiple variants (standard, minimal)
- ✅ Working examples included
- ✅ Tested template download

### Integration
- ✅ Template selection integrated into `adversarial agent onboard`
- ✅ Smoke tests passed (standard, minimal, variable substitution)
- ✅ Documentation updated
- ✅ Git cleanup completed (all work committed and pushed)

---

## Future Considerations

### When to Reconsider Package Extraction

Consider extracting `agent-coordinate` package IF:
1. **User base grows to 50+ active users** using agent coordination
2. **Specific requests** for PyPI package (not just templates)
3. **Pain points emerge** that templates cannot solve (e.g., programmatic API, complex state management)
4. **Maintenance burden** of template approach becomes significant

### Current Recommendation
- **Keep agent coordination in adversarial-workflow** as extension layer
- **Maintain agent-roles-template repository** for easy copying
- **Improve documentation** as primary value-add
- **Monitor user feedback** for future extraction decision

---

## Lessons Learned

1. **Start minimal**: Template repository (5h) validated the concept before heavy investment (80-90h)
2. **User validation matters**: Without proven demand, avoid premature extraction
3. **Reviewer feedback valuable**: External critique prevented scope creep
4. **Hybrid approach works**: Built-in templates + GitHub templates provide flexibility

---

## Next Steps

1. ✅ Move TASK-AGENT-TEMPLATE-INTEGRATION.md to `delegation/tasks/completed/`
2. ✅ Archive Phase -1 and Phase 0 tasks to `delegation/tasks/archived/`
3. ✅ Update agent-handoffs.json with decision status
4. Ready for handoff to thematic-cuts or new adversarial-workflow development

---

**Signed**: Coordinator Agent
**Date**: 2025-10-19
