# ADV-0066 Review Starter — Remove Aider Remnants

**PR**: https://github.com/movito/adversarial-workflow/pull/61
**Branch**: `feature/ADV-0066-remove-aider-remnants`
**Task**: `delegation/tasks/4-in-review/ADV-0066-remove-aider-remnants.md`

## Summary

Systematic removal of all aider references from live code following the LiteLLM
migration (ADV-0065, PR #60). This is a cleanup task — no new features, just
deletions, reference updates, and CLI command rewiring.

## Key Changes

### CLI commands rewired (cli.py)
- `evaluate()` → now calls `run_evaluator(builtin_config, task_file)` instead of shelling out to `evaluate_plan.sh`
- `review()` → same pattern, uses `run_evaluator()` with "review" builtin
- `validate()` → direct `subprocess.run(shlex.split(test_command))` instead of `validate_tests.sh`
- `health()` → removed dead script-check code
- Log file selection now filters by evaluator `output_suffix` for reliability

### Files deleted (16)
- 3 shell scripts: `.adversarial/scripts/{evaluate_plan,review_implementation,validate_tests}.sh`
- 5 templates: `adversarial_workflow/templates/{.aider.conf.yml,evaluate_plan.sh,proofread_content.sh,review_implementation.sh,validate_tests.sh}.template`
- 8 investigation files: `.adversarial/investigation/test_file_*.{md,txt}`

### Tests updated
- Removed aider mocks (`mock_aider_command`, `shutil.which("aider")`)
- Mocks now target `adversarial_workflow.evaluators.runner.run_evaluator`
- Fixed impossible test state: NEEDS_REVISION test now correctly mocks `run_evaluator` returning 1

### CI updated
- Removed `pip install aider-chat` step
- Bash compatibility job validates init structure instead of deleted scripts

### Docs updated
- README, SETUP, QUICK_START, TROUBLESHOOTING, UPGRADE, AGENT_INTEGRATION
- Agent/workflow docs: onboarding, pypi-publisher, agent-template, agent-creation-workflow
- Serena memories updated

## Review Focus Areas

1. **cli.py evaluate()/review()**: Verify the `run_evaluator()` integration is correct — especially log file selection by `output_suffix`
2. **validate()**: Verify `shlex.split()` handling is robust
3. **Test coverage**: Verify removed tests are truly dead and replacements cover the new code paths
4. **Doc accuracy**: Verify no lingering aider references in user-facing docs

## Pre-Existing Issues

See `.agent-context/ADV-0066-preexisting-issues.md` for issues found during
this task that are pre-existing (dead verdict handling in cli.evaluate(),
empty test_command edge case, etc.). These should be a separate follow-up task.

## Bot Review Summary

- **CodeRabbit**: 12 threads across 3 rounds, all resolved
  - Round 1: 4 threads (markdown, QUICK_START sync, SETUP version, CI job)
  - Round 2: 6 threads (duplicate file gate, log selection, shlex.split, TOC anchor, review workaround, venv command)
  - Round 3: 2 threads (false positive on builtin key, impossible test mock)
- **BugBot**: No findings
- **Evaluator**: code-reviewer-fast ran; findings were false positives (code already handles FileNotFoundError, returncode, file existence)

## Verification

```bash
# All tests pass
pytest tests/ -v  # 539 passed

# CI green on all matrix combinations
# Python 3.10/3.11/3.12, Ubuntu/macOS

# No aider references in live code
grep -ri aider adversarial_workflow/ scripts/ tests/ .github/ .claude/ .agent-context/workflows/ README.md SETUP.md QUICK_START.md UPGRADE.md
# Only historical/archival hits remain
```
