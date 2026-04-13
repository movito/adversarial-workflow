# TASK-2025-0037: Adversarial-Workflow Output Validation & File Reading Enhancement

**Target Repository**: adversarial-workflow
**Created By**: thematic-cuts project (coordinator agent)
**Date Created**: 2025-10-30
**Priority**: HIGH
**Estimated Duration**: 2-3 hours
**Complexity**: MEDIUM

---

## Executive Summary

Implement output validation and investigate file reading limitations in adversarial-workflow's evaluation system. The thematic-cuts team partially fixed false-positive evaluations by disabling git/repo-map, but discovered deeper issues with Aider's file reading behavior that require upstream investigation.

**User Impact**:
- Evaluators silently fail, reporting empty evaluations as successful
- Large files (>500 lines) not fully processed by GPT-4o
- Users proceed with unvalidated plans, discovering issues during implementation

**Business Value**:
- Catch evaluation failures early (defensive programming)
- Improve reliability for large task specifications
- Better user confidence in evaluation system

---

## Background & Context

### What Thematic-Cuts Team Completed ✅

**Commits to adversarial-workflow** (v0.3.2):
- Added `--no-git` flag to prevent git scanning issues
- Added `--map-tokens 0` flag to disable repo-map summarization
- Updated evaluation scripts

**Testing & Verification**:
- Verified flags work correctly (git/repo-map disabled)
- Discovered deeper file reading issue
- Documented workarounds for large files (>500 lines)

**Documentation Created**:
- `delegation/handoffs/EVALUATOR-FIX-VERIFICATION-RESULTS-2025-10-24.md` (comprehensive test results)
- `delegation/handoffs/EVALUATOR-FILE-READING-LIMITATION-2025-10-24.md` (root cause analysis)
- `delegation/handoffs/EVALUATOR-FILE-READING-GITHUB-ISSUE.md` (issue report draft)

### What Remains to Be Done ❌

**Phase 1: Output Validation** (Originally planned, not implemented)
- Validate evaluation logs contain actual GPT-4o content
- Detect and report empty/failed evaluations explicitly
- Exit with proper error codes when evaluation fails

**Phase 2: File Reading Investigation** (New discovery)
- Investigate why 1,065-line files only send 12k tokens (should be ~15k)
- Determine if Aider `--read` flag has size/line limits
- Test GPT-4o attention patterns with large contexts

**Phase 3: Content Verification** (Enhancement)
- Verify evaluator claims against actual file content
- Warn when "missing content" actually exists
- Reduce false-negative feedback loops

---

## Problem Statement

### Issue 1: Silent Evaluation Failures (Original Bug)

**Symptom**: Evaluation command reports "✅ Evaluation approved!" when no evaluation occurred

**Example**:
```bash
$ adversarial evaluate task.md

Warning: Input is not a terminal (fd=0).
Unable to list files in git repo: BadObject: b'4ac2421...'
Is your git repo corrupted?

=== Plan evaluation complete ===
✅ Evaluation approved!  # ← FALSE POSITIVE
```

**Log File**: 505 bytes (git warnings only, no GPT-4o output)

**Impact**: Users proceed with unreviewed plans, waste implementation time

**Status**: ✅ Mitigated by `--no-git` flag, but validation still needed

### Issue 2: Large File Reading Limitations (New Discovery)

**Symptom**: GPT-4o doesn't process full file content for large specifications

**Evidence**:
- File: 1,065 lines (~4,000 words)
- Expected tokens: ~13-15k
- Actual tokens sent: 12k (with repo-map disabled)
- Evaluator claims content missing that verifiably exists

**Example Claims vs Reality**:

| Evaluator Claim | Reality | Proof |
|----------------|---------|-------|
| "lacks specific details on edge cases" | ✅ 30 lines of edge case handling | Lines 86-116 |
| "error handling not fully fleshed out" | ✅ Detailed error messages with examples | Lines 100-116 |
| "no mention of integration with existing systems" | ✅ 60 lines of CLI integration | Lines 738-797 |
| "no mention of how implementation will be documented" | ✅ 150+ lines of documentation plan | Lines 752-859 |

**Verification**:
```bash
# All content exists in file
$ grep -n "Error Handling Strategy" TASK-2025-026-aaf-export.md
86:#### Error Handling Strategy

$ wc -l <(sed -n '86,116p' TASK-2025-026-aaf-export.md)
31 lines  # Content exists!
```

**Impact**:
- Endless revision loops requesting existing content
- Manual approval needed for comprehensive plans
- Reduced confidence in evaluation system

**Status**: ❌ Unresolved - Requires investigation

---

## Technical Requirements

### Requirement 1: Output Validation Function

**Objective**: Detect when evaluation failed to produce actual content

**Implementation Location**:
- `adversarial_workflow/commands/evaluate.py`
- OR `adversarial_workflow/core/evaluation.py`

**Function Specification**:

```python
def validate_evaluation_output(log_file_path: str) -> tuple[bool, str]:
    """
    Validate that evaluation log contains actual GPT-4o evaluation content.

    Args:
        log_file_path: Path to evaluation log file

    Returns:
        (is_valid, message): True if valid evaluation, False if failed

    Examples:
        >>> validate_evaluation_output("valid.log")
        (True, "Evaluation output valid")

        >>> validate_evaluation_output("empty.log")
        (False, "Log file too small (505 bytes), likely failed")
    """
    with open(log_file_path, 'r') as f:
        content = f.read()

    # Check 1: Minimum content size
    # Working evaluations: >1000 bytes
    # Failed evaluations: <600 bytes (just warnings)
    if len(content) < 500:
        return False, f"Log file too small ({len(content)} bytes), likely failed"

    # Check 2: Required evaluation sections
    required_sections = [
        "OVERALL ASSESSMENT",
        "EXECUTIVE SUMMARY"
    ]

    missing_sections = [s for s in required_sections if s not in content]
    if missing_sections:
        return False, f"Missing evaluation sections: {', '.join(missing_sections)}"

    # Check 3: Known failure patterns
    failure_patterns = [
        ("Unable to list files in git repo", "Git repository scanning failed"),
        ("Is your git repo corrupted", "Git repository error"),
        ("BadObject", "Git object error"),
        ("Error reading", "File reading error")
    ]

    for pattern, description in failure_patterns:
        if pattern in content and len(content) < 1000:
            # Small file with error pattern = evaluation didn't run
            return False, f"Aider failed: {description}"

    # Check 4: Token usage (indicates GPT-4o actually ran)
    if "Tokens:" not in content and "tokens" not in content.lower():
        return False, "No token usage found - GPT-4o may not have run"

    # Check 5: Minimum token count
    # Typical evaluations: 400-1000+ tokens received
    # Failed runs: 0 tokens or very few
    import re
    token_match = re.search(r'(\d+)k?\s+sent.*?(\d+)\s+received', content)
    if token_match:
        tokens_received = int(token_match.group(2))
        if tokens_received < 100:
            return False, f"Suspiciously low token count ({tokens_received} received)"

    return True, "Evaluation output valid"
```

**Integration**:

```python
def evaluate_plan(task_file: str) -> int:
    """
    Evaluate a task plan using Aider + GPT-4o.

    Returns:
        0 if evaluation succeeded
        1 if evaluation failed or validation failed
    """
    # ... existing code to run aider ...

    # Run aider evaluation
    result = subprocess.run(aider_cmd, ...)

    # CRITICAL: Validate output before reporting success
    is_valid, message = validate_evaluation_output(log_file_path)

    if not is_valid:
        print(f"❌ Evaluation failed: {message}")
        print(f"Log file: {log_file_path}")
        print("\nPlease check the log file for details.")
        return 1  # Non-zero exit code
    else:
        print(f"✅ Evaluation completed successfully!")
        print(f"Review output in: {log_file_path}")
        return 0
```

**Test Cases**:

```python
def test_validate_evaluation_output():
    # Test 1: Valid evaluation (>1000 bytes, has sections)
    assert validate_evaluation_output("tests/fixtures/valid_eval.log") == (True, "Evaluation output valid")

    # Test 2: Empty file with git errors
    assert validate_evaluation_output("tests/fixtures/git_error.log")[0] == False

    # Test 3: Missing required sections
    assert validate_evaluation_output("tests/fixtures/incomplete.log")[0] == False

    # Test 4: No token usage
    assert validate_evaluation_output("tests/fixtures/no_tokens.log")[0] == False
```

---

### Requirement 2: File Reading Investigation

**Objective**: Understand why large files aren't fully processed

**Investigation Tasks**:

1. **Test Aider `--read` Flag Behavior**
   ```bash
   # Create test file with markers every 100 lines
   for i in {1..2000}; do
       if [ $((i % 100)) -eq 0 ]; then
           echo "MARKER_LINE_$i"
       else
           echo "Content line $i"
       fi
   done > test_large_file.txt

   # Run Aider and ask it to list all markers
   aider --model gpt-4o --read test_large_file.txt --message "List all MARKER_LINE_ entries you see"

   # Check: Does it see all 20 markers or only first N?
   ```

2. **Check Token Budget Allocation**
   ```bash
   # Test: How are tokens allocated in Aider?
   # - Prompt instructions: X tokens
   # - File content: Y tokens
   # - System prompts: Z tokens
   # Total should match "tokens sent" in log
   ```

3. **Test File Size Limits**
   ```bash
   # Test files of increasing size
   # 100 lines: X tokens sent
   # 500 lines: Y tokens sent
   # 1000 lines: Z tokens sent
   # 2000 lines: ? tokens sent

   # Look for plateaus indicating limits
   ```

4. **Review Aider Source Code**
   ```bash
   # Check aider repository for file reading implementation
   # Look for: line limits, byte limits, token limits
   grep -r "read.*file" aider/
   grep -r "max.*lines" aider/
   grep -r "truncate" aider/
   ```

**Expected Findings**:
- Identify if Aider truncates large files
- Determine optimal file size for reliable evaluation (<500 lines?)
- Document any workarounds needed

---

### Requirement 3: Token Count Verification (Enhancement)

**Objective**: Warn users when token count seems too low

**Implementation**:

```python
def estimate_file_tokens(file_path: str) -> int:
    """
    Estimate tokens for a file using rough approximation.

    Estimation: ~1 token per 4 characters (OpenAI's rule of thumb)
    """
    with open(file_path, 'r') as f:
        char_count = len(f.read())

    return char_count // 4  # Rough estimate


def verify_token_count(task_file: str, tokens_sent: int) -> None:
    """
    Warn if token count is suspiciously low for file size.
    """
    expected_tokens = estimate_file_tokens(task_file)

    if tokens_sent < expected_tokens * 0.7:  # 30% tolerance
        print(f"⚠️  Token count lower than expected:")
        print(f"   Sent: {tokens_sent:,} tokens")
        print(f"   Expected: ~{expected_tokens:,} tokens")
        print(f"   File may not be fully processed by evaluator")
```

**Integration**:

```python
def evaluate_plan(task_file: str) -> int:
    # ... run aider ...

    # Extract token count from log
    tokens_sent = extract_token_count(log_file_path)

    # Verify token count
    verify_token_count(task_file, tokens_sent)

    # ... continue with validation ...
```

---

### Requirement 4: Content Verification (Enhancement)

**Objective**: Catch false-negative claims ("missing" content that exists)

**Implementation**:

```python
def verify_evaluation_claims(task_file: str, evaluation_log: str) -> list[str]:
    """
    Check if evaluator claims content is missing that actually exists.

    Returns:
        List of warnings about potentially false claims
    """
    warnings = []

    with open(task_file, 'r') as f:
        task_content = f.read().lower()

    with open(evaluation_log, 'r') as f:
        eval_content = f.read()

    # Extract "missing" claims from evaluation
    missing_patterns = [
        r'no mention of (.+)',
        r'lacks (.+)',
        r'missing (.+)',
        r'does not include (.+)',
        r'should add (.+)'
    ]

    for pattern in missing_patterns:
        matches = re.finditer(pattern, eval_content, re.IGNORECASE)
        for match in matches:
            claimed_missing = match.group(1).strip()

            # Check if keywords from claim exist in task file
            keywords = extract_keywords(claimed_missing)
            found_keywords = [kw for kw in keywords if kw in task_content]

            if len(found_keywords) >= len(keywords) * 0.7:  # 70% keywords found
                warnings.append(
                    f"⚠️  Evaluator claims missing: '{claimed_missing}'\n"
                    f"   But file contains keywords: {', '.join(found_keywords)}\n"
                    f"   Consider manual review - content may exist"
                )

    return warnings
```

**User Experience**:

```bash
$ adversarial evaluate task.md

✅ Evaluation completed successfully!
Review output in: .adversarial/logs/task-evaluation.log

⚠️  Note: 3 potential false-negative claims detected:
   - Evaluator claims missing: 'error handling details'
     But file contains keywords: error, handling, exception, validation
     Consider manual review - content may exist
```

---

## Implementation Plan

### Phase 1: Output Validation (High Priority) - 45-60 minutes

**Tasks**:
1. ✅ Locate evaluation command code (5 min)
2. ✅ Implement `validate_evaluation_output()` function (20 min)
3. ✅ Integrate validation into evaluation flow (10 min)
4. ✅ Write unit tests (15 min)
5. ✅ Manual testing with known cases (10 min)

**Acceptance Criteria**:
- Empty log files (git errors) report failure, not success
- Exit code is non-zero when validation fails
- Success messages only shown for valid evaluations
- All test cases pass

**Files Modified**:
- `adversarial_workflow/commands/evaluate.py` (or equivalent)
- `tests/test_evaluate.py` (new or updated)
- `tests/fixtures/` (add test log files)

---

### Phase 2: File Reading Investigation (High Priority) - 60-90 minutes

**Tasks**:
1. ✅ Create test files with markers (15 min)
2. ✅ Run marker tests with various file sizes (20 min)
3. ✅ Review Aider source code for limits (30 min)
4. ✅ Document findings and recommendations (15-30 min)

**Acceptance Criteria**:
- Identified if/where Aider truncates files
- Documented file size limits for reliable evaluation
- Recommendations for handling large files

**Deliverables**:
- Investigation report (markdown)
- Test results with various file sizes
- Recommended file size limits
- Workarounds if needed

---

### Phase 3: Token Verification (Medium Priority) - 30 minutes

**Tasks**:
1. ✅ Implement `estimate_file_tokens()` (10 min)
2. ✅ Implement `verify_token_count()` (10 min)
3. ✅ Integrate into evaluation flow (5 min)
4. ✅ Test with various file sizes (5 min)

**Acceptance Criteria**:
- Warnings shown when token count is suspiciously low
- No false warnings for normal files
- Helpful guidance for users

---

### Phase 4: Content Verification (Low Priority / Optional) - 45-60 minutes

**Tasks**:
1. ✅ Implement claim extraction logic (20 min)
2. ✅ Implement keyword matching (15 min)
3. ✅ Integrate warnings into output (10 min)
4. ✅ Test with known false-negative cases (15 min)

**Acceptance Criteria**:
- False-negative claims detected and warned
- No false warnings on legitimate missing content
- Clear actionable warnings for users

**Note**: This is an enhancement, not critical for basic functionality

---

## Testing Strategy

### Test Case 1: Empty Log (Git Error)

**Setup**:
```bash
# Create empty log with only git errors (505 bytes)
cat > test_empty.log << 'EOF'
Warning: Input is not a terminal (fd=0).
────────────────────────────────────────────────────────────────────────────────
Unable to list files in git repo: BadObject: b'4ac2421...'
Is your git repo corrupted?

=== Plan evaluation complete ===
EOF
```

**Expected Result**:
```bash
$ adversarial evaluate task.md
❌ Evaluation failed: Missing evaluation sections: OVERALL ASSESSMENT, EXECUTIVE SUMMARY
Log file: test_empty.log
Please check the log file for details.

$ echo $?
1  # Non-zero exit code
```

---

### Test Case 2: Valid Evaluation (Working)

**Setup**: Use known working evaluation log (>1000 bytes, has sections)

**Expected Result**:
```bash
$ adversarial evaluate task.md
✅ Evaluation completed successfully!
Review output in: .adversarial/logs/task-evaluation.log

$ echo $?
0  # Success exit code
```

---

### Test Case 3: Large File (>500 lines)

**Setup**: Create 1,065-line task file (like TASK-2025-026)

**Expected Result**:
```bash
$ adversarial evaluate large_task.md

⚠️  Token count lower than expected:
   Sent: 12,000 tokens
   Expected: ~15,000 tokens
   File may not be fully processed by evaluator

✅ Evaluation completed successfully!
```

---

### Test Case 4: False Negative Claims

**Setup**: Evaluation claims missing content that exists

**Expected Result**:
```bash
$ adversarial evaluate task.md

✅ Evaluation completed successfully!

⚠️  Note: 2 potential false-negative claims detected:
   - Evaluator claims missing: 'error handling'
     But file contains keywords: error, handling, exception
     Consider manual review - content may exist
```

---

## Success Criteria

### Must Have (Required for Completion)

- ✅ Output validation function implemented and tested
- ✅ Validation integrated into evaluation flow
- ✅ Empty/failed evaluations report failure (not success)
- ✅ Exit codes correct (0 = success, 1 = failure)
- ✅ Unit tests cover validation logic
- ✅ Manual testing with known broken/working cases passes

### Should Have (High Value)

- ✅ File reading investigation completed
- ✅ Token count verification warnings implemented
- ✅ Documented file size recommendations
- ✅ Test results with various file sizes

### Nice to Have (Optional Enhancements)

- Content verification for false-negative claims
- Enhanced error messages with troubleshooting tips
- Integration tests with actual Aider calls
- Documentation updates (README, troubleshooting guide)

---

## Risk Assessment

**Risk Level**: LOW-MEDIUM

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Validation breaks existing workflows | Low | Medium | Thorough testing with working evaluations |
| False positives (valid evals marked as failed) | Low | High | Conservative validation rules, test with many examples |
| File reading investigation inconclusive | Medium | Low | Document findings even if no clear solution |
| Performance impact from validation | Very Low | Low | Validation is fast (<100ms) |
| Breaking changes to evaluation API | Low | Medium | Make validation opt-in initially |

**Mitigation Strategy**:
- Test with 10+ known working evaluations
- Test with 5+ known failing evaluations
- Beta test with thematic-cuts team before release
- Document all changes in changelog

---

## References & Documentation

### From Thematic-Cuts Team

**Verification Reports**:
- `delegation/handoffs/EVALUATOR-FIX-VERIFICATION-RESULTS-2025-10-24.md` - Test results after partial fix
- `delegation/handoffs/EVALUATOR-FILE-READING-LIMITATION-2025-10-24.md` - Root cause analysis
- `delegation/handoffs/EVALUATOR-FILE-READING-GITHUB-ISSUE.md` - Issue report draft

**Original Task**:
- `delegation/tasks/active/TASK-2025-027-fix-evaluator-false-positive.md` - Original specification

**Test Files Available**:
- `.adversarial/logs/TASK-2025-017-investigation-evaluation.log` - Working example (4,760 bytes)
- `.adversarial/logs/TASK-2025-026-PLAN-EVALUATION.md` - Broken example (505 bytes)
- `delegation/tasks/active/TASK-2025-026-aaf-export.md` - Large file test case (1,065 lines)

### Technical Context

**Current adversarial-workflow Version**: v0.3.2
**Aider Version**: v0.86.1
**Model**: gpt-4o
**Environment**: macOS, Python 3.11

**Flags Already Added** (by thematic-cuts team):
```bash
aider \
  --model gpt-4o \
  --yes-always \
  --no-git \           # ← Added in v0.3.2
  --map-tokens 0 \     # ← Added in v0.3.2
  --read "$task_file"
```

---

## Deliverables Checklist

### Code
- [ ] `validate_evaluation_output()` function implemented
- [ ] Validation integrated into evaluation flow
- [ ] Token count verification implemented
- [ ] Content verification implemented (optional)

### Tests
- [ ] Unit tests for validation function (5+ test cases)
- [ ] Integration tests with Aider (3+ scenarios)
- [ ] Test fixtures (working/broken logs)

### Documentation
- [ ] Investigation report (file reading behavior)
- [ ] Updated README (if needed)
- [ ] Changelog entry
- [ ] Troubleshooting guide (if needed)

### Verification
- [ ] All test cases pass
- [ ] No regressions on existing evaluations
- [ ] Thematic-cuts team beta testing complete

---

## Timeline

**Total Estimated Time**: 2-3 hours

- **Phase 1** (Output Validation): 45-60 minutes - **HIGH PRIORITY**
- **Phase 2** (File Reading Investigation): 60-90 minutes - **HIGH PRIORITY**
- **Phase 3** (Token Verification): 30 minutes - **MEDIUM PRIORITY**
- **Phase 4** (Content Verification): 45-60 minutes - **OPTIONAL**

**Recommended Approach**:
1. Start with Phase 1 (highest impact, lowest risk)
2. Then Phase 2 (understand root cause)
3. Add Phase 3 if time allows (nice enhancement)
4. Consider Phase 4 for future version (less critical)

---

## Questions for adversarial-workflow Team

1. **File Reading**: Are there known limits in Aider's `--read` flag? Line count? Byte count? Token count?

2. **Token Budget**: How are tokens allocated in Aider evaluations? Prompt vs file content vs system?

3. **Best Practices**: What's the recommended maximum file size for reliable evaluation?

4. **API Design**: Should validation be opt-in (`--validate-output` flag) or always-on?

5. **Error Handling**: Preferred error message style? Current messages seem inconsistent.

---

## Contact

**Created By**: Coordinator agent (thematic-cuts project)
**Contact**: Fredrik (via thematic-cuts repository)
**Date**: 2025-10-30
**Status**: Ready for implementation

**This task can be implemented independently** - all context and requirements are included in this document.

---

## Appendix: Example Logs

### Example 1: Failed Evaluation (Empty Log)

```
Warning: Input is not a terminal (fd=0).
────────────────────────────────────────────────────────────────────────────────
Unable to list files in git repo: BadObject: b'4ac2421d3db8d26bb3cfb4c26bafa9ec7d231892'
Is your git repo corrupted?
Unable to read git repository, it may be corrupt?
BadObject: b'4ac2421d3db8d26bb3cfb4c26bafa9ec7d231892'

=== Plan evaluation complete ===
```

**Size**: 505 bytes
**Issue**: No GPT-4o output, should fail validation

---

### Example 2: Successful Evaluation (Working Log)

```
Aider v0.86.1
Main model: gpt-4o with diff edit format
Weak model: gpt-4o-mini
Git repo: none
Repo-map: disabled

OVERALL ASSESSMENT
APPROVED

EXECUTIVE SUMMARY
This task specification for AAF export functionality is comprehensive and well-structured...
[... 4,500 more bytes of detailed evaluation ...]

Tokens: 11k sent, 474 received. Cost: $0.03 message, $0.03 session.
```

**Size**: 4,760 bytes
**Issue**: None - should pass validation

---

## Version History

- **v1.0** (2025-10-30): Initial task creation for adversarial-workflow team
