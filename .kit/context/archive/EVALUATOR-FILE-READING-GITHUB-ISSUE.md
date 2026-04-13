# GitHub Issue: Evaluator Cannot Read Full Content of Large Files

**For**: https://github.com/movito/adversarial-workflow/issues

---

## Title

```
Evaluator fails to read full content of large task files (>500 lines), causing false NEEDS_REVISION loops
```

---

## Labels

- `bug`
- `evaluation`
- `aider`
- `priority: high`

---

## Issue Body

```markdown
## Description

The evaluator (GPT-4o via Aider) appears unable to read the full content of large task specification files, causing it to repeatedly claim content is missing when it verifiably exists in the file. This creates an infinite NEEDS_REVISION loop where comprehensive plans can never be approved.

## Impact

**Severity**: HIGH - Blocks approval of comprehensive task specifications

**User Impact**:
- Cannot get detailed task specifications approved (>500 lines)
- Forced to choose: incomplete plans (get approved) vs comprehensive plans (stuck in loop)
- Undermines adversarial workflow value proposition

**Frequency**: Any task specification >500 lines will likely hit this issue

## Evidence

**Test case**: TASK-2025-026 (AAF Export specification)
- File size: 1,065 lines
- Evaluation rounds: 5 (all NEEDS_REVISION)
- Content added: All requested content verified to exist via grep

**Evaluator claims vs reality**:

| Evaluator Claim | Reality | Proof |
|----------------|---------|-------|
| "lacks details on handling edge cases" | ✅ 30 lines with code examples exist | `grep -A 30 "Error Handling Strategy" file.md` |
| "integration testing strategy not fleshed out" | ✅ 55 lines of test implementation exist | `grep -A 55 "Automated AAF Validation" file.md` |
| "no mention of documentation" | ✅ 108 lines of README docs exist | `grep -A 108 "User Documentation" file.md` |
| "doesn't address performance bottlenecks" | ✅ 61 lines of performance analysis exist | `grep -A 61 "Large Project Efficiency" file.md` |

## Root Cause Hypothesis

**Aider repo-map summarization**:

From Aider output:
```
Repo-map: using 4096 tokens, auto refresh
Added delegation/tasks/active/TASK-2025-026-aaf-export.md to the chat (read-only).
Tokens: 15k sent, 422 received.
```

**Analysis**:
- File size: 1,065 lines ≈ 13,000-15,000 tokens
- Tokens sent: 15,000 total (includes prompt + file + repo context)
- Repo-map: 4,096 tokens

**Conclusion**: Not enough tokens for full file content. Aider likely sending summary instead of full text.

**This explains**:
- Evaluator sees section headings but not detailed content within sections
- Claims content is missing when only reading structure, not substance
- Each round adds content, but evaluator never sees it

## Reproduction Steps

1. Create task specification file with >500 lines containing:
   - Detailed error handling section (30+ lines)
   - Comprehensive testing strategy (50+ lines)
   - Documentation plan (100+ lines)
   - Performance analysis (60+ lines)

2. Run evaluator:
   ```bash
   adversarial evaluate task-file.md
   ```

3. Observe: Evaluator returns NEEDS_REVISION claiming sections lack detail

4. Verify content exists:
   ```bash
   grep -A 30 "Error Handling" task-file.md  # Shows detailed content
   ```

5. Add more detail to the sections as requested

6. Re-run evaluator

7. **Observe**: Same claims of missing content despite verification

8. **Result**: Infinite loop - never achieves APPROVED verdict

## Proposed Solutions

### Solution 1: Disable Repo-Map for Evaluation (Quick Fix)

**Change**: Add flag to disable repo-map summarization in evaluate command

```python
# In adversarial_workflow/commands/evaluate.py
aider_cmd = [
    "aider",
    "--model", "gpt-4o",
    "--no-git",
    "--map-tokens", "0",  # <-- ADD THIS: Disable repo-map
    # ... other flags
]
```

**Expected outcome**: Aider sends full file content instead of summary

**Risk**: May hit token limits on very large files (>2000 lines)

### Solution 2: Detect and Warn (User Experience)

**Change**: Detect large files and warn user about potential summarization

```python
def evaluate(task_file):
    line_count = count_lines(task_file)

    if line_count > 500:
        print(f"⚠️  Large task file detected ({line_count} lines)")
        print("Note: Files >500 lines may be summarized by evaluator")
        print("Recommendation: Split into phase-specific files or proceed with manual review")
```

### Solution 3: Post-Evaluation Verification (Detection)

**Change**: Verify evaluator claims against actual file content

```python
def verify_evaluation_claims(task_file, evaluation_log):
    """Check if evaluator's missing content claims are accurate."""

    claims = parse_missing_content_claims(evaluation_log)

    for claim in claims:
        keyword = extract_keyword(claim)
        exists = search_in_file(task_file, keyword)

        if exists:
            print(f"⚠️  False negative: '{keyword}' exists at line {exists.line}")
            print("   Evaluator may not be reading full file content")
```

### Solution 4: Phase-Based Evaluation (Alternative Workflow)

**Change**: Support evaluating sections/phases separately instead of whole file

```bash
# Instead of evaluating entire 1000-line file:
adversarial evaluate task-file.md

# Evaluate phases separately:
adversarial evaluate task-file.md --section "Phase 1: Dependencies"
adversarial evaluate task-file.md --section "Phase 2: Implementation"
# etc.
```

## Recommended Immediate Action

**Test Solution 1**: Add `--map-tokens 0` flag to evaluate command and verify if:
1. Full file content is sent to GPT-4o
2. Evaluator recognizes detailed content within sections
3. False negatives are eliminated

## Environment

- **adversarial-workflow version**: 0.3.2 (commit 8f0146d5)
- **Aider version**: 0.86.1
- **Model**: gpt-4o
- **Platform**: macOS (Darwin 24.6.0)
- **Python**: 3.11

## Additional Context

**Detailed investigation report**: Available in originating project at:
`delegation/handoffs/EVALUATOR-FILE-READING-LIMITATION-2025-10-24.md`

This report includes:
- Complete token budget analysis
- All grep verification commands
- 5 rounds of evaluation output comparison
- Detailed hypotheses and evidence

**Related resolved issues**:
- ✅ Wrapper verdict detection bug (fixed in 8f0146d5)
- ✅ Untracked files issue (resolved by committing before evaluation)

## Questions for Investigation

1. Is repo-map intended for evaluation mode, or only for code editing?
2. What token budget should be allocated to read-only evaluation files?
3. Can repo-map be disabled selectively for evaluation mode?
4. Are there Aider flags to force full file reading without summarization?
5. At what file size does Aider trigger summarization mode?
6. Can we detect when summarization happens and warn the user?

## Success Criteria

After fix is implemented:

- [ ] Evaluator can read full content of 1,000+ line files
- [ ] Evaluator feedback references actual content, not just structure
- [ ] False negatives eliminated (doesn't claim missing content that exists)
- [ ] Comprehensive task specifications can achieve APPROVED verdict
- [ ] Warning displayed for files that may be summarized

---

**Reported by**: thematic-cuts project coordinator agent
**Date**: 2025-10-24
**Priority**: HIGH (blocks core workflow)
**Test case**: TASK-2025-026 (1,065 lines, 5 evaluation rounds, all false negatives)
```

---

## Copy-Paste Ready Version for GitHub

The markdown above is ready to paste directly into a new GitHub issue at:
https://github.com/movito/adversarial-workflow/issues/new

Simply:
1. Copy the **Title** section (first code block)
2. Add suggested **Labels** manually in GitHub UI
3. Copy the **Issue Body** section (main markdown content)
4. Submit

---

## Alternative: Simplified Version

If you want a shorter, more concise issue, here's a condensed version:

````markdown
## Summary

The evaluator cannot read the full content of large task specification files (>500 lines), causing it to repeatedly request content that already exists. This creates an infinite NEEDS_REVISION loop.

## Evidence

**Test case**: 1,065-line task specification evaluated 5 times
- Each round: Evaluator claims content is missing
- Reality: All requested content verifiably exists (grep confirmed)
- Aider output: "Tokens: 15k sent" for ~13k-15k token file

**Hypothesis**: Aider's repo-map (4096 tokens) summarizes the file instead of sending full content.

## Impact

- ✅ Works: Task specs <300 lines
- ❌ Broken: Task specs >500 lines (stuck in NEEDS_REVISION loop)
- 🚫 Blocks: Comprehensive planning in adversarial workflow

## Quick Fix Suggestion

Add `--map-tokens 0` to Aider command in evaluate mode to disable summarization.

## Reproduction

1. Create 600+ line task file with detailed sections
2. Run `adversarial evaluate file.md`
3. Observe: Claims missing content
4. Verify: `grep "section name" file.md` shows content exists
5. Add more detail
6. Re-run: Same claims
7. Result: Infinite loop

**Full investigation**: `delegation/handoffs/EVALUATOR-FILE-READING-LIMITATION-2025-10-24.md` in test project
````

---

Both versions ready to use. Which format would you prefer for the GitHub issue?
