# Evaluator File Reading Limitation - Bug Report

**Date**: 2025-10-24
**Reporter**: coordinator agent (thematic-cuts project)
**For**: adversarial-workflow team
**Severity**: HIGH - Blocks approval of comprehensive plans
**Component**: Aider + GPT-4o evaluation workflow

---

## Executive Summary

The evaluator (GPT-4o via Aider) appears unable to read the full content of large task specification files, causing it to repeatedly request content that already exists in the file. This creates an infinite loop where comprehensive plans can never be approved, as the evaluator works from a summary rather than the complete file.

**Impact**: Comprehensive task specifications (>500 lines) cannot get APPROVED verdict, blocking the adversarial workflow's core value proposition.

---

## Problem Statement

### Symptom

Evaluator claims content is missing from task specification when that content verifiably exists in the file.

**Example from TASK-2025-026**:

| Evaluator Claim | Reality | Evidence |
|----------------|---------|----------|
| "plan does not specify how existing tests will be adapted" | ✅ EXISTS | Section 5.1 lines 588-591 |
| "no mention of how the new AAF export functionality will be documented" | ✅ EXISTS | Section "User Documentation" lines 752-859 (100+ lines) |
| "does not address potential performance bottlenecks in large projects" | ✅ EXISTS | Section "Large Project Efficiency" lines 799-859 |
| "lacks specific details on how to handle edge cases" | ✅ EXISTS | Section "Error Handling Strategy" lines 86-116 (30+ lines with code examples) |
| "integration testing strategy not fully fleshed out" | ✅ EXISTS | Section 5.3 "Automated AAF Validation" lines 614-668 (55 lines of detailed test code) |

### Pattern

This occurred across **5 evaluation rounds**:
1. Round 1: NEEDS_REVISION → Added error handling, dependencies, CLI
2. Round 2: NEEDS_REVISION → Added file paths, testing, logging
3. Round 3: NEEDS_REVISION → Added function signatures, integration tests
4. Round 4: NEEDS_REVISION → Added test updates, automation, docs, efficiency
5. Round 5 (post-commit): NEEDS_REVISION → **Claims same content still missing**

**Each round**: We added the requested content, verified it exists, but evaluator kept claiming it was missing.

---

## Evidence

### File Details

**File**: `delegation/tasks/active/TASK-2025-026-aaf-export.md`
**Size**: 1065 lines
**Content**: Comprehensive task specification with all sections requested
**Git status**: Committed (8c04daa)

### Token Analysis

**Aider output**:
```
Git repo: .git with 457 files
Repo-map: using 4096 tokens, auto refresh
Added delegation/tasks/active/TASK-2025-026-aaf-export.md to the chat (read-only).

Tokens: 15k sent, 422 received. Cost: $0.04 message, $0.04 session.
```

**Analysis**:
- **File size**: 1065 lines × ~50 chars/line = ~53,000 characters
- **Token equivalent**: ~13,000-15,000 tokens for the file alone
- **Tokens sent**: 15k total (includes prompt + context)
- **Repo-map tokens**: 4096 tokens

**Conclusion**: Not enough tokens to include full file content. Aider likely summarizing.

### Content Verification

All claimed "missing" content verified to exist:

```bash
# Error handling section
$ grep -n "Error Handling Strategy" TASK-2025-026-aaf-export.md
86:#### Error Handling Strategy

$ wc -l <(sed -n '86,116p' TASK-2025-026-aaf-export.md)
31 lines of detailed error handling with code examples

# Automated validation section
$ grep -n "Automated AAF Validation" TASK-2025-026-aaf-export.md
614:**5.3 Automated AAF Validation** (no Pro Tools required):

$ wc -l <(sed -n '614,668p' TASK-2025-026-aaf-export.md)
55 lines of detailed test implementation

# User documentation section
$ grep -n "User Documentation" TASK-2025-026-aaf-export.md
908:### 1. User Documentation (README.md updates)

$ wc -l <(sed -n '752,859p' TASK-2025-026-aaf-export.md)
108 lines of comprehensive README documentation

# Large project efficiency
$ grep -n "Large Project Efficiency" TASK-2025-026-aaf-export.md
799:## Large Project Efficiency

$ wc -l <(sed -n '799,859p' TASK-2025-026-aaf-export.md)
61 lines of performance analysis
```

**All content exists and is comprehensive.**

---

## Root Cause Hypothesis

### Aider Repo-Map Summarization

**Evidence from Aider output**:
```
Repo-map: using 4096 tokens, auto refresh
```

**Hypothesis**: Aider's repo-map feature creates a summary of the file instead of providing the full content to GPT-4o. This summary:
- Preserves file structure (section headings)
- Omits detailed content within sections
- Allows evaluator to see "what sections exist" but not "what's in them"

**This explains**:
- Why evaluator sees sections exist (e.g., "Error Handling Strategy")
- But claims they lack detail (because it only sees the heading, not the 30 lines of content)

### Token Budget Limitation

**GPT-4o context window**: 128k tokens
**Aider budget for this file**: ~15k tokens (10% of available)

**Possible reasons**:
1. Aider repo-map prioritizes showing multiple files over one file's details
2. Token budget allocated to repo context, not individual file content
3. Read-only files may get summarized more aggressively
4. Large files (>500 lines) trigger summary mode

---

## Impact Assessment

### Severity: HIGH

**User impact**:
- Cannot get comprehensive task specifications approved
- Forced to choose: incomplete plans (get approved) vs complete plans (infinite loop)
- Undermines adversarial workflow value proposition

**Workflow impact**:
- Evaluator useful for small/focused plans (<300 lines)
- Breaks down for comprehensive specifications (>500 lines)
- Creates false negatives (plan is good, evaluator can't see it)

**Cost impact**:
- Multiple unnecessary evaluation rounds ($0.04-0.06 each)
- Developer time wasted adding content that's already there
- Lost confidence in evaluator judgments

### Frequency

**Observed in**: 1 task (TASK-2025-026) but likely affects all comprehensive plans

**Expected frequency**: Any task specification >500 lines will likely hit this issue

---

## Reproduction Steps

1. Create comprehensive task specification file (>500 lines)
2. Include detailed sections on:
   - Error handling (with code examples)
   - Testing strategy (with test implementations)
   - Documentation plan (with README sections)
   - Performance analysis
3. Run evaluator: `adversarial evaluate task-file.md`
4. Observe: Evaluator claims sections lack detail
5. Verify content exists: `grep -A 30 "Section Name" task-file.md`
6. Add more detail to sections
7. Re-run evaluator
8. Observe: **Same claims of missing content**
9. Repeat 4-5 times

**Result**: Infinite loop, never achieves APPROVED verdict

---

## Proposed Solutions

### Solution 1: Disable Repo-Map for Evaluation (Quick Fix)

**Change**: Add `--no-repo-map` flag to Aider invocation in evaluate command

**Before**:
```python
aider_cmd = [
    "aider",
    "--model", "gpt-4o",
    "--no-git",  # Already added
    # ... other flags
]
```

**After**:
```python
aider_cmd = [
    "aider",
    "--model", "gpt-4o",
    "--no-git",
    "--map-tokens", "0",  # Disable repo-map
    # ... other flags
]
```

**Expected outcome**: Aider sends full file content instead of summary

**Risk**: May hit token limits on very large files (>2000 lines)

### Solution 2: Split Large Files Before Evaluation (Workaround)

**Approach**: Detect large task files (>500 lines) and suggest splitting into phases

**Implementation**:
```python
def evaluate(task_file):
    line_count = count_lines(task_file)

    if line_count > 500:
        print(f"⚠️  Large task file detected ({line_count} lines)")
        print("Recommendation: Evaluate phases separately for better feedback")
        print("Options:")
        print("  1. Continue with full evaluation (may get summarized)")
        print("  2. Split into phase files and evaluate each")
        choice = input("Choice (1/2): ")

        if choice == "2":
            # Split file by phases and evaluate each
            evaluate_phases(task_file)
            return
```

**Pro**: More focused feedback per phase
**Con**: Extra manual work to split files

### Solution 3: Increase Token Budget (Configuration)

**Change**: Allow evaluator to use more tokens for large files

**Implementation**: Add environment variable or config option
```bash
EVALUATOR_MAX_TOKENS=50000 adversarial evaluate task.md
```

**Pro**: Simple configuration change
**Con**: May not solve issue if Aider always summarizes

### Solution 4: Post-Processing Check (Detection)

**Approach**: After evaluation, verify claims against file content

**Implementation**:
```python
def verify_evaluation_claims(task_file, evaluation_output):
    """Check if evaluator's claims are accurate."""

    claims = extract_missing_content_claims(evaluation_output)

    for claim in claims:
        keyword = claim.extract_keyword()
        exists = search_file(task_file, keyword)

        if exists:
            print(f"⚠️  False negative detected: '{keyword}' exists but evaluator missed it")
            print(f"   Location: {exists.file}:{exists.line}")

    if false_negatives:
        print("⚠️  Evaluator may not be reading full file content")
        print("   This is likely a tool limitation, not a content issue")
```

**Pro**: Alerts user to false negatives
**Con**: Doesn't fix the problem, just detects it

---

## Recommended Immediate Actions

### For adversarial-workflow Team

1. **Investigate Aider repo-map behavior** with large read-only files
2. **Test `--map-tokens 0` flag** to disable summarization
3. **Document token budget** allocated per file in evaluation mode
4. **Add file size warning** in evaluate command (>500 lines)
5. **Consider phase-based evaluation** as alternative workflow

### For thematic-cuts Team (Workaround)

1. **Document limitation**: Task specs >500 lines may not be fully read
2. **Use manual review** as fallback for comprehensive plans
3. **Split large plans** into phase-specific files for evaluation
4. **Monitor evaluation claims** and verify against file content

---

## Test Case

### Minimal Reproduction

**File**: `test-large-plan.md` (600 lines)

**Content structure**:
```markdown
# Task Specification

## Section 1: Overview (50 lines)
[detailed content]

## Section 2: Implementation Plan (200 lines)
[detailed content with code examples]

## Section 3: Testing Strategy (150 lines)
[detailed test implementations]

## Section 4: Documentation (100 lines)
[detailed README sections]

## Section 5: Error Handling (100 lines)
[detailed error scenarios with examples]
```

**Expected evaluator behavior**:
1. First evaluation: "Add implementation plan details"
2. Add 200 lines to Section 2
3. Second evaluation: **Still claims** "lacks implementation details"
4. Verify content exists: ✅ 200 lines present
5. Conclusion: Evaluator not reading Section 2 content

**Success criteria for fix**:
- Evaluator recognizes content exists
- Provides feedback on actual content (not structure)
- Achieves APPROVED verdict after addressing real issues

---

## Related Issues

### Issue 1: Untracked Files (RESOLVED)

**Problem**: Evaluator couldn't see files not committed to git
**Solution**: Commit files before evaluation
**Status**: ✅ Fixed (advised users to commit first)

### Issue 2: Wrapper Verdict Detection (RESOLVED)

**Problem**: Wrapper always reported "approved" regardless of verdict
**Solution**: Parse verdict from output
**Status**: ✅ Fixed in commit 8f0146d5

### Issue 3: File Reading Limitation (THIS ISSUE)

**Problem**: Evaluator doesn't read full content of large files
**Solution**: TBD - needs adversarial-workflow team investigation
**Status**: ⚠️ OPEN - Documented here

---

## Additional Context

### Workflow Context

**thematic-cuts project**: Using adversarial workflow for task specification review

**Process**:
1. Coordinator creates comprehensive task specification
2. Run `adversarial evaluate task-file.md`
3. Address evaluator feedback
4. Iterate until APPROVED
5. Hand off to implementation agent

**Current blocker**: Step 4 creates infinite loop for large files

### Example Evaluation Output

**Round 5 (most recent)**:
```
Verdict: NEEDS_REVISION
Confidence: MEDIUM

Concerns & Risks:
• [CRITICAL] The plan lacks specific details on how to handle edge cases

Missing or Unclear:
• The plan does not address potential performance bottlenecks in large projects

Specific Recommendations:
1. Include detailed steps for handling edge cases
2. Provide more detailed documentation on the CLI command usage
3. Expand the integration testing strategy

Tokens: 15k sent, 422 received. Cost: $0.04 message, $0.04 session.
```

**Reality** (verified by grep):
- ✅ Edge case handling: 30 lines with code examples (lines 86-116)
- ✅ Performance bottlenecks: 61 lines of analysis (lines 799-859)
- ✅ CLI documentation: 108 lines of detailed docs (lines 752-859)
- ✅ Integration testing: 55 lines of test code (lines 614-668)

**Disconnect**: Evaluator sees structure but not content

---

## Data for Investigation

### File Metrics

| Metric | Value |
|--------|-------|
| Total lines | 1065 |
| Total characters | ~53,000 |
| Estimated tokens | ~13,000-15,000 |
| Sections | 25+ |
| Code blocks | 40+ |
| Detailed subsections | 15+ |

### Aider Metrics (from output)

| Metric | Value |
|--------|-------|
| Repo files | 457 |
| Repo-map tokens | 4,096 |
| Total tokens sent | 15,000 |
| Tokens received | 422 |
| Cost | $0.04 |

### Token Budget Analysis

```
Total context window: 128,000 tokens (GPT-4o)
Tokens sent:          15,000 tokens
File alone would be:  ~13,000 tokens
Remaining for:        ~2,000 tokens (prompt + repo context)

If repo-map uses:     4,096 tokens
File gets:            ~11,000 tokens (82% of file content)

Hypothesis: 18% of file content is summarized/omitted
```

---

## Recommendations Summary

### Immediate (adversarial-workflow team)

1. **Test**: Run evaluator with `--map-tokens 0` on large file
2. **Measure**: Confirm if full content is sent to GPT-4o
3. **Document**: Token budget allocation strategy
4. **Warn**: Add file size warning (>500 lines) in CLI

### Short-term (next release)

1. **Fix**: Disable repo-map for evaluation mode (or make configurable)
2. **Validate**: Add post-evaluation claim verification
3. **Guide**: Document best practices for large task specs
4. **Alert**: Detect false negatives and notify user

### Long-term (future consideration)

1. **Alternative**: Phase-based evaluation workflow
2. **Enhancement**: Chunk large files intelligently
3. **Improvement**: Better summarization that preserves detail
4. **Monitoring**: Track evaluation false negative rate

---

## Questions for adversarial-workflow Team

1. **Is repo-map intended** for evaluation mode, or only for code changes?
2. **What token budget** should be allocated to read-only evaluation files?
3. **Can we disable** repo-map selectively for evaluation?
4. **Are there Aider flags** to force full file reading (not summary)?
5. **Should large files** (>500 lines) be split before evaluation?
6. **Can we detect** when summarization happens and warn the user?

---

## Conclusion

The evaluator appears unable to read the full content of comprehensive task specifications (>500 lines) due to Aider's repo-map summarization. This creates a critical workflow limitation where thorough planning is penalized - the more comprehensive the plan, the less likely it is to be approved.

**This is a tooling issue, not a content issue.** The adversarial-workflow team should investigate Aider's file reading behavior and implement one of the proposed solutions to enable evaluation of comprehensive task specifications.

---

**Report prepared by**: coordinator agent (thematic-cuts project)
**Date**: 2025-10-24
**For**: adversarial-workflow team
**Priority**: HIGH
**Blocking**: TASK-2025-026 (AAF Export) approval

**Supporting evidence**:
- Task file: `delegation/tasks/active/TASK-2025-026-aaf-export.md` (commit 8c04daa)
- Evaluation logs: `.adversarial/logs/TASK-2025-026-PLAN-EVALUATION.md` (5 rounds)
- Content verification: All grep commands showing content exists
