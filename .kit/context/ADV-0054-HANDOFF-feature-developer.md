# ADV-0054 Handoff: Fix review_implementation.sh Bugs

## Context

The `adversarial review` pipeline is broken for downstream projects. Four bugs were
discovered during real usage in the research-method-matrix project. See
`/Github/research-method-matrix/.agent-context/RMM-0001-adversarial-issues.md` for
the original bug report.

## Implementation Guide

### Bug 1: mkdir -p before first write

**Template** (`adversarial_workflow/templates/review_implementation.sh.template`):

Insert before line 103 (`# Capture current implementation state`):
```bash
# Ensure output directories exist before writing
mkdir -p "$ARTIFACTS_DIR"
mkdir -p "$LOG_DIR"
```

**Committed script** (`.adversarial/scripts/review_implementation.sh`):

Same fix — add `mkdir -p` before line 50. Also remove the duplicate `mkdir -p` that
appears later (line 88-89 in committed script) to avoid confusion.

### Bug 2: Branch-aware git diff

In both the template and committed script, replace the artifact capture block:

**Before**:
```bash
git diff > "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
git diff --stat > "${ARTIFACTS_DIR}${TASK_NUM}-change-summary.txt"
git status --short > "${ARTIFACTS_DIR}${TASK_NUM}-file-status.txt"
```

**After**:
```bash
# Detect default branch for comparison
DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")

# Capture all branch changes (committed + staged + unstaged)
git diff "${DEFAULT_BRANCH}...HEAD" > "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
git diff "${DEFAULT_BRANCH}...HEAD" --stat > "${ARTIFACTS_DIR}${TASK_NUM}-change-summary.txt"
git status --short > "${ARTIFACTS_DIR}${TASK_NUM}-file-status.txt"
```

Also update the `LINES_CHANGED` line:
```bash
LINES_CHANGED=$(git diff "${DEFAULT_BRANCH}...HEAD" --stat | tail -1)
```

**Edge case**: If there are also uncommitted changes on the branch, the three-dot diff
won't include them. Consider appending unstaged changes:
```bash
# Also capture any uncommitted work
if ! git diff --quiet; then
  echo -e "\n\n# === Uncommitted changes ===" >> "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
  git diff >> "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
fi
```

### Bug 3: CLI review argument passthrough

**File**: `adversarial_workflow/cli.py`

1. Find the review subparser registration (~line 3182):
   ```python
   # Before:
   subparsers.add_parser("review", help="Run Phase 3: Code review")

   # After:
   review_parser = subparsers.add_parser("review", help="Run Phase 3: Code review")
   review_parser.add_argument("task_file", nargs="?", help="Task file path")
   ```

2. Update `review()` function signature (~line 2111):
   ```python
   def review(task_file: str | None = None) -> int:
   ```

3. Pass argument to script (~line 2148):
   ```python
   cmd = [script]
   if task_file:
       cmd.append(task_file)
   result = subprocess.run(cmd, timeout=180)
   ```

4. Update the call site (~line 3466):
   ```python
   elif args.command == "review":
       return review(args.task_file)
   ```

### Bug 4: Fix /check-spec skill

**File**: `.claude/commands/check-spec.md`

Replace Step 3:
```markdown
## Step 3: Run the evaluator

\```bash
adversarial evaluate .adversarial/inputs/<TASK-ID>-spec-compliance-input.md --evaluator spec-compliance
\```
```

## Testing

- Run `pytest tests/ -v` — all existing tests must pass
- Manual verification: `adversarial review --help` should show the optional task_file argument
- Template and committed script should have matching logic for Bugs 1 & 2

## Resources

- Bug report: `/Github/research-method-matrix/.agent-context/RMM-0001-adversarial-issues.md`
- Task spec: `delegation/tasks/2-todo/ADV-0054-fix-review-script-bugs.md`
- CLI source: `adversarial_workflow/cli.py` (review at ~line 2111, subparser at ~line 3182)
- Template: `adversarial_workflow/templates/review_implementation.sh.template`
- Committed script: `.adversarial/scripts/review_implementation.sh`
- Skill: `.claude/commands/check-spec.md`
