## ADV-0065 — Replace Aider Transport with LiteLLM (PR #60)

**Date**: 2026-04-10
**Agent**: feature-developer-v5
**Scorecard**: 14 threads, 0 regressions, 2 fix rounds, 5 commits (11 on branch pre-squash)

### What Worked

1. **Handoff file was excellent** — The `.agent-context/ADV-0065-HANDOFF-litellm-transport.md` gave precise file-by-file scope, pre-identified the `ModelResolver` contract, and listed exact functions to remove. Implementation started immediately with no ambiguity.
2. **TDD caught the verdict token mismatch** — Writing tests against `_REJECT_VERDICTS` revealed that the evaluate prompt used `REJECT` while the parser expects `REJECTED`. CodeRabbit also caught this independently, confirming the test-first approach works.
3. **Bot triage was efficient** — 14 threads across cursor[bot] and CodeRabbit, all addressed in 2 fix commits (ead35a5, 1cfeca9). The `resolved_api_key_env` parameter addition (cursor finding) was a genuine improvement.

### What Was Surprising

1. **CI failed on ruff format, not tests** — The actual test suite passed fine, but CI gate failed because `runner.py` and `test_evaluator_runner.py` had trailing blank lines. This was a formatting-only fix (commit 52a6067) that burned an extra CI cycle.
2. **Evaluator returned FAIL on all false positives** — `code-reviewer-fast` (gemini-2.5-flash) flagged 5 issues, all of which were either already fixed, false positives (custom evaluators "relying on aider"), or acknowledged out-of-scope (Python 3.13 CI). The evaluator's value was low for this task.
3. **Local main diverged from origin** — After merge, `git pull --rebase` hit conflicts because local main had pre-squash commits that were already upstream via the squash merge. Required manual `git reset --hard origin/main` (which needed user permission).

### What Should Change

1. **Always run `ruff format` before every commit** — The CI failure was avoidable. Consider adding `ruff format` to the inner loop after every code change, not just after Serena edits. The pre-commit hook should catch this but didn't fire on the CodeRabbit fix commit.
2. **CI checker agent needs bash permission** — The `ci-checker` agent launched in Phase 7 couldn't run any commands due to missing bash permissions. It returned a permission error instead of CI status. Either fix the agent's permissions or stop using it.
3. **Reset local main before starting feature branches** — The diverged-main issue cost time at merge. Feature branches should start from a freshly-fetched `origin/main`, and after merge the local main should be reset to origin immediately.

### Permission Prompts Hit

1. `git push --force-with-lease origin feature/ADV-0065-replace-aider-with-litellm` — denied (during rebase attempt). Not needed in the end since PR was already merged via GitHub.
2. `git reset --hard origin/main` — denied. User had to run manually. This is a common post-merge cleanup pattern that could be added to the allow list.

### Process Actions Taken

- [ ] Add `ruff format <changed-files>` to inner loop after every code edit (not just Serena)
- [ ] Fix ci-checker agent bash permissions or document the limitation
- [ ] Add `git reset --hard origin/main` to settings.json allow list for post-merge cleanup
- [ ] Consider reducing evaluator weight for transport-swap tasks (low signal-to-noise)
