# ADV-0054: Fix review_implementation.sh Bugs

**Status**: In Review
**Priority**: High
**Type**: Bug Fix
**Estimated Effort**: 1-2 hours
**Created**: 2026-03-15
**Reported By**: RMM-0001 (research-method-matrix project)

## Summary

The `adversarial review` command and its underlying `review_implementation.sh` script
have multiple bugs that make the review phase non-functional for downstream projects.
These were discovered during real usage in the research-method-matrix project (RMM-0001).

The bugs affect both the **template** (what `adversarial init` generates for new projects)
and the **CLI wrapper** (the `adversarial review` subcommand). The `/check-spec` skill
also references a non-existent CLI command.

## Bug Details

### Bug 1: `mkdir -p` comes after first write (CRASH)

**Files**: `adversarial_workflow/templates/review_implementation.sh.template` (lines 105-107),
`.adversarial/scripts/review_implementation.sh` (lines 50-52)

The script writes artifacts on lines 105-107:
```bash
git diff > "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
git diff --stat > "${ARTIFACTS_DIR}${TASK_NUM}-change-summary.txt"
git status --short > "${ARTIFACTS_DIR}${TASK_NUM}-file-status.txt"
```

But `mkdir -p "$ARTIFACTS_DIR"` doesn't appear until much later in the committed script
(line 89). The template doesn't have `mkdir -p` at all.

**Fix**: Add `mkdir -p "$ARTIFACTS_DIR"` and `mkdir -p "$LOG_DIR"` immediately before
the artifact capture block (before the first `git diff >` redirect).

### Bug 2: `git diff` captures wrong changes (WRONG OUTPUT)

**Files**: Same as Bug 1

The script uses bare `git diff` which only captures **unstaged** changes. On a feature
branch where work is committed or staged, this produces empty or misleading output.
The RMM project saw only a task file deletion (from `./scripts/project start` move)
instead of the 5 source files with actual implementation changes.

**Fix**: Replace bare `git diff` with branch-aware diff:

```bash
# Detect the default branch
DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")

# Capture ALL changes on this branch (committed + staged + unstaged)
git diff "${DEFAULT_BRANCH}...HEAD" > "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
git diff "${DEFAULT_BRANCH}...HEAD" --stat > "${ARTIFACTS_DIR}${TASK_NUM}-change-summary.txt"
```

Also update the `--stat` line that computes `LINES_CHANGED` to use the same range.

Keep `git status --short` as-is (it shows current working tree state, which is useful context).

### Bug 3: `adversarial review` doesn't pass file argument (BROKEN CLI)

**File**: `adversarial_workflow/cli.py` (lines 2111-2160, 3182)

The `review` subcommand is registered with no arguments:
```python
subparsers.add_parser("review", help="Run Phase 3: Code review")
```

And the `review()` function calls the script without forwarding any argument:
```python
result = subprocess.run([script], timeout=180)
```

But the script **requires** a task file argument and exits with an error without one.

**Fix**:
1. Add an optional positional argument to the `review` subparser:
   ```python
   review_parser = subparsers.add_parser("review", help="Run Phase 3: Code review")
   review_parser.add_argument("task_file", nargs="?", help="Task file path (optional)")
   ```
2. Update `review()` to accept and pass the argument:
   ```python
   def review(task_file: str | None = None) -> int:
   ```
3. Pass it to the script: `subprocess.run([script, task_file] if task_file else [script], ...)`
4. Update the call site to pass `args.task_file`

### Bug 4: `/check-spec` skill references non-existent command (BROKEN SKILL)

**File**: `.claude/commands/check-spec.md` (line 34)

The skill instructs:
```bash
adversarial spec-compliance-fast .adversarial/inputs/<TASK-ID>-spec-compliance-input.md
```

But `spec-compliance-fast` is not a CLI subcommand. The spec-compliance evaluator exists
at `.adversarial/evaluators/custom/spec-compliance.yml` and should be invoked via:
```bash
adversarial evaluate .adversarial/inputs/<TASK-ID>-spec-compliance-input.md --evaluator spec-compliance
```

**Fix**: Update `.claude/commands/check-spec.md` Step 3 to use the correct command.

## Acceptance Criteria

- [ ] **Bug 1**: `mkdir -p` for artifacts and log dirs happens before first file write in both template and committed script
- [ ] **Bug 2**: Diff captures all branch changes via `git diff <default-branch>...HEAD`, not bare `git diff`
- [ ] **Bug 3**: `adversarial review <task-file>` passes the file argument through to the script
- [ ] **Bug 4**: `/check-spec` skill references correct `adversarial evaluate` command
- [ ] **Tests**: Existing tests still pass (`pytest tests/ -v`)
- [ ] **Consistency**: Template and committed script remain in sync (or committed script is removed if redundant)

## Files to Modify

1. `adversarial_workflow/templates/review_implementation.sh.template` — Bugs 1, 2
2. `.adversarial/scripts/review_implementation.sh` — Bugs 1, 2 (keep in sync with template)
3. `adversarial_workflow/cli.py` — Bug 3 (review subparser + review() function + call site)
4. `.claude/commands/check-spec.md` — Bug 4

## Notes

- **Issue 5 from RMM report** (aider skipping gitignored artifacts) is already fixed — both the template and committed script have `--no-gitignore`. The RMM project likely had an older copy.
- The committed `.adversarial/scripts/review_implementation.sh` is a local copy that diverges slightly from the template. Consider whether to keep both in sync or remove the committed copy.
- `config.yml` in this repo is missing `artifacts_directory` — the script falls back to parsing it from config, which returns empty. This doesn't crash because `init` creates the dir, but the path variable will be empty for repos that don't set it. The template handles this via config parsing. Not in scope for this task but worth noting.
