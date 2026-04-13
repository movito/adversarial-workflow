# ADV-0066: Remove Aider Remnants — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-04-10
**From**: Planner
**To**: feature-developer-v5
**Task**: `delegation/tasks/2-todo/ADV-0066-remove-aider-remnants.md`
**Status**: Ready for implementation
**Evaluation**: ✅ REVISION_SUGGESTED (minor — both addressed in spec)

---

## Task Summary

Remove all remnants of the Aider dependency following the LiteLLM migration (ADV-0065, PR #60). This is a cleanup task: delete dead files, update CLI commands, fix tests, update CI, and update docs. No new features.

## Your Mission

### Phase 1: Update Tests (Red → Green)
- Remove `mock_aider_command` fixture from `conftest.py`
- Delete aider-specific test cases (`test_check_aider_not_installed`, `test_check_aider_installed`, `test_check_aider_version_retrieval`, `test_evaluate_aider_not_found`, `test_init_creates_aider_config`)
- Remove all `patch("shutil.which", return_value="/usr/bin/aider")` mocks from remaining tests
- Remove `aider_model` from config fixtures and assertions
- Update `test_python_version.py` — remove <3.13 constraint references
- Tests will fail at this point because CLI still checks for aider

### Phase 2: Update CLI Code (Green)
- `cli.py`: Remove aider from `init` (stop copying `.aider.conf.yml`), `check` (remove `shutil.which("aider")`), and `_print_getting_started` (remove install warning)
- `scripts/core/project`: Remove Python <3.13 upper bound check (lines 573-598)
- Tests should now pass

### Phase 3: Delete Dead Files + Update CI
- `git rm` the 5 shell script templates, 3 shell scripts, `.aider.conf.yml.template`, and `.adversarial/investigation/` directory
- Remove `pip install aider-chat` step from `.github/workflows/test-package.yml`
- Remove `.aider.conf.yml` existence check from CI
- Remove `aider-chat` from `.github/dependabot.yml`

### Phase 4: Update Docs
- README.md, SETUP.md, QUICK_START.md: Remove aider prerequisites, install steps, workflow examples
- UPGRADE.md: Add migration note
- Agent docs: `.claude/agents/onboarding.md`, `pypi-publisher.md`, `AGENT-TEMPLATE.md`
- Serena memories: `.serena/memories/project-overview.md`, `suggested_commands.md`
- CHANGELOG.md: Add removal entry under [Unreleased]

### Phase 5: Final Verify
- Regenerate `uv.lock`
- Run full test suite
- Run `./scripts/core/ci-check.sh`
- Final `grep -ri aider` sweep on live code directories

## Critical Details

### Files with highest aider reference count
1. `tests/test_cli_core.py` — 31 refs (mostly `shutil.which` mocks)
2. `adversarial_workflow/cli.py` — 27 refs (init, check, getting-started)
3. `tests/test_evaluate.py` — 14 refs (mock_which in every test)
4. `tests/conftest.py` — 10 refs (fixtures)

### DO NOT TOUCH (historical records)
- `docs/decisions/adr/` — ADRs are historical
- `delegation/tasks/5-done/`, `8-archive/` — Completed/archived tasks
- `CHANGELOG.md` — Existing entries stay; only add new [Unreleased] entry
- `.adversarial/logs/`, `.agent-context/retros/`, `.agent-context/reviews/`

### CLI `init` command — what to keep
The `init` command creates `.adversarial/config.yml`, evaluator directories, and templates. After this change it should still do all of that — just not create `.aider.conf.yml` or copy shell scripts.

### CLI `check` command — what to keep
The `check` command validates: Python version, API keys, config file, evaluator discovery. After this change it should still do all of that — just not check for aider binary.

## Resources

- **Task spec**: `delegation/tasks/2-todo/ADV-0066-remove-aider-remnants.md` (detailed inventory with line numbers)
- **Predecessor**: ADV-0065 (PR #60)
- **Evaluator output**: `.adversarial/logs/ADV-0066-remove-aider-remnants--arch-review-fast.md`

## Time Estimate

4 hours total:
- Phase 1 (Tests): 1 hour
- Phase 2 (CLI code): 1 hour
- Phase 3 (Delete + CI): 0.5 hours
- Phase 4 (Docs): 1 hour
- Phase 5 (Verify): 0.5 hours

---

**Task File**: `delegation/tasks/2-todo/ADV-0066-remove-aider-remnants.md`
**Handoff Date**: 2026-04-10
**Coordinator**: Planner
