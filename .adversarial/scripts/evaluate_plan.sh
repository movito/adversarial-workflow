#!/bin/bash
# SCRIPT_VERSION: 0.9.5
# Phase 1: Plan Evaluation - Critical design review

# Load environment variables from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Load configuration from .adversarial/config.yml
if [ ! -f .adversarial/config.yml ]; then
  echo "Error: Configuration file not found: .adversarial/config.yml"
  echo "Run 'adversarial init' first to initialize the workflow."
  exit 1
fi

# Parse config using grep/awk (simple YAML parsing)
EVALUATOR_MODEL=$(grep 'evaluator_model:' .adversarial/config.yml | awk '{print $2}')
TASK_DIR=$(grep 'task_directory:' .adversarial/config.yml | awk '{print $2}')
LOG_DIR=$(grep 'log_directory:' .adversarial/config.yml | awk '{print $2}')

TASK_FILE="$1"

if [ -z "$TASK_FILE" ]; then
  echo "Usage: ./.adversarial/scripts/evaluate_plan.sh <task_file_path>"
  echo ""
  echo "Example: ./.adversarial/scripts/evaluate_plan.sh ${TASK_DIR}TASK-2025-001.md"
  exit 1
fi

if [ ! -f "$TASK_FILE" ]; then
  echo "Error: Task file not found: $TASK_FILE"
  exit 1
fi

# Extract task number from filename
TASK_NUM=$(basename "$TASK_FILE" | grep -oE 'TASK-[0-9]+-[0-9]+' || basename "$TASK_FILE" .md)

echo "╔════════════════════════════════════════════╗"
echo "║   PHASE 1: PLAN EVALUATION                 ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Task File: $TASK_FILE"
echo "Task: $TASK_NUM"
echo "Model: $EVALUATOR_MODEL"
echo ""

# Create evaluation output file
EVAL_OUTPUT="${LOG_DIR}${TASK_NUM}-PLAN-EVALUATION.md"

echo "=== REVIEWER ($EVALUATOR_MODEL) ANALYZING PLAN ==="
echo ""

# Ensure log directory exists
mkdir -p "$LOG_DIR"

aider \
  --no-browser \
  --model "$EVALUATOR_MODEL" \
  --yes \
  --no-detect-urls \
  --no-git \
  --map-tokens 0 \
  --no-gitignore \
  --read "$TASK_FILE" \
  --message "You are a REVIEWER performing critical design review.

**Your Role:**
You are reviewing an implementation plan for this task. Your job is to provide constructive, thorough critique to improve the plan BEFORE implementation begins.

**Task File Provided:**
$TASK_FILE

**Your Evaluation Criteria:**

1. **Completeness Check**
   - Does the plan address ALL requirements?
   - Are all failing tests covered?
   - Are edge cases identified?
   - Is error handling specified?

2. **Design Quality**
   - Is the approach sound?
   - Are there simpler alternatives?
   - Will this scale/maintain well?
   - Are there hidden dependencies?

3. **Risk Assessment**
   - What could go wrong?
   - Are there breaking changes?
   - Impact on existing code?
   - Test coverage adequate?

4. **Implementation Clarity**
   - Is the plan detailed enough to implement?
   - Are file/function names specified?
   - Is the sequence of changes clear?
   - Are acceptance criteria defined?

5. **Missing Elements**
   - What's not addressed in the plan?
   - Are there unstated assumptions?
   - Dependencies on other tasks?
   - Documentation needs?

**Output Format:**

Please provide your evaluation in this EXACT format:

## Evaluation Summary
**Verdict:** [APPROVED / NEEDS_REVISION / REJECT]
**Confidence:** [HIGH / MEDIUM / LOW]
**Estimated Implementation Time:** [X hours/days]

## Strengths
- [What the plan does well]
- [Clear, specific, detailed approach]
- [Good decisions highlighted]

## Concerns & Risks
- [CRITICAL] [High-priority issues that must be addressed]
- [MEDIUM] [Important but not blocking]
- [LOW] [Nice-to-have improvements]

## Missing or Unclear
- [What needs clarification]
- [What needs to be added to the plan]
- [Unstated assumptions to make explicit]

## Specific Recommendations
1. [Concrete, actionable improvement]
2. [Alternative approaches to consider]
3. [Additional steps needed]

## Questions for Plan Author
1. [Question about design decision]
2. [Clarification needed on approach]
3. [Trade-off to discuss]

## Approval Conditions
[If NEEDS_REVISION: List specific changes needed for approval]
[If APPROVED: Any caveats or things to watch during implementation]

---

Be thorough, be critical, but be constructive. Your goal is to improve the plan, not to block progress unnecessarily.

If the plan is fundamentally sound but has minor issues, mark as APPROVED with caveats.
If the plan has significant gaps or risks, mark as NEEDS_REVISION with specific fixes.
Only use REJECT if the entire approach is flawed.

**IMPORTANT**: You are ONLY evaluating. Do NOT implement any code. Do NOT edit any files. Do NOT suggest file changes with SEARCH/REPLACE blocks. Only provide your written evaluation following the format above." \
  --no-auto-commits 2>&1 | tee "$EVAL_OUTPUT"

echo ""
echo "=== Plan evaluation complete ==="
echo ""
echo "Evaluation saved to: $EVAL_OUTPUT"
echo ""
echo "Next steps:"
echo "1. Review evaluation output above"
echo "2. Plan author addresses feedback and updates plan"
echo "3. Run this script again if NEEDS_REVISION"
echo "4. Proceed to implementation if APPROVED"
echo ""
