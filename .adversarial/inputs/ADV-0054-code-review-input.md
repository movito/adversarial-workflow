# Code Review Input: ADV-0054 — Fix review_implementation.sh Bugs

# ADV-0054 Review Starter: Fix review_implementation.sh Bugs

**PR**: https://github.com/movito/adversarial-workflow/pull/48
**Branch**: `feature/ADV-0054-fix-review-script-bugs`
**Commits**: 3

## What Changed

4 bugs fixed in the adversarial review pipeline, discovered during real downstream usage (RMM-0001):

1. **mkdir crash** (Bug 1): Added `mkdir -p` for artifacts/log dirs before first file write
2. **Wrong diff** (Bug 2): Replaced bare `git diff` with `git diff <default-branch>...HEAD` + staged/unstaged capture
3. **Broken CLI** (Bug 3): Added required `task_file` argument to `adversarial review` subparser
4. **Bad command ref** (Bug 4): Updated `/check-spec` to use `adversarial evaluate --evaluator spec-compliance`

## Files Modified

| File | Changes |
|------|---------|
| `adversarial_workflow/cli.py` | `review()` signature, branch-aware pre-check, required arg, 3 usage examples |
| `adversarial_workflow/templates/review_implementation.sh.template` | mkdir, DEFAULT_BRANCH detection, staged/unstaged capture |
| `.adversarial/scripts/review_implementation.sh` | Same as template (kept in sync) |
| `.claude/commands/check-spec.md` | Fixed command reference |

## Bot Review Summary

- **8 threads** across 3 rounds (BugBot + CodeRabbit)
- **7 fixed**, **1 resolved without fixing** (LINES_CHANGED cosmetic display)
- Key bot-driven improvements: branch-aware CLI pre-check, staged change capture, DEFAULT_BRANCH fallback fix, required task_file

## Spec Deviation (Intentional)

`task_file` made **required** instead of spec's `nargs="?"` (optional). Reason: the underlying script exits with error when no argument is provided, so making it optional in the CLI creates a guaranteed failure path. CodeRabbit flagged this as Major; we agreed and fixed it.

## Review Focus Areas

1. **Shell logic**: DEFAULT_BRANCH detection fallback chain (`--short` + `${VAR:-main}`)
2. **CLI pre-check**: Now checks branch diff + staged + unstaged (all must be clean to abort)
3. **Staged/unstaged capture**: Appended to artifacts with section headers

## Evaluator Verdict

**MOSTLY_COMPLIANT** — All bugs fixed. Two noted gaps: intentional `task_file` deviation (explained above) and no new unit tests for bash script fixes (not feasible without mocking git/filesystem).

## How to Review

```bash
git checkout feature/ADV-0054-fix-review-script-bugs
pytest tests/ -v                    # 493 pass
adversarial review --help           # Shows required task_file
```


---

## Full Diff (main...HEAD)

```diff
diff --git a/.adversarial/scripts/review_implementation.sh b/.adversarial/scripts/review_implementation.sh
index fc23211..27f0173 100755
--- a/.adversarial/scripts/review_implementation.sh
+++ b/.adversarial/scripts/review_implementation.sh
@@ -45,12 +45,37 @@ echo "Task: $TASK_NUM"
 echo "Model: $EVALUATOR_MODEL"
 echo ""
 
+# Ensure output directories exist before writing
+mkdir -p "$ARTIFACTS_DIR"
+mkdir -p "$LOG_DIR"
+
+# Detect default branch for comparison
+DEFAULT_BRANCH=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null || true)
+DEFAULT_BRANCH=${DEFAULT_BRANCH#origin/}
+DEFAULT_BRANCH=${DEFAULT_BRANCH:-main}
+
 # Capture current implementation state
 echo "=== Capturing implementation artifacts ==="
-git diff > "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
-git diff --stat > "${ARTIFACTS_DIR}${TASK_NUM}-change-summary.txt"
+git diff "${DEFAULT_BRANCH}...HEAD" > "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
+git diff "${DEFAULT_BRANCH}...HEAD" --stat > "${ARTIFACTS_DIR}${TASK_NUM}-change-summary.txt"
 git status --short > "${ARTIFACTS_DIR}${TASK_NUM}-file-status.txt"
 
+# Also capture staged but uncommitted work
+if ! git diff --cached --quiet; then
+  echo -e "\n\n# === Staged changes ===" >> "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
+  git diff --cached >> "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
+  echo -e "\n\n# === Staged changes ===" >> "${ARTIFACTS_DIR}${TASK_NUM}-change-summary.txt"
+  git diff --cached --stat >> "${ARTIFACTS_DIR}${TASK_NUM}-change-summary.txt"
+fi
+
+# Also capture any uncommitted work
+if ! git diff --quiet; then
+  echo -e "\n\n# === Uncommitted changes ===" >> "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
+  git diff >> "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
+  echo -e "\n\n# === Uncommitted changes ===" >> "${ARTIFACTS_DIR}${TASK_NUM}-change-summary.txt"
+  git diff --stat >> "${ARTIFACTS_DIR}${TASK_NUM}-change-summary.txt"
+fi
+
 # Check if there are any changes
 if [ ! -s "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff" ]; then
   echo ""
@@ -62,7 +87,7 @@ if [ ! -s "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff" ]; then
 fi
 
 # Count lines changed
-LINES_CHANGED=$(git diff --stat | tail -1)
+LINES_CHANGED=$(git diff "${DEFAULT_BRANCH}...HEAD" --stat | tail -1)
 
 echo "✓ Changes captured:"
 echo "  - Git diff: ${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
@@ -84,10 +109,6 @@ echo ""
 echo "=== REVIEWER ($EVALUATOR_MODEL) ANALYZING IMPLEMENTATION ==="
 echo ""
 
-# Ensure log and artifacts directories exist
-mkdir -p "$LOG_DIR"
-mkdir -p "$ARTIFACTS_DIR"
-
 # Create review output file
 REVIEW_OUTPUT="${LOG_DIR}${TASK_NUM}-IMPLEMENTATION-REVIEW.md"
 
diff --git a/.claude/commands/check-spec.md b/.claude/commands/check-spec.md
index 1132f11..4bf8cde 100644
--- a/.claude/commands/check-spec.md
+++ b/.claude/commands/check-spec.md
@@ -31,7 +31,7 @@ Use the Bash tool to read files and assemble the input. Do NOT summarize or trun
 ## Step 3: Run the evaluator
 
 ```bash
-adversarial spec-compliance-fast .adversarial/inputs/<TASK-ID>-spec-compliance-input.md
+adversarial evaluate .adversarial/inputs/<TASK-ID>-spec-compliance-input.md --evaluator spec-compliance
 ```
 
 ## Step 4: Read and act on results
diff --git a/adversarial_workflow/cli.py b/adversarial_workflow/cli.py
index 84e6074..91fb857 100644
--- a/adversarial_workflow/cli.py
+++ b/adversarial_workflow/cli.py
@@ -494,7 +494,7 @@ def quickstart() -> int:
             "",
             "Try the full workflow:",
             "  1. Implement the fix (or let Claude do it via aider)",
-            "  2. Run: adversarial review (Phase 3: Code Review)",
+            "  2. Run: adversarial review <task_file> (Phase 3: Code Review)",
             "  3. Run: adversarial validate (Phase 4: Test Validation)",
             "",
             "Learn more:",
@@ -1704,7 +1704,7 @@ def health(verbose: bool = False, json_output: bool = False) -> int:
         if health_score > 70:
             print(f"{BOLD}Ready to:{RESET}")
             print("  • Evaluate task plans: adversarial evaluate <task-file>")
-            print("  • Review implementations: adversarial review")
+            print("  • Review implementations: adversarial review <task_file>")
             print("  • Validate tests: adversarial validate")
         else:
             print(f"{BOLD}Next steps:{RESET}")
@@ -2108,17 +2108,33 @@ def evaluate(task_file: str) -> int:
         return 0
 
 
-def review() -> int:
+def review(task_file: str) -> int:
     """Run Phase 3: Code review."""
 
     print("🔍 Reviewing implementation...")
     print()
 
-    # Check for git changes
-    result = subprocess.run(["git", "diff", "--quiet"], capture_output=True)
-
-    if result.returncode == 0:
-        # No changes
+    # Check for git changes (branch-aware: committed, staged, or unstaged)
+    default_branch = subprocess.run(
+        ["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
+        capture_output=True,
+        text=True,
+    )
+    base = (
+        default_branch.stdout.strip().removeprefix("origin/")
+        if default_branch.returncode == 0
+        else "main"
+    )
+    branch_diff = subprocess.run(["git", "diff", "--quiet", f"{base}...HEAD"], capture_output=True)
+    staged_diff = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
+    unstaged_diff = subprocess.run(["git", "diff", "--quiet"], capture_output=True)
+
+    if (
+        branch_diff.returncode == 0
+        and staged_diff.returncode == 0
+        and unstaged_diff.returncode == 0
+    ):
+        # No changes at all
         print(f"{YELLOW}⚠️  WARNING: No git changes detected!{RESET}")
         print("   This might indicate PHANTOM WORK.")
         print("   Aborting review to save tokens.")
@@ -2145,7 +2161,7 @@ def review() -> int:
         return 1
 
     try:
-        result = subprocess.run([script], timeout=180)
+        result = subprocess.run([script, task_file], timeout=180)
     except subprocess.TimeoutExpired:
         print(f"{RED}❌ ERROR: Review timed out (>3 minutes){RESET}")
         return 1
@@ -3031,7 +3047,7 @@ Examples:
   adversarial agent onboard             # Set up agent coordination
   adversarial evaluate tasks/feat.md    # Evaluate plan
   adversarial proofread docs/guide.md   # Proofread teaching content
-  adversarial review                    # Review implementation
+  adversarial review <task_file>         # Review implementation
   adversarial validate "npm test"       # Validate with tests
   adversarial split large-task.md       # Split large files
   adversarial check-citations doc.md    # Verify URLs in document
@@ -3178,8 +3194,9 @@ For more information: https://github.com/movito/adversarial-workflow
         "--no-cache", action="store_true", help="Bypass cache and fetch fresh data"
     )
 
-    # review command (static - reviews git changes, no file argument)
-    subparsers.add_parser("review", help="Run Phase 3: Code review")
+    # review command
+    review_parser = subparsers.add_parser("review", help="Run Phase 3: Code review")
+    review_parser.add_argument("task_file", help="Task file path")
 
     # validate command
     validate_parser = subparsers.add_parser("validate", help="Run Phase 4: Test validation")
@@ -3464,7 +3481,7 @@ For more information: https://github.com/movito/adversarial-workflow
             print("  adversarial library update <name>")
             return 1
     elif args.command == "review":
-        return review()
+        return review(args.task_file)
     elif args.command == "validate":
         return validate(args.test_command)
     elif args.command == "split":
diff --git a/adversarial_workflow/templates/review_implementation.sh.template b/adversarial_workflow/templates/review_implementation.sh.template
index 7208ddf..8c4e619 100644
--- a/adversarial_workflow/templates/review_implementation.sh.template
+++ b/adversarial_workflow/templates/review_implementation.sh.template
@@ -100,12 +100,37 @@ echo "Task: $TASK_NUM"
 echo "Model: $EVALUATOR_MODEL"
 echo ""
 
+# Ensure output directories exist before writing
+mkdir -p "$ARTIFACTS_DIR"
+mkdir -p "$LOG_DIR"
+
+# Detect default branch for comparison
+DEFAULT_BRANCH=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null || true)
+DEFAULT_BRANCH=${DEFAULT_BRANCH#origin/}
+DEFAULT_BRANCH=${DEFAULT_BRANCH:-main}
+
 # Capture current implementation state
 echo "=== Capturing implementation artifacts ==="
-git diff > "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
-git diff --stat > "${ARTIFACTS_DIR}${TASK_NUM}-change-summary.txt"
+git diff "${DEFAULT_BRANCH}...HEAD" > "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
+git diff "${DEFAULT_BRANCH}...HEAD" --stat > "${ARTIFACTS_DIR}${TASK_NUM}-change-summary.txt"
 git status --short > "${ARTIFACTS_DIR}${TASK_NUM}-file-status.txt"
 
+# Also capture staged but uncommitted work
+if ! git diff --cached --quiet; then
+  echo -e "\n\n# === Staged changes ===" >> "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
+  git diff --cached >> "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
+  echo -e "\n\n# === Staged changes ===" >> "${ARTIFACTS_DIR}${TASK_NUM}-change-summary.txt"
+  git diff --cached --stat >> "${ARTIFACTS_DIR}${TASK_NUM}-change-summary.txt"
+fi
+
+# Also capture any uncommitted work
+if ! git diff --quiet; then
+  echo -e "\n\n# === Uncommitted changes ===" >> "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
+  git diff >> "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
+  echo -e "\n\n# === Uncommitted changes ===" >> "${ARTIFACTS_DIR}${TASK_NUM}-change-summary.txt"
+  git diff --stat >> "${ARTIFACTS_DIR}${TASK_NUM}-change-summary.txt"
+fi
+
 # Check if there are any changes
 if [ ! -s "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff" ]; then
   echo ""
@@ -117,7 +142,7 @@ if [ ! -s "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff" ]; then
 fi
 
 # Count lines changed
-LINES_CHANGED=$(git diff --stat | tail -1)
+LINES_CHANGED=$(git diff "${DEFAULT_BRANCH}...HEAD" --stat | tail -1)
 
 echo "✓ Changes captured:"
 echo "  - Git diff: ${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
diff --git a/delegation/tasks/3-in-progress/ADV-0054-fix-review-script-bugs.md b/delegation/tasks/3-in-progress/ADV-0054-fix-review-script-bugs.md
new file mode 100644
index 0000000..ce24562
--- /dev/null
+++ b/delegation/tasks/3-in-progress/ADV-0054-fix-review-script-bugs.md
@@ -0,0 +1,130 @@
+# ADV-0054: Fix review_implementation.sh Bugs
+
+**Status**: In Progress
+**Priority**: High
+**Type**: Bug Fix
+**Estimated Effort**: 1-2 hours
+**Created**: 2026-03-15
+**Reported By**: RMM-0001 (research-method-matrix project)
+
+## Summary
+
+The `adversarial review` command and its underlying `review_implementation.sh` script
+have multiple bugs that make the review phase non-functional for downstream projects.
+These were discovered during real usage in the research-method-matrix project (RMM-0001).
+
+The bugs affect both the **template** (what `adversarial init` generates for new projects)
+and the **CLI wrapper** (the `adversarial review` subcommand). The `/check-spec` skill
+also references a non-existent CLI command.
+
+## Bug Details
+
+### Bug 1: `mkdir -p` comes after first write (CRASH)
+
+**Files**: `adversarial_workflow/templates/review_implementation.sh.template` (lines 105-107),
+`.adversarial/scripts/review_implementation.sh` (lines 50-52)
+
+The script writes artifacts on lines 105-107:
+```bash
+git diff > "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
+git diff --stat > "${ARTIFACTS_DIR}${TASK_NUM}-change-summary.txt"
+git status --short > "${ARTIFACTS_DIR}${TASK_NUM}-file-status.txt"
+```
+
+But `mkdir -p "$ARTIFACTS_DIR"` doesn't appear until much later in the committed script
+(line 89). The template doesn't have `mkdir -p` at all.
+
+**Fix**: Add `mkdir -p "$ARTIFACTS_DIR"` and `mkdir -p "$LOG_DIR"` immediately before
+the artifact capture block (before the first `git diff >` redirect).
+
+### Bug 2: `git diff` captures wrong changes (WRONG OUTPUT)
+
+**Files**: Same as Bug 1
+
+The script uses bare `git diff` which only captures **unstaged** changes. On a feature
+branch where work is committed or staged, this produces empty or misleading output.
+The RMM project saw only a task file deletion (from `./scripts/project start` move)
+instead of the 5 source files with actual implementation changes.
+
+**Fix**: Replace bare `git diff` with branch-aware diff:
+
+```bash
+# Detect the default branch
+DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")
+
+# Capture ALL changes on this branch (committed + staged + unstaged)
+git diff "${DEFAULT_BRANCH}...HEAD" > "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
+git diff "${DEFAULT_BRANCH}...HEAD" --stat > "${ARTIFACTS_DIR}${TASK_NUM}-change-summary.txt"
+```
+
+Also update the `--stat` line that computes `LINES_CHANGED` to use the same range.
+
+Keep `git status --short` as-is (it shows current working tree state, which is useful context).
+
+### Bug 3: `adversarial review` doesn't pass file argument (BROKEN CLI)
+
+**File**: `adversarial_workflow/cli.py` (lines 2111-2160, 3182)
+
+The `review` subcommand is registered with no arguments:
+```python
+subparsers.add_parser("review", help="Run Phase 3: Code review")
+```
+
+And the `review()` function calls the script without forwarding any argument:
+```python
+result = subprocess.run([script], timeout=180)
+```
+
+But the script **requires** a task file argument and exits with an error without one.
+
+**Fix**:
+1. Add an optional positional argument to the `review` subparser:
+   ```python
+   review_parser = subparsers.add_parser("review", help="Run Phase 3: Code review")
+   review_parser.add_argument("task_file", nargs="?", help="Task file path (optional)")
+   ```
+2. Update `review()` to accept and pass the argument:
+   ```python
+   def review(task_file: str | None = None) -> int:
+   ```
+3. Pass it to the script: `subprocess.run([script, task_file] if task_file else [script], ...)`
+4. Update the call site to pass `args.task_file`
+
+### Bug 4: `/check-spec` skill references non-existent command (BROKEN SKILL)
+
+**File**: `.claude/commands/check-spec.md` (line 34)
+
+The skill instructs:
+```bash
+adversarial spec-compliance-fast .adversarial/inputs/<TASK-ID>-spec-compliance-input.md
+```
+
+But `spec-compliance-fast` is not a CLI subcommand. The spec-compliance evaluator exists
+at `.adversarial/evaluators/custom/spec-compliance.yml` and should be invoked via:
+```bash
+adversarial evaluate .adversarial/inputs/<TASK-ID>-spec-compliance-input.md --evaluator spec-compliance
+```
+
+**Fix**: Update `.claude/commands/check-spec.md` Step 3 to use the correct command.
+
+## Acceptance Criteria
+
+- [ ] **Bug 1**: `mkdir -p` for artifacts and log dirs happens before first file write in both template and committed script
+- [ ] **Bug 2**: Diff captures all branch changes via `git diff <default-branch>...HEAD`, not bare `git diff`
+- [ ] **Bug 3**: `adversarial review <task-file>` passes the file argument through to the script
+- [ ] **Bug 4**: `/check-spec` skill references correct `adversarial evaluate` command
+- [ ] **Tests**: Existing tests still pass (`pytest tests/ -v`)
+- [ ] **Consistency**: Template and committed script remain in sync (or committed script is removed if redundant)
+
+## Files to Modify
+
+1. `adversarial_workflow/templates/review_implementation.sh.template` — Bugs 1, 2
+2. `.adversarial/scripts/review_implementation.sh` — Bugs 1, 2 (keep in sync with template)
+3. `adversarial_workflow/cli.py` — Bug 3 (review subparser + review() function + call site)
+4. `.claude/commands/check-spec.md` — Bug 4
+
+## Notes
+
+- **Issue 5 from RMM report** (aider skipping gitignored artifacts) is already fixed — both the template and committed script have `--no-gitignore`. The RMM project likely had an older copy.
+- The committed `.adversarial/scripts/review_implementation.sh` is a local copy that diverges slightly from the template. Consider whether to keep both in sync or remove the committed copy.
+- `config.yml` in this repo is missing `artifacts_directory` — the script falls back to parsing it from config, which returns empty. This doesn't crash because `init` creates the dir, but the path variable will be empty for repos that don't set it. The template handles this via config parsing. Not in scope for this task but worth noting.
```
