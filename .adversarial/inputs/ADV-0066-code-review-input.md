# Code Review Input: ADV-0066 Remove Aider Remnants

## Task Summary
Systematic removal of all aider references from the codebase following LiteLLM migration (ADV-0065). This is a cleanup task — no new features, just deletions and reference updates.

## Scope
- 16 dead files deleted (shell scripts, templates, investigation files)
- CLI commands updated: evaluate(), review(), validate() now use run_evaluator() instead of shell scripts
- Tests updated: removed aider mocks, added run_evaluator mocks
- CI updated: removed aider-chat install step, updated bash compatibility job
- Docs updated: README, SETUP, QUICK_START, TROUBLESHOOTING, UPGRADE, AGENT_INTEGRATION
- Agent/workflow docs updated

## Key Code Changes

### adversarial_workflow/cli.py
- evaluate(): Replaced subprocess.run of evaluate_plan.sh with run_evaluator(builtin_config, task_file)
- review(): Replaced subprocess.run of review_implementation.sh with run_evaluator(builtin_config, task_file)
- validate(): Replaced subprocess.run of validate_tests.sh with direct subprocess.run using shlex.split()
- health(): Removed dead script-check code
- Log file selection now filters by evaluator output_suffix instead of newest *.md glob

### tests/test_evaluate.py
- Removed aider-specific tests (missing_script, rate_limit, timeout, windows_error)
- Added: test_evaluate_builtin_not_found, test_evaluate_run_evaluator_failure, test_evaluate_delegates_to_run_evaluator
- All mocks now target adversarial_workflow.evaluators.runner.run_evaluator

### .github/workflows/test-package.yml
- Removed pip install aider-chat
- Updated bash compatibility job to verify init structure instead of validating deleted scripts

## Test Results
- 539 tests pass
- CI green on all matrix combinations (Python 3.10/3.11/3.12, Ubuntu/macOS)

## Bot Review Status
- 10 CodeRabbit threads raised across 2 rounds, all fixed and resolved
- BugBot: no findings
