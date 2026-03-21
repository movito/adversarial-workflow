# ADV-0057 Retro — Review Script Robustness

**Date**: 2026-03-21
**Agent**: feature-developer-v4
**PR**: #56 (MERGED)
**Duration**: ~45 min active work + 10 min bot wait

## What went well

- **Clean PR**: Both bots (CodeRabbit, BugBot) approved with 0 threads — no triage rounds needed
- **Evaluator alignment**: Both adversarial evaluators (Gemini Flash, OpenAI o1) found CONCERNS but 0 bugs in the actual changes — all findings were pre-existing
- **Targeted scope**: 4 independent fixes, 4 files modified, no scope creep
- **Test coverage**: Added 2 new tests for Fix 3 (CLI error handling), 545 total passing

## What could be improved

- **Branch management**: Git checkout got confused mid-session — edits were applied to `main` instead of the feature branch, requiring re-application. Need to verify branch after each checkout with `git log --oneline -3`
- **File reversion**: The `.adversarial/scripts/review_implementation.sh` and template reverted unexpectedly (system reminders showed external modification). Had to re-apply fixes twice
- **Evaluator invocation**: First evaluator run used file paths instead of evaluator names — should use short names (`code-reviewer`, `code-reviewer-fast`)

## Learnings

- `adversarial evaluate` takes evaluator **names** not file paths (e.g. `code-reviewer` not `.adversarial/evaluators/openai-code-reviewer.yml`)
- Always verify branch with `git branch --show-current` before editing, not just after checkout
- For bash script changes, both script and template must be edited — verify sync with `grep -n "ADV-XXXX"` across both files

## Follow-up

- Created ADV-0064 in backlog for pre-existing evaluator findings (8 items, all latent)
