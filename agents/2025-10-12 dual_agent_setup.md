# Dual-Agent Development Setup

This document contains instructions for setting up a dual-agent development workflow using Claude Code for implementation and GPT-4 (via Aider) for code review and verification.

## Goal

Prevent "phantom work" by having one AI agent (Claude) implement features and another AI agent (GPT-4) critically review the actual changes made.

## Prerequisites

Before starting, ensure you have:
- Git initialized in your project
- Python 3.8+ installed
- Node.js/npm (if applicable to your project)
- Aider installed: `pip install aider-chat`
- OpenAI API key set: `export OPENAI_API_KEY=your_key_here`

## Setup Instructions

### 1. Create Project Structure

Create the following directory structure in your project root:

```
tasks/
scripts/
.aider/
```

### 2. Create Configuration Files

#### File: `.aider.conf.yml`

Create this file in your project root with the following content:

```yaml
# Default model for implementation
model: claude-sonnet-4-5

# Git integration settings
auto-commits: false
dirty-commits: false
git: true

# Show diffs in responses
show-diffs: true
```

#### File: `.gitignore` (append these lines)

```
tasks/*.diff
tasks/*.txt
tasks/review_notes.md
.aider.chat.history.md
.aider.input.history
```

### 3. Create Workflow Scripts

#### File: `scripts/implement.sh`

```bash
#!/bin/bash
# Implementation phase using Claude Sonnet

TASK="$1"

if [ -z "$TASK" ]; then
  echo "Usage: ./scripts/implement.sh 'task description'"
  exit 1
fi

echo "=== IMPLEMENTATION PHASE ==="
echo "Task: $TASK"
echo ""

aider \
  --model claude-sonnet-4-5 \
  --message "Task: $TASK

Please implement this feature with REAL, working code.

Requirements:
1. Write actual, functional code (not just TODOs or comments)
2. Add or update tests as appropriate
3. Ensure code follows project conventions

After implementation, provide:
1. Summary of files you modified
2. Key changes made
3. Test status (did you add/run tests?)

Be thorough and complete the implementation fully." \
  --no-auto-commits

echo ""
echo "=== Implementation complete ==="
echo "Review the changes with: git diff"
echo "Proceed to review with: ./scripts/review.sh '$TASK'"
```

#### File: `scripts/review.sh`

```bash
#!/bin/bash
# Review phase using GPT-4

TASK="$1"

if [ -z "$TASK" ]; then
  echo "Usage: ./scripts/review.sh 'task description'"
  exit 1
fi

# Capture current state
echo "=== Capturing changes for review ==="
git diff > tasks/latest_changes.diff
git diff --stat > tasks/change_summary.txt
git status --short > tasks/file_status.txt

# Check if there are any changes
if [ ! -s tasks/latest_changes.diff ]; then
  echo "WARNING: No changes detected in git diff!"
  echo "This might indicate phantom work."
fi

echo ""
echo "=== REVIEW PHASE ==="
echo "Task: $TASK"
echo ""

aider \
  --model gpt-4o \
  --read tasks/latest_changes.diff tasks/change_summary.txt tasks/file_status.txt \
  --message "You are a SKEPTICAL code reviewer verifying another AI agent's work.

Original task: $TASK

Files provided:
- tasks/latest_changes.diff: Complete git diff of changes
- tasks/change_summary.txt: Summary of changed files
- tasks/file_status.txt: Git status

Your job is to critically evaluate if REAL work was done:

1. **Actual Implementation Check**
   - Is there real code, or just comments/TODOs?
   - Are there substantive logic changes?
   - Look for placeholder text like 'TODO', 'FIXME', '// implement this'

2. **Completeness Check**
   - Does the implementation address the full task?
   - Are edge cases handled?
   - Is error handling present?

3. **Test Coverage**
   - Are there new or updated tests?
   - Do tests look meaningful or are they stubs?
   - Is test logic appropriate for the changes?

4. **Quality Assessment**
   - Does code follow good practices?
   - Are there obvious bugs or issues?
   - Is the implementation production-ready?

Provide your assessment in this format:

## Review Summary
**Task:** [restate task]
**Verdict:** [ACCEPT / NEEDS_REVISION / REJECT]
**Completion Estimate:** [0-100%]

## Findings
[List specific issues, concerns, or praise]

## Missing or Incomplete
[What still needs to be done]

## Recommendation
[What should happen next]

Be harsh and thorough. Phantom work is unacceptable." \
  --no-auto-commits

echo ""
echo "=== Review complete ==="
```

#### File: `scripts/review_with_tests.sh`

```bash
#!/bin/bash
# Review phase with test execution

TASK="$1"
TEST_COMMAND="${2:-npm test}"  # Default to npm test, override as needed

if [ -z "$TASK" ]; then
  echo "Usage: ./scripts/review_with_tests.sh 'task description' [test_command]"
  exit 1
fi

# Capture changes
echo "=== Capturing changes ==="
git diff > tasks/latest_changes.diff
git diff --stat > tasks/change_summary.txt

# Run tests
echo ""
echo "=== Running tests: $TEST_COMMAND ==="
$TEST_COMMAND > tasks/test_output.txt 2>&1
TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
  echo "✓ Tests passed"
else
  echo "✗ Tests failed (exit code: $TEST_EXIT_CODE)"
fi

# Review with test results
echo ""
echo "=== REVIEW PHASE ==="

aider \
  --model gpt-4o \
  --read tasks/latest_changes.diff tasks/change_summary.txt tasks/test_output.txt \
  --message "You are verifying another AI agent's implementation with test results.

Task: $TASK
Test Command: $TEST_COMMAND
Test Exit Code: $TEST_EXIT_CODE

Files provided:
- tasks/latest_changes.diff: Code changes
- tasks/change_summary.txt: Changed files summary
- tasks/test_output.txt: Test execution output

Evaluate:
1. **Implementation Quality**
   - Real code vs comments/TODOs?
   - Addresses the task completely?

2. **Test Results Analysis**
   - Did tests pass? If not, why?
   - Are new tests added for new functionality?
   - Are tests meaningful or just stubs?
   - Does test coverage match the scope of changes?

3. **Code-Test Alignment**
   - Do the tests actually exercise the new code?
   - Are there untested code paths?

Provide verdict: ACCEPT / NEEDS_REVISION / REJECT

Be thorough and critical." \
  --no-auto-commits

echo ""
echo "=== Review with tests complete ==="
```

#### File: `scripts/workflow.sh`

```bash
#!/bin/bash
# Complete dual-agent workflow

TASK="$1"
USE_TESTS="${2:-no}"  # Pass 'yes' to include test running

if [ -z "$TASK" ]; then
  echo "Usage: ./scripts/workflow.sh 'task description' [yes to include tests]"
  echo ""
  echo "Example: ./scripts/workflow.sh 'add user login' yes"
  exit 1
fi

echo "╔════════════════════════════════════════════╗"
echo "║   DUAL-AGENT DEVELOPMENT WORKFLOW          ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Task: $TASK"
echo ""

# Phase 1: Implementation
echo "┌─────────────────────────────────────────┐"
echo "│ Phase 1: Implementation (Claude)        │"
echo "└─────────────────────────────────────────┘"
echo ""

./scripts/implement.sh "$TASK"

# Check if user wants to continue
echo ""
echo "═══════════════════════════════════════════"
echo "Review the changes above."
echo "Continue to review phase? (y/n)"
read -r response

if [[ ! "$response" =~ ^[Yy]$ ]]; then
  echo "Workflow stopped. You can run review later with:"
  echo "./scripts/review.sh '$TASK'"
  exit 0
fi

# Phase 2: Review
echo ""
echo "┌─────────────────────────────────────────┐"
echo "│ Phase 2: Review (GPT-4)                 │"
echo "└─────────────────────────────────────────┘"
echo ""

if [[ "$USE_TESTS" == "yes" ]]; then
  ./scripts/review_with_tests.sh "$TASK"
else
  ./scripts/review.sh "$TASK"
fi

# Phase 3: Decision
echo ""
echo "═══════════════════════════════════════════"
echo "Based on the review, would you like to:"
echo "  1) Commit the changes"
echo "  2) Request revisions from Claude"
echo "  3) Discard changes"
echo "  4) Exit and decide later"
echo ""
echo "Enter choice (1-4):"
read -r choice

case $choice in
  1)
    git add -A
    git commit -m "$TASK"
    echo "✓ Changes committed"
    ;;
  2)
    echo ""
    echo "Enter revision instructions:"
    read -r revisions
    ./scripts/implement.sh "$TASK - REVISION: $revisions"
    ;;
  3)
    git reset --hard
    git clean -fd
    echo "✓ Changes discarded"
    ;;
  4)
    echo "Exiting. Changes are staged but not committed."
    ;;
  *)
    echo "Invalid choice. Exiting."
    ;;
esac

echo ""
echo "Workflow complete."
```

### 4. Make Scripts Executable

Run this command:

```bash
chmod +x scripts/*.sh
```

### 5. Create Initial Task Directory Files

Create empty placeholder files:

```bash
touch tasks/.gitkeep
echo "# Task Reviews" > tasks/README.md
```

### 6. Create Usage Documentation

#### File: `DUAL_AGENT_WORKFLOW.md`

```markdown
# Dual-Agent Workflow Usage

## Quick Start

### Full Workflow
```bash
./scripts/workflow.sh "add user authentication"
```

### With Test Running
```bash
./scripts/workflow.sh "add user authentication" yes
```

### Manual Step-by-Step

1. **Implement** (Claude):
   ```bash
   ./scripts/implement.sh "implement feature X"
   ```

2. **Review changes**:
   ```bash
   git diff
   ```

3. **Review** (GPT-4):
   ```bash
   ./scripts/review.sh "implement feature X"
   ```

4. **Review with tests** (GPT-4):
   ```bash
   ./scripts/review_with_tests.sh "implement feature X" "npm test"
   ```

## Customization

### For Python Projects
Edit `scripts/review_with_tests.sh` and change:
```bash
TEST_COMMAND="${2:-pytest}"
```

### For Different Models
Edit `.aider.conf.yml` to change default models.

### Project-Specific Test Commands
Pass test command as second argument:
```bash
./scripts/review_with_tests.sh "add feature" "cargo test"
./scripts/review_with_tests.sh "add feature" "python -m pytest tests/"
```

## Tips for Best Results

1. **Be specific in task descriptions**:
   - ❌ "improve the code"
   - ✓ "add input validation to the user registration form"

2. **Review git diff yourself** between phases to spot obvious issues

3. **Iterate**: If GPT-4 finds issues, use them to request revisions

4. **Check the tasks/ directory** for detailed diffs and review notes

## Troubleshooting

### Aider not found
```bash
pip install aider-chat
```

### OpenAI API errors
Ensure your API key is set:
```bash
export OPENAI_API_KEY=your_key_here
```

### Claude model not available
You may need to configure Anthropic API access for Aider. Check Aider's documentation.

### No changes detected
This might indicate Claude didn't actually make changes. Check:
- Was the task too vague?
- Did an error occur during implementation?
- Look at aider's output for error messages
```

## Verification

After setup, your project structure should look like:

```
your-project/
├── src/                              # Your source code
├── tasks/                            # ← New
│   ├── .gitkeep
│   └── README.md
├── scripts/                          # ← New
│   ├── implement.sh
│   ├── review.sh
│   ├── review_with_tests.sh
│   └── workflow.sh
├── .aider/                           # ← New (created by aider)
├── .aider.conf.yml                   # ← New
├── DUAL_AGENT_WORKFLOW.md            # ← New
└── .gitignore                        # ← Updated
```

## Test the Setup

Run this command to verify everything is configured:

```bash
./scripts/workflow.sh "add a comment to the README explaining this is a test"
```

This will:
1. Have Claude add a simple comment to your README
2. Have GPT-4 review the change
3. Let you decide whether to commit

If this works, your dual-agent setup is ready!

## Next Steps

1. **Customize** the review prompts in `scripts/review.sh` for your specific needs
2. **Adjust** test commands in `scripts/review_with_tests.sh` for your project
3. **Start using** the workflow for real development tasks
4. **Iterate** on the prompts based on what works best for catching phantom work

Remember: The goal is to have an adversarial verification step that catches incomplete or superficial implementations.
