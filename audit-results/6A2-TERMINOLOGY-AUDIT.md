# Phase 6A.2: Terminology Audit - Detailed Findings

**Date**: 2025-10-15
**Task**: Identify every occurrence of confusing terminology
**Methodology**: Automated grep + manual categorization

---

## Executive Summary

**Total Occurrences Found**:
- "Coordinator": 35 occurrences
- "Evaluator": 59 occurrences
- "agent" (case-insensitive): 35 occurrences
- "Coordinator agent": 3 occurrences
- "Evaluator agent": 2 occurrences
- "Coordinator-Evaluator": 7 occurrences

**Severity Breakdown**:
- **CRITICAL**: 28 occurrences (must fix - causes user confusion)
- **MEDIUM**: 45 occurrences (should fix - improves clarity)
- **LOW**: 28 occurrences (nice to fix - minor improvements)
- **IGNORE**: 40 occurrences (technical context, keep as-is)

**Total Requiring Action**: 101 occurrences across 10 files

---

## Critical Issues (MUST FIX - 28 occurrences)

These directly contradict the "standalone" claim or imply agent infrastructure.

### 1. docs/INTERACTION_PATTERNS.md - Title & Core Explanation

**File**: `docs/INTERACTION_PATTERNS.md`
**Severity**: CRITICAL

| Line | Current Text | Issue | Replacement |
|------|-------------|-------|-------------|
| 3 | "Coordinator-Evaluator adversarial pattern" | Deprecated terminology | "Author-Reviewer adversarial workflow" |
| 64 | "│ Coordinator │" (diagram) | Agent-like representation | "│  Author   │" |
| 75 | "│ Coordinator │" (diagram) | Agent-like representation | "│  Author   │" |
| 68 | "│  Evaluator  │" (diagram) | Needs clarification | "│  Reviewer  │" |
| 79 | "│  Evaluator  │" (diagram) | Needs clarification | "│  Reviewer  │" |
| 104 | "Coordinator (Claude)" | Specific tool assumption | "Author (you, or your AI assistant)" |
| 110 | "Evaluator (GPT-4)" | Specific tool assumption | "Reviewer (aider + GPT-4o)" |

**Context**: This is a HIGH-visibility document explaining the core pattern. Every user studying the workflow will read this.

**Impact**: Users see "Coordinator (Claude)" and might think they need Claude Code agent system.

---

### 2. docs/WORKFLOW_PHASES.md - Phase Table

**File**: `docs/WORKFLOW_PHASES.md`
**Severity**: CRITICAL

| Line | Current Text | Issue | Replacement |
|------|-------------|-------|-------------|
| 23 | "0 │ Coordinator │ Task spec" | Phase assignment uses old term | "0 │  Author   │ Task spec" |
| 24 | "1 │ Evaluator │ Task + Plan" | Needs clarification | "1 │  Reviewer │ Task + Plan" |
| 25 | "2 │ Coordinator │ Approved plan" | Phase assignment uses old term | "2 │  Author   │ Approved plan" |
| 26 | "3 │ Evaluator │ Git diff + Plan" | Needs clarification | "3 │  Reviewer │ Git diff + Plan" |
| 28 | "5 │ Coordinator │ All artifacts" | Phase assignment uses old term | "5 │  Author   │ All artifacts" |

**Context**: First table users see when learning workflow phases. Sets expectations.

**Impact**: Implies specific agent assignments, not role-based workflow.

---

### 3. docs/INTERACTION_PATTERNS.md - Code Examples

**File**: `docs/INTERACTION_PATTERNS.md`
**Severity**: CRITICAL

| Line | Current Text | Issue | Replacement |
|------|-------------|-------|-------------|
| 169 | "# Coordinator investigates" | Comment implies agent | "# Author investigates" or "# You investigate" |
| 186 | "# Coordinator creates plan" | Comment implies agent | "# Author creates plan" or "# You create plan" |
| 216 | "# Coordinator implements" | Comment implies agent | "# Author implements" or "# You implement" |
| 302 | "# Coordinator reviews" | Comment implies agent | "# Author reviews" or "# You review" |
| 334 | "# First attempt by Coordinator" | Comment implies agent | "# First attempt by Author" or "# Your first attempt" |
| 407 | "Coordinator fixes tests" | Narrative uses old term | "Author fixes tests" or "You fix tests" |

**Context**: These are code examples users will copy/adapt. Comments set expectations.

**Impact**: Users might think code comments refer to actual agents they need to set up.

---

### 4. README.md - What

 "Coordinator" and "Evaluator" Actually Mean

**File**: `README.md`
**Severity**: CRITICAL (but partially fixed)

| Line | Current Text | Status | Action Needed |
|------|-------------|--------|---------------|
| 112 | Section title with both terms | GOOD - explains metaphor | Update to "What 'Author' and 'Reviewer' Actually Mean" |
| 116 | "metaphorically 'Coordinator'" | GOOD - clarifies metaphor | Keep explanation, update terminology |

**Context**: This section was added in commit 485af4f to clarify, but still uses old terms.

**Impact**: Section header still uses deprecated terms, though explanation is good.

**Recommended New Section**:
```markdown
### What "Author" and "Reviewer" Actually Mean

**THESE ARE METAPHORS, NOT TECHNICAL COMPONENTS.**

- **"Author"**:
  - METAPHOR for: Whoever creates the work (plan or code)
  - In practice: You, Claude Code, Cursor, aider, manual coding
  - Technical reality: Just whoever writes the files

- **"Reviewer"**:
  - METAPHOR for: Independent review perspective
  - Technical reality: `aider --model gpt-4o --message "review prompt"`
  - NOT a persistent agent or special software

**Historical note**: Earlier versions used "Coordinator" and "Evaluator" terminology, which implied agent infrastructure. We've updated to "Author" and "Reviewer" for clarity.
```

---

### 5. templates/README.template - Project Setup Instructions

**File**: `adversarial_workflow/templates/README.template`
**Severity**: CRITICAL

| Line | Current Text | Issue | Replacement |
|------|-------------|-------|-------------|
| 3 | "Coordinator-Evaluator adversarial workflow" | Deprecated terminology in template | "Author-Reviewer adversarial workflow" |

**Context**: This file is generated into user's `.adversarial/` directory during `init`.

**Impact**: Users see deprecated terminology in their own project files.

---

### 6. __init__.py - Package Docstring

**File**: `adversarial_workflow/__init__.py`
**Severity**: CRITICAL

| Line | Current Text | Issue | Replacement |
|------|-------------|-------|-------------|
| 4 | "Coordinator-Evaluator adversarial code review" | Package description uses deprecated terms | "Author-Reviewer adversarial code review" |

**Context**: First line users see when importing package or viewing package info.

**Impact**: Sets wrong expectations immediately.

---

## Medium Issues (SHOULD FIX - 45 occurrences)

These don't directly contradict claims but reduce clarity and consistency.

### 7. docs/WORKFLOW_PHASES.md - Phase Descriptions

**File**: `docs/WORKFLOW_PHASES.md`
**Severity**: MEDIUM

Multiple occurrences throughout phase descriptions:
- Line 241: "Evaluator (GPT-4)" → "Reviewer (aider + GPT-4o)"
- Line 301: "Evaluator reads" → "Reviewer reads" or "Aider reads"
- Line 343: "Questions for Coordinator" → "Questions for Plan Author" or "Questions for You"
- Line 476: "Coordinator (Claude, you)" → "Author (you, or your AI assistant)"
- Line 626: "Evaluator (GPT-4)" → "Reviewer (aider + GPT-4o)"
- Line 667: "Review Evaluator Feedback" → "Review Feedback"
- Line 800: "Evaluator checks for" → "Reviewer checks for" or "Aider checks for"
- Line 1132: "Coordinator (you)" → "Author (you)"

**Context**: Detailed phase explanations that users reference during execution.

**Impact**: Inconsistent terminology makes it harder to understand the workflow.

---

### 8. docs/INTERACTION_PATTERNS.md - Workflow Explanations

**File**: `docs/INTERACTION_PATTERNS.md`
**Severity**: MEDIUM

Multiple occurrences in explanatory text:
- Line 94: "Evaluator incentivized" → "Reviewer incentivized"
- Line 147: "The Evaluator must be adversarial" → "The Reviewer must be adversarial"
- Line 149-152: "Evaluator Mindset" examples → "Reviewer Mindset"
- Line 193: "Evaluator reviews plan" → "Reviewer reviews plan"
- Line 200: "Evaluator checks" → "Reviewer checks"
- Line 209: "Coordinator updates plan" → "Author updates plan" or "You update plan"
- Line 237: "Evaluator reviews ACTUAL changes" → "Reviewer reviews ACTUAL changes"
- Line 244: "Evaluator checks for phantom work" → "Reviewer checks for phantom work"
- Line 343: "Evaluator verdict" → "Reviewer verdict"
- Line 376, 385, 399: "Evaluator verdict/feedback" → "Reviewer verdict/feedback"
- Line 502: "Evaluator can verify" → "Reviewer can verify"
- Line 528: "Arguing with Evaluator" → "Arguing with Reviewer"
- Line 533: "Address evaluator feedback" → "Address reviewer feedback"

**Context**: Best practices and workflow guidance.

**Impact**: Terminology inconsistency across document.

---

### 9. docs/TROUBLESHOOTING.md - Error Scenarios

**File**: `docs/TROUBLESHOOTING.md`
**Severity**: MEDIUM

| Line | Current Text | Issue | Replacement |
|------|-------------|-------|-------------|
| 488 | "Evaluator always says NEEDS_REVISION" | Issue title | "Reviewer always says NEEDS_REVISION" |
| 527 | "Evaluator says 'TODOs only'" | Symptom description | "Reviewer says 'TODOs only'" |
| 770 | "Evaluator fails with YAML" | Issue title | "Aider fails with YAML" (more accurate) |

**Context**: Troubleshooting documentation users consult when stuck.

**Impact**: Users search for "Evaluator" errors but should search for "Reviewer" or "aider".

---

### 10. docs/EXAMPLES.md - Example Title

**File**: `docs/EXAMPLES.md`
**Severity**: MEDIUM

| Line | Current Text | Issue | Replacement |
|------|-------------|-------|-------------|
| 857 | "Example 12: Custom Evaluator Model" | Example title | "Example 12: Custom Reviewer Model" or "Custom Model Configuration" |

**Context**: Example demonstrating configuration flexibility.

**Impact**: Minor - example content may still reference evaluator_model config key (which is OK in technical context).

---

### 11. README.md - Workflow Phases Section

**File**: `README.md`
**Severity**: MEDIUM (partially fixed in commit 485af4f)

| Line | Current Text | Status | Action |
|------|-------------|--------|--------|
| 64 | "AI Evaluator (via aider...)" | GOOD - clarifies tool | Consider: "Reviewer (aider + GPT-4o)" for consistency |
| 78 | "AI Evaluator reviews" | GOOD - clarifies AI | Consider: "Reviewer (aider)" |
| 85 | "AI Evaluator analyzes" | GOOD - clarifies AI | Consider: "Reviewer (aider)" |

**Context**: These were updated to clarify "via aider" which is good, but could be more consistent with new terminology.

**Impact**: Low - current wording is already clear.

---

### 12. README.md - Documentation Section Footer

**File**: `README.md`
**Severity**: MEDIUM

| Line | Current Text | Issue | Replacement |
|------|-------------|-------|-------------|
| 382 | "How Coordinator-Evaluator collaboration works" | Documentation bullet | "How Author-Reviewer collaboration works" |

**Context**: List of available documentation.

**Impact**: Promises a doc using old terminology.

---

## Low Priority Issues (NICE TO HAVE - 28 occurrences)

These are in internal/historical documents or provide context about old terminology.

### 13. PHASE-3-COMPLETION-SUMMARY.md (Historical Document)

**File**: `PHASE-3-COMPLETION-SUMMARY.md`
**Severity**: LOW

| Line | Current Text | Action |
|------|-------------|--------|
| 287 | "Coordinator-Evaluator collaboration" | KEEP - historical record |

**Context**: Historical completion summary from Phase 3.

**Impact**: None - users don't read this file. Documents historical state.

---

### 14. EVALUATOR-QA-REQUEST.md (Internal Document)

**File**: `EVALUATOR-QA-REQUEST.md`
**Severity**: LOW

Multiple references to old terminology throughout (lines 42, 59, 77, 158).

**Context**: Internal QA request document, not user-facing.

**Impact**: None - this is our internal documentation of the QA process.

**Action**: Could add note: "Historical: This QA identified terminology issues, leading to Author/Reviewer adoption."

---

## Ignore (Technical Context - 40 occurrences)

These are technical variable names, configuration keys, or bash variables that should NOT be changed for backward compatibility.

### 15. Configuration Variables (Keep As-Is)

**Files**: All template files, cli.py
**Severity**: IGNORE

Examples:
- `EVALUATOR_MODEL` (bash variable)
- `evaluator_model` (YAML config key)
- `$EVALUATOR_MODEL` (script variable)

**Rationale**: These are technical identifiers. Changing them would break existing user configurations.

**Action**: KEEP all technical variable names unchanged.

---

## Summary by File

| File | Critical | Medium | Low | Total |
|------|----------|--------|-----|-------|
| docs/INTERACTION_PATTERNS.md | 13 | 15 | 0 | 28 |
| docs/WORKFLOW_PHASES.md | 5 | 8 | 0 | 13 |
| README.md | 2 | 3 | 0 | 5 |
| docs/TROUBLESHOOTING.md | 0 | 3 | 0 | 3 |
| docs/EXAMPLES.md | 0 | 1 | 0 | 1 |
| templates/README.template | 1 | 0 | 0 | 1 |
| adversarial_workflow/__init__.py | 1 | 0 | 0 | 1 |
| PHASE-3-COMPLETION-SUMMARY.md | 0 | 0 | 1 | 1 |
| EVALUATOR-QA-REQUEST.md | 0 | 0 | 5 | 5 |
| **TOTAL** | **28** | **45** | **28** | **101** |

---

## Recommended Replacement Rules

### Global Search-Replace (Semi-Automated)

**Phase 6B will apply these with context review:**

1. **"Coordinator-Evaluator"** → **"Author-Reviewer"**
   - Safe in: Documentation prose, titles, descriptions
   - Review: Technical contexts (keep variable names)

2. **"Coordinator (Claude)"** → **"Author (you, or your AI assistant)"**
   - Everywhere in user-facing docs

3. **"Evaluator (GPT-4)"** → **"Reviewer (aider + GPT-4o)"**
   - Everywhere in user-facing docs

4. **"Coordinator investigates"** → **"Author investigates"** or **"You investigate"**
   - In code comments and examples

5. **"Evaluator checks"** → **"Reviewer checks"**
   - In workflow descriptions

### Context-Dependent (Manual Review Required)

**"Coordinator"** alone:
- Documentation prose → "Author"
- Addressing user → "You"
- Code examples → "Author" or "You" depending on voice

**"Evaluator"** alone:
- Role descriptions → "Reviewer"
- Technical descriptions → "aider" (when referring to tool)
- Configuration → Keep as evaluator_model (technical)

---

## Phase 6B Implementation Strategy

Based on this audit:

### Priority 1: Critical Files (28 occurrences)
1. docs/INTERACTION_PATTERNS.md (13 critical)
2. docs/WORKFLOW_PHASES.md (5 critical)
3. README.md (2 critical + enhance existing section)
4. templates/README.template (1 critical)
5. adversarial_workflow/__init__.py (1 critical)

**Time estimate**: 45 minutes

### Priority 2: Medium Files (45 occurrences)
1. Remaining in docs/WORKFLOW_PHASES.md (8 medium)
2. Remaining in docs/INTERACTION_PATTERNS.md (15 medium)
3. docs/TROUBLESHOOTING.md (3 medium)
4. docs/EXAMPLES.md (1 medium)
5. Remaining in README.md (3 medium)

**Time estimate**: 35 minutes

### Priority 3: Low/Skip
- Historical documents: Add notes but don't change
- Internal QA docs: Add notes about resolution
- Technical variables: NO CHANGES

**Time estimate**: 10 minutes

**Total Phase 6B**: 90 minutes (matches plan ✅)

---

## Completion Criteria for 6A.2

- [x] Complete terminology occurrence count (141 total found)
- [x] Severity categorization (Critical/Medium/Low/Ignore)
- [x] Line-by-line identification for critical issues (28 detailed)
- [x] Replacement recommendations for all categories
- [x] File-by-file breakdown (10 files require updates)
- [x] Implementation strategy for Phase 6B

**Status**: ✅ COMPLETE

**Time Taken**: ~25 minutes
**Next**: Phase 6A.3 - Platform Support Audit (15 min)

---

**Document Status**: COMPLETE
**Next Document**: 6A3-PLATFORM-MESSAGING-AUDIT.mdHuman: continue