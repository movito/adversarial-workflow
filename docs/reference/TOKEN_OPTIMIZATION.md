# Token Optimization: Making AI Code Review Affordable

This document explains how the adversarial workflow achieves **10-20x cost reduction** compared to standard Aider usage through strategic token management.

## Table of Contents

- [The Token Problem](#the-token-problem)
- [The --read vs --files Difference](#the---read-vs---files-difference)
- [Single-Shot Invocations](#single-shot-invocations)
- [Measuring Token Usage](#measuring-token-usage)
- [Optimization Strategies](#optimization-strategies)
- [Real Cost Comparisons](#real-cost-comparisons)

---

## The Token Problem

### What Are Tokens?

AI models charge based on **tokens** - roughly 4 characters or 0.75 words each.

**Example costs** (GPT-4o, as of 2024):
- **Input tokens**: $5 per 1M tokens (~$0.005 per 1K)
- **Output tokens**: $15 per 1M tokens (~$0.015 per 1K)

**A typical Python file** (500 lines):
- ~2000 tokens

**A complete codebase** (100 files):
- ~200,000 tokens = **$1.00 just to read**

### The Standard Aider Pattern (Expensive)

```bash
# ❌ EXPENSIVE: Adds ALL files to context
aider --files src/**/*.py
```

**What happens**:
1. Aider reads ALL Python files (200K tokens input)
2. Keeps them in context for entire conversation
3. Each message repeats full context
4. Each response references full context

**Cost for 10-message conversation**:
- Input: 200K tokens × 10 messages = 2M tokens = **$10.00**
- Output: ~50K tokens = **$0.75**
- **Total: $10.75 for one task**

**For 20 tasks/month**: ~$215/month 💸

---

## The --read vs --files Difference

### Aider has TWO ways to access files:

#### 1. `--files` (adds to context, EXPENSIVE)

```bash
aider --files src/validation.py src/data_models.py
```

**Behavior**:
- Files added to **persistent context**
- AI can edit these files
- Files sent with **every message** in conversation
- Context accumulates (more files = more cost)

**Use when**:
- AI needs to EDIT these specific files
- Small number of files (<5)
- Short conversation (1-3 messages)

#### 2. `--read` (reference only, CHEAP)

```bash
aider --read docs/plan.md --read task.md
```

**Behavior**:
- Files sent **once** for reference
- AI CANNOT edit these files
- Not included in conversation context
- Used for context/instructions only

**Use when**:
- Providing instructions (task files, plans)
- Showing examples (test output, git diff)
- AI only needs to READ, not EDIT
- Large files or many files

### The Critical Difference

**Scenario**: Review a git diff against a task plan.

```bash
# ❌ EXPENSIVE WAY (100K tokens)
aider --files task.md --files approved-plan.md --files implementation.diff

# ✅ CHEAP WAY (5K tokens)
aider --read task.md --read approved-plan.md --read implementation.diff --message "Review this implementation"
```

**Why?**
- **Expensive**: All 3 files in context, repeated per message
- **Cheap**: All 3 files sent once, message is single-shot

**Cost difference**: **20x cheaper!**

---

## Single-Shot Invocations

### The Conversation Problem

**Traditional Aider usage** (multi-message):
```bash
$ aider --files src/validation.py

User: Add validation for Clip.name
AI: Sure! Here's the code... [50K tokens]

User: Also check timecode format
AI: Updated! Here's the code... [50K tokens]

User: What about start < end?
AI: Added! Here's the code... [50K tokens]
```

**Token cost**: 200K input + 150K output = **$1.75**

### The Single-Shot Pattern

**Adversarial workflow** (one message):
```bash
$ aider --read task.md --message "Implement according to plan" --yes

AI: [Reads plan, implements all requirements] [50K tokens]
```

**Token cost**: 10K input + 50K output = **$0.80**

**Savings**: 54% cheaper, and faster!

### How to Write Single-Shot Prompts

#### ❌ Bad (requires conversation)
```bash
aider --files validation.py
# Then interactively discuss changes
```

#### ✅ Good (complete instructions upfront)
```bash
aider --read TASK-2025-015-plan.md \
      --files tests/test_otio_integration.py \
      --message "Implement the 6 API fixes specified in the plan:
1. Line 188: Fix Clip constructor parameters
2. Line 197: Use duration_frames_otio() method
3-6: [etc, all fixes listed]

Follow SEARCH/REPLACE format from plan exactly." \
      --yes
```

**The prompt includes**:
- What to do (implement 6 fixes)
- Where (specific file and lines)
- How (SEARCH/REPLACE from plan)
- Acceptance (all 6 changes applied)

**Result**: AI completes in one response, no follow-up needed.

---

## Measuring Token Usage

### Aider Provides Token Counts

After each run, Aider shows:
```
Tokens: 12,450 sent, 3,200 received.
Cost: $0.11
```

**Track these** in your task logs!

### Example Token Tracking

From TASK-2025-015 completion summary:

```markdown
## Token Usage

**Phase 1: Plan Evaluation**
- Sent: 8,500 tokens (task file)
- Received: 2,100 tokens (evaluation)
- Cost: $0.07

**Phase 3: Code Review**
- Sent: 15,200 tokens (diff + plan + task)
- Received: 3,800 tokens (review)
- Cost: $0.13

**Phase 4: Test Validation**
- Sent: 6,100 tokens (test output + task)
- Received: 2,400 tokens (analysis)
- Cost: $0.06

**Total**: 26K tokens sent, 8K received = **$0.26 for entire task**
```

**Compare to standard Aider**: Would be ~$2.50 for same task (10x more).

### Where Tokens Go

| Component | Standard Aider | Adversarial | Savings |
|-----------|----------------|-------------|---------|
| Codebase context | 150-200K | 0K | **100%** |
| Task file | 3K × 10 msgs = 30K | 3K × 1 = 3K | **90%** |
| Git diff | 10K × 5 msgs = 50K | 10K × 1 = 10K | **80%** |
| Conversation | 100K | 5K | **95%** |
| **TOTAL** | **330K** | **18K** | **95%** |

---

## Optimization Strategies

### Strategy 1: Use --read for Everything Except Edit Targets

```bash
# ❌ DON'T: Add reference files to context
aider --files task.md --files plan.md --files src/validation.py

# ✅ DO: Read references, only add edit targets
aider --read task.md --read plan.md --files src/validation.py
```

**Savings**: 60-80% on input tokens.

### Strategy 2: Single-Shot with --yes Flag

```bash
# ❌ DON'T: Interactive conversation
aider --files src/validation.py
# Then multiple messages back and forth

# ✅ DO: Complete prompt + auto-approval
aider --files src/validation.py \
      --read plan.md \
      --message "[Complete instructions]" \
      --yes
```

**Savings**: 70-90% on repeated context.

### Strategy 3: Extract Minimal Context

```bash
# ❌ DON'T: Send entire test file (10K tokens)
aider --read tests/test_validation.py

# ✅ DO: Send only relevant excerpt (1K tokens)
aider --read <(grep -A 20 "test_clip_validation" tests/test_validation.py)
```

**Savings**: 90% on large reference files.

### Strategy 4: Reuse Artifacts

```bash
# Phase 3: Create diff once
git diff > .adversarial/artifacts/TASK-2025-016.diff

# Later phases: Read saved diff
aider --read .adversarial/artifacts/TASK-2025-016.diff
```

**Benefit**: Consistent review context, no re-generation cost.

### Strategy 5: Targeted File Editing

```bash
# ❌ DON'T: Add whole module
aider --files thematic_cuts/workflow/*.py  # 15 files!

# ✅ DO: Add only files that need changes
aider --files thematic_cuts/workflow/validator.py  # 1 file
```

**Savings**: Only pay for what you edit.

### Strategy 6: Use --no-gitignore Carefully

```bash
# ❌ DON'T: Accidentally include node_modules
aider --files src/**/*.js --no-gitignore  # Might hit node_modules!

# ✅ DO: Specific paths or use gitignore
aider --files src/components/*.js  # Controlled scope
```

**Disaster prevention**: Avoid accidentally sending 50MB of dependencies.

---

## Real Cost Comparisons

### Task 1: Simple Bug Fix

**Standard Aider approach**:
```bash
aider --files thematic_cuts/**/*.py

User: Fix the validation bug in Clip
[5 messages back and forth]
```

- Input: 180K tokens × 5 = 900K tokens
- Output: 25K tokens
- **Cost: $4.88**

**Adversarial approach**:
```bash
# Phase 1: Plan
aider --read task.md --message "Evaluate this plan" --yes
# 5K input, 2K output = $0.06

# Phase 3: Review
aider --read task.md --read plan.md --read diff.txt --message "Review implementation" --yes
# 12K input, 3K output = $0.11

# Phase 4: Validate
aider --read task.md --read test-output.txt --message "Validate test results" --yes
# 8K input, 2K output = $0.08
```

- Input: 25K tokens
- Output: 7K tokens
- **Cost: $0.25**

**Savings: 95% ($4.63 saved)**

### Task 2: Feature Implementation

**Standard Aider approach**:
```bash
aider --files src/**/*.py tests/**/*.py

User: Implement validation framework
User: Add error handling
User: Create tests
User: Fix the issues
User: Update docs
[15 messages total]
```

- Input: 250K × 15 = 3.75M tokens
- Output: 120K tokens
- **Cost: $20.55**

**Adversarial approach**:
```bash
# Phase 0: Investigation
aider --read task.md --message "Investigate current validation" --yes
# 8K + 3K = $0.085

# Phase 1: Plan
aider --read task.md --read investigation.md --message "Evaluate plan" --yes
# 15K + 5K = $0.15

# Phase 2: Implementation (with clear plan)
aider --files src/validation.py --files src/data_models.py \
      --read task.md --read plan.md \
      --message "Implement validation framework per plan" --yes
# 45K + 25K = $0.60

# Phase 3: Review
aider --read diff.txt --read plan.md --message "Review" --yes
# 18K + 4K = $0.15

# Phase 4: Tests
aider --files tests/test_validation.py --read plan.md \
      --message "Add tests per plan" --yes
# 22K + 12K = $0.29

# Phase 5: Validate
aider --read test-output.txt --message "Validate" --yes
# 9K + 3K = $0.09
```

- Input: 117K tokens
- Output: 52K tokens
- **Cost: $1.37**

**Savings: 93% ($19.18 saved)**

### Monthly Savings

**Typical project**: 20 tasks/month

| Approach | Cost/Task | Monthly Cost |
|----------|-----------|--------------|
| Standard Aider | $15.50 | **$310.00** |
| Adversarial | $1.20 | **$24.00** |
| **Savings** | **$14.30** | **$286.00** |

**ROI**: Pays for itself in first month if you do >2 tasks.

---

## Best Practices Summary

### ✅ DO

1. **Use --read for reference materials**
   - Task files
   - Plans
   - Git diffs
   - Test output
   - Documentation

2. **Use --files only for edit targets**
   - Files AI needs to modify
   - Keep to minimum necessary

3. **Write complete prompts**
   - All instructions upfront
   - Specific file:line references
   - Clear acceptance criteria

4. **Use --yes for automation**
   - Skip confirmation prompts
   - Single-shot execution
   - Faster + cheaper

5. **Track token usage**
   - Note costs in task logs
   - Compare approaches
   - Optimize over time

### ❌ DON'T

1. **Add whole codebase to context**
   - Never `--files src/**/*.py`
   - Too expensive
   - Unnecessary

2. **Have conversations**
   - Avoid interactive sessions
   - Each message repeats context
   - Plan first, execute once

3. **Repeat file reads**
   - Save artifacts to disk
   - Reuse in later phases
   - Avoid re-reading same content

4. **Include build artifacts**
   - Use .gitignore
   - Exclude node_modules, venv, etc.
   - Waste of tokens

5. **Trust AI's suggestions blindly**
   - AI might suggest `--files` for everything
   - You know your codebase
   - Override with --read when appropriate

---

## Advanced: Creating Token-Efficient Prompts

### Template: Plan Evaluation

```bash
aider \
  --model gpt-4o \
  --yes \
  --no-gitignore \
  --read "$TASK_FILE" \
  --message "You are an EVALUATOR agent performing critical design review.

**Your Role:**
[Clear role definition]

**Task File Provided:**
$TASK_FILE

**Your Evaluation Criteria:**
[Numbered list of what to check]

**Output Format:**
[Exact format specification]

[Detailed instructions for thoroughness]

Be critical but constructive. Your goal is to improve the plan." \
  --no-auto-commits
```

**Why this works**:
- Single invocation (--yes)
- Reference only (--read)
- Complete instructions (no follow-up)
- Structured output (easy to parse)

**Cost**: ~$0.05-0.10 per evaluation

### Template: Code Review

```bash
# Capture artifacts first (free)
git diff > .adversarial/artifacts/diff.txt
git diff --stat > .adversarial/artifacts/stats.txt

# Single review invocation
aider \
  --model gpt-4o \
  --yes \
  --no-gitignore \
  --read .adversarial/artifacts/diff.txt \
  --read .adversarial/artifacts/stats.txt \
  --read "$TASK_FILE" \
  --read "$PLAN_FILE" \
  --message "You are an EVALUATOR reviewing actual code changes.

**Files Provided:**
- Implementation: diff.txt (ACTUAL git changes)
- Statistics: stats.txt
- Requirements: $TASK_FILE
- Approved plan: $PLAN_FILE

**Review Criteria:**
1. Phantom Work Detection (CRITICAL)
   - Real code vs TODOs?
   [etc]

[Detailed instructions]

**Output Format:**
[Structured format]

Be thorough and critical. Phantom work is UNACCEPTABLE." \
  --no-auto-commits
```

**Cost**: ~$0.10-0.20 per review

### Template: Test Validation

```bash
# Run tests first (free)
pytest tests/ > .adversarial/artifacts/test-output.txt 2>&1

# Single validation invocation
aider \
  --model gpt-4o \
  --yes \
  --no-gitignore \
  --read .adversarial/artifacts/test-output.txt \
  --read "$TASK_FILE" \
  --message "You are a TEST-RUNNER analyzing results.

**Context:**
- Test output: test-output.txt
- Requirements: $TASK_FILE

**Your Validation:**
[Criteria]

**Output Format:**
[Format]

Be precise with test counts." \
  --no-auto-commits
```

**Cost**: ~$0.05-0.10 per validation

---

## Monitoring and Optimization

### Track These Metrics

Create a simple log:

```markdown
# token-usage.md

| Date | Task | Phase | Sent | Received | Cost | Notes |
|------|------|-------|------|----------|------|-------|
| 2025-10-13 | TASK-015 | Plan | 8.5K | 2.1K | $0.07 | Good |
| 2025-10-13 | TASK-015 | Review | 15.2K | 3.8K | $0.13 | Optimal |
| 2025-10-13 | TASK-015 | Validate | 6.1K | 2.4K | $0.06 | Good |
| 2025-10-14 | TASK-016 | Plan | 12K | 4K | $0.12 | Could reduce |
```

### Red Flags

**If you see**:
- Single invocation > 50K tokens sent → Too much context
- Cost > $1.00 per phase → Not using --read effectively
- Multiple messages in one phase → Need better planning

**Action**: Review your aider command, switch to --read where possible.

### Green Flags

**Good patterns**:
- Evaluation: 5-15K tokens, $0.05-0.15
- Review: 10-25K tokens, $0.10-0.30
- Validation: 5-15K tokens, $0.05-0.15
- **Total per task: $0.25-1.00**

---

## Conclusion

Token optimization is not about being cheap - it's about being **strategic**:

1. **Use the right tool**: `--read` for reference, `--files` for editing
2. **Plan before executing**: Single-shot is cheaper than conversation
3. **Minimize context**: Only include what AI needs to see
4. **Track and improve**: Measure token usage, optimize over time

**Result**: 10-20x cost reduction while maintaining (or improving) quality.

The adversarial workflow makes AI code review **affordable for everyone**, not just large teams with big budgets.
