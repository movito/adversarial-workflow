# Review Insights Index

Knowledge extracted from code reviews for future reference (KIT-ADR-0019).

---

## Evaluators (`adversarial_workflow/evaluators/`)

### ADV-0029: YAML field validation should check for bool coercion
- YAML parses `yes`/`no`/`true`/`false` as booleans, not strings
- When validating integer fields, explicitly check `isinstance(value, bool)` before `isinstance(value, int)` (since bool is a subclass of int in Python)
- Pattern used in `discovery.py:126-152`

### ADV-0029: Precedence logging pattern for config overrides
- When multiple sources can provide a value (CLI > config > default), log which source is active
- Pattern: `print(f"Using {setting}: {value} ({source})")`
- Helps users understand where their configuration comes from

---

## Testing (`tests/`)

### ADV-0029: Integration testing subprocess timeouts with mock scripts
- Create lightweight mock scripts that sleep for configurable durations
- Test timeout success: mock sleeps less than timeout
- Test timeout failure: mock sleeps longer than timeout
- Verify timeout values flow through entire stack
- See `tests/test_timeout_integration.py` for pattern

### ADV-0029: Use raw strings for regex in pytest.raises match
- Style preference: `match=r"pattern.*here"` not `match="pattern.*here"`
- Prevents escape sequence issues

---

## CLI (`adversarial_workflow/cli.py`)

### ADV-0029: Validation at execution time for CLI overrides
- CLI flag validation (e.g., max values) should happen at execution time, not argument parsing
- Allows config defaults to be used if CLI flag not provided
- Pattern: Check `args.flag is not None` before applying validation

---

---

## Library Module (`adversarial_workflow/library/`)

### ADV-0013: YAML document separator stripping for concatenation
- When concatenating YAML content (e.g., adding provenance headers), strip leading `---` document separator
- Without stripping, results in multi-document YAML that some parsers reject
- Pattern: `if yaml_content.startswith("---"): yaml_content = yaml_content[3:].lstrip("\n")`

### ADV-0013: Cross-provider file collision prevention
- Use `{provider}-{name}.yml` naming instead of just `{name}.yml`
- Example: `google-gemini-flash.yml` vs `openai-gpt-4o.yml`
- Prevents collisions when different providers have evaluators with same name

### ADV-0013: HTTPError must be caught before URLError
- `urllib.error.HTTPError` is a subclass of `urllib.error.URLError`
- Catch HTTPError first to get proper HTTP status codes
- Pattern: `except HTTPError as e: ... except URLError as e: ...`

### ADV-0013: Timezone-aware UTC timestamps
- Use `datetime.now(timezone.utc)` not `datetime.now()` with appended "Z"
- Proper format: `.isoformat(timespec="seconds").replace("+00:00", "Z")`
- Prevents naive datetime + fake "Z" suffix

### ADV-0013: Cache with stale fallback for offline resilience
- Implement TTL-based cache with `get_stale()` method for expired-but-usable data
- On network error, fall back to stale cache before raising exception
- Pattern in `CacheManager` with separate `get()` and `get_stale()` methods

### ADV-0013: Provenance tracking via `_meta` block
- Installed library items should include machine-readable provenance
- Structure: `_meta: { source, source_path, version, installed }`
- Enables update checking and audit trails

---

## Testing (`tests/`)

### ADV-0013: pytest fixtures cannot be renamed with underscore
- Built-in fixtures like `capsys` cannot be renamed to `_capsys`
- Either use the fixture or remove the parameter entirely
- Don't try to suppress "unused" warnings by renaming fixtures

### ADV-0013: Integration tests should be marked for selective execution
- Use `pytest.mark.network` or similar for tests requiring network
- Allows `pytest -m "not network"` for offline CI runs
- Pattern: `pytestmark = pytest.mark.network` at module level

---

## Evaluators (`adversarial_workflow/evaluators/`)

### ADV-0065: Verdict tokens in prompts must match parser sets exactly
- Built-in evaluator prompts instruct the LLM to output verdict tokens (e.g., `APPROVED`, `REJECTED`)
- These tokens must match the `_PASS_VERDICTS`, `_REVISE_VERDICTS`, `_REJECT_VERDICTS` sets in `runner.py`
- The evaluate prompt originally used `REJECT` but the parser expects `REJECTED` — caught by both TDD and CodeRabbit
- Pattern: when adding/modifying verdict tokens, grep for all three sets and the prompt text

### ADV-0065: LiteLLM exception hierarchy for error handling
- `litellm.RateLimitError` — API rate limits (429)
- `litellm.AuthenticationError` — invalid API key (401)
- `litellm.Timeout` — request exceeded timeout
- Catch these specifically rather than broad `Exception` — provides actionable error messages
- Auth error should reference the `api_key_env` variable name so users know which key to check

### ADV-0065: `resolved_api_key_env` should flow through to error handlers
- When `ModelResolver` resolves a model, it also resolves the API key env var name
- Pass this through to `_run_custom_evaluator()` so auth errors can say "check GEMINI_API_KEY" not just "auth failed"
- Fallback chain: `resolved_api_key_env or config.api_key_env or "API key"`

---

## Process

### ADV-0065: Transport-swap tasks have low evaluator signal
- `code-reviewer-fast` returned FAIL with 5 findings, all triaged as false positive or out-of-scope
- For mechanical dependency swaps where the API contract is preserved, evaluator review adds more noise than signal
- Consider skipping evaluator review for mechanical refactors and relying on TDD + bot reviews instead

### ADV-0065: Always `ruff format` before every commit
- CI failed on formatting (trailing blank lines) despite passing tests
- Pre-commit hooks don't always fire (e.g., when committing CodeRabbit fixes quickly)
- Add explicit `ruff format <changed-files>` to the inner loop after every code edit

---

## CLI (`adversarial_workflow/cli.py`)

### ADV-0066: Builtin evaluator rewiring pattern
- `evaluate()`, `review()` now call `run_evaluator(builtin_config, file)` instead of shelling out to scripts
- Log file selection: filter by `output_suffix` (e.g., `PLAN-EVALUATION`) rather than glob for newest `.md`
- Pattern: `BUILTIN_EVALUATORS.get("evaluate")` returns the config, then `run_evaluator()` handles everything

### ADV-0066: Duplicate verdict extraction is dead code
- `run_evaluator()` already extracts verdicts and returns exit codes (0=APPROVED, 1=revision/rejected)
- `cli.evaluate()` then re-extracts the verdict from the log file — the NEEDS_REVISION/REJECTED branches are unreachable after a return code of 0
- Pre-existing design smell tracked in `.kit/context/ADV-0066-preexisting-issues.md`
- **RESOLVED in ADV-0067**: Dead code removed, `evaluate()` now follows the same pattern as `review()`

### ADV-0067: `run_evaluator()` returns 0 for both APPROVED and UNKNOWN verdicts
- `_report_verdict()` returns 0 for pass verdicts AND for unrecognized/unknown verdicts (the `else` branch)
- This means callers cannot distinguish "approved" from "unknown verdict" using the return code alone
- When simplifying `evaluate()` to check `eval_result != 0`, the success message should say "complete" not "approved" — since 0 doesn't guarantee approval
- Bots caught this semantic subtlety during ADV-0067 review

### ADV-0067: Cascading dead code cleanup
- When removing a dead code block, audit all functions/imports it was the sole caller of
- ADV-0067 spec estimated ~55 lines removed; actual was ~420 lines due to 4 orphaned helper functions + `import re` + their tests
- Task specs should include a "cascade audit" step when deleting code blocks

---

## Testing (`tests/`)

### ADV-0066: Audit glob mocks that return empty lists
- When a test mocks `glob.glob` to return `[]`, verify this doesn't accidentally skip the code path being tested
- A `glob.glob` returning `[]` can bypass validation entirely, making the test pass vacuously
- Pattern: after mocking glob, assert the validation function is still called (or test both empty and non-empty returns)

---

## Process

### ADV-0066: Cleanup tasks can generate 4+ bot review rounds
- A deletion-heavy task (46 files, ~7000 lines removed) generated 15 threads across 4 rounds
- Most findings were valid (log file selection, shlex handling, impossible test mocks)
- Budget for bot triage even on "simple" cleanup tasks

### ADV-0067: Task spec precision enables fast implementation
- The ADV-0067 handoff included exact line numbers and the target pattern (`review()` lines 1861-1869)
- Agent went straight to implementation with zero exploration time
- For small refactors, precise line-number references in the handoff are more valuable than architectural context

## Infrastructure Migrations

### ADV-0068: Bulk path replacement must include destination directories
- When moving files AND rewriting paths, the replacement script must target BOTH source-adjacent files and the moved files themselves
- Files moved into `.kit/context/` (agent-handoffs.json, README.md, workflows/) still contained old paths
- Pattern: run replacement script on destination dirs AFTER `git mv`, not just on `.claude/` and `scripts/`

### ADV-0068: `delegation/tasks/active/` has no .kit/ equivalent
- Legacy `delegation/tasks/active/` paths in CLI-scaffolded docs (README, QUICK_START, SETUP) describe consumer project structure
- The `.kit/tasks/` layout uses numbered folders (1-backlog through 9-reference), not `active/`
- Don't blindly sed `delegation/tasks/active/` → `.kit/tasks/active/` — it doesn't exist
- Rule: consumer-facing docs that describe CLI behavior should NOT be rewritten during kit migration

### ADV-0068: Use explicit `git add` for large migrations, never `git add -A`
- `git add -A` swept up `.aider.*`, `.dispatch/`, and stale root files (`planner2.md`)
- Stage by category: `git add .kit/` then `git add .claude/` etc.
- Add common dev artifacts (`.aider.*`, `.dispatch/`) to `.gitignore` proactively

### ADV-0069: `project move` doesn't git-track the old path removal
- `./scripts/core/project move` moves the filesystem file but doesn't `git rm` the old path
- If you stage only the new location, git sees both old and new — BugBot catches the duplicate
- Pattern: after `project move`, always `git add` the old directory too (so git sees the deletion) or use `git mv` directly

### ADV-0070: Sub-agents can make unauthorized commits on feature branches
- The ci-checker agent (launched as bot-watcher substitute) committed changes to agent definition files on the feature branch, violating Workflow Freeze Policy
- Had to `git reset --soft` to undo the unauthorized commit
- Pattern: when launching monitoring sub-agents, either (a) use `isolation: "worktree"` or (b) add explicit "do not commit" instructions in the prompt

### ADV-0070: Batch `sed` is faster than Edit tool for bulk markdown path updates
- Updating ~12 files with `sed -i '' 's|old|new|g'` was far faster than individual Read+Edit cycles
- For bulk string replacements in markdown (no syntax sensitivity), sed is the right tool
- The Edit tool is better for code where you need precision and context

### ADV-0070: Docs-only tasks should skip evaluator/self-review phases
- For `--type docs` tasks with zero code changes, adversarial evaluator and self-review phases add no value
- Consider adding a fast-path in the workflow that short-circuits phases 4, 5, and 8 for docs-only PRs

---

## Version Management (`adversarial_workflow/__init__.py`, `cli.py`)

### ADV-0071: `shutil.which()` finds stale system installs over venv binaries
- The `run_cli` test fixture used `shutil.which("adversarial")` which resolved to `/opt/homebrew/bin/adversarial` (stale system install) instead of the venv binary
- Fix: use `sys.executable` to ensure tests run against the same Python environment
- Pattern: always use `[sys.executable, "-m", "module"]` or `sys.executable` path for subprocess tests, never rely on PATH resolution

### ADV-0071: `PackageNotFoundError.__str__` produces garbled messages
- `PackageNotFoundError("adversarial-workflow")` formats as "No package metadata was found for adversarial-workflow" — but if you embed it in a larger string like `f"{pkg_name} is not installed"`, the result is garbled
- Fix: raise `RuntimeError` with a clean message instead of re-raising `PackageNotFoundError`

### ADV-0071: DRY refactor of `from . import __version__` breaks direct execution
- Making `cli.py` import `__version__` from `__init__.py` via relative import (`from . import __version__`) breaks `python adversarial_workflow/cli.py` direct execution
- The evaluator (arch-review-fast) suggested this DRY pattern, but it's incorrect for CLI entry points
- Fix: keep separate `importlib.metadata.version()` calls in both files — duplication is acceptable here
- Pattern: evaluator suggestions about import DRY should be validated against direct-execution use cases

---

## Evaluator Pipeline

### ADV-0071: Gemini Flash wraps verdicts in bold markdown, breaking extraction
- Gemini Flash evaluators output `**FAIL**` or `**NON_COMPLIANT**` while o1 outputs bare `FAIL`
- The verdict extraction regex worked by luck because most runs used o1
- This is a silent bug affecting all Gemini-based evaluators — tracked as ADV-0072
- Pattern: verdict extraction regex should strip markdown formatting before matching

### ADV-0071: Evaluator pipeline catches regressions TDD misses
- Round 1 evaluator flagged that the DRY relative import broke direct script execution
- Unit tests couldn't catch this because they import the module normally
- The evaluator pipeline earned its keep on this task — it found a real correctness regression

---

## Validation (`adversarial_workflow/utils/validation.py`)

### ADV-0072: Regex patterns for verdict extraction must be line-anchored
- Bold-wrapped verdicts (`**FAIL**`) can appear as incidental text mid-document (e.g., `**FAIL**ure modes discussed`)
- ALL verdict patterns must use `^\s*` prefix and `\s*$` or `(?::|\s*$)` suffix to prevent false positives from substring/mid-line matches
- Pattern ordering matters: higher-specificity patterns (keyed `Verdict:`) first, lower-specificity (bare line) last
- When adding new regex patterns to a group, **audit ALL existing sibling patterns** for the same class of vulnerability

### ADV-0072: CodeRabbit catches regex boundary issues TDD misses
- The original spec only proposed adding 2 patterns, but CodeRabbit progressively flagged that all 6 patterns had the same anchoring gap across 3 rounds
- The iterative bot-driven refinement expanded the fix scope correctly — more thorough than the original spec
- For regex-heavy changes, expect 2-3 bot rounds of boundary tightening

### ADV-0072: o1 evaluator doesn't recognize parametrized test coverage
- The code-review evaluator flagged "untested" cases that were actually covered by parametrized fixtures (`@pytest.mark.parametrize`)
- When writing evaluator dispositions, explicitly note which parametrized tests cover each finding
- Consider adding a note to evaluator input templates about parametrized test structures

---

*Last updated: 2026-04-15*
