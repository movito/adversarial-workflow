# ADV-0066: Remove Aider Remnants from Codebase

**Status**: Done
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 3-5 hours
**Created**: 2026-04-10
**Depends On**: ADV-0065 (merged PR #60)

## Related Tasks

**Depends On**: ADV-0065 (Replace Aider with LiteLLM — DONE)
**Blocks**: v1.0.0 release (cannot ship with dead aider references)

## Overview

ADV-0065 replaced the Aider transport layer with LiteLLM, but left behind extensive remnants: dead shell scripts, obsolete templates, stale CLI checks, aider-specific test mocks, CI steps that install `aider-chat`, user-facing docs that tell users to install aider, and an investigation directory with aider log files. This task removes all of them.

**Context**: This is a cleanup task following a dependency removal. The codebase has 145 files mentioning "aider" — most are historical (ADRs, completed tasks, changelogs) and should be left alone. The actionable items fall into 6 categories below.

## Requirements

### Functional Requirements

1. **Delete dead artifacts** — Remove files that exist only to support the aider transport
2. **Update CLI `init` command** — Stop creating `.aider.conf.yml` and shell scripts
3. **Update CLI `check` command** — Remove aider installation check, remove Python <3.13 upper bound warning
4. **Update CI pipeline** — Remove `pip install aider-chat` step and `.aider.conf.yml` assertion
5. **Update tests** — Remove aider mocks, aider-specific assertions, update conftest fixtures
6. **Update user-facing docs** — Remove aider from prerequisites, setup instructions, workflow examples
7. **Clean up config** — Remove aider from dependabot, remove `.aider*` from `.gitignore` (optional), regenerate `uv.lock`

### Non-Functional Requirements
- [ ] No regressions — all existing tests pass after mock migration
- [ ] `adversarial init` still works (creates config, evaluators — just not aider files)
- [ ] `adversarial check` still works (validates API keys, config — just not aider binary)
- [ ] CI still passes

## Detailed Inventory

### Category 1: Delete Files (dead artifacts)

| File | Reason |
|------|--------|
| `.aider.chat.history.md` | Aider session history (gitignored, on disk) |
| `.aider.input.history` | Aider input history (gitignored, on disk) |
| `.adversarial/scripts/evaluate_plan.sh` | Built-in evaluator — replaced by `builtins.py` inline prompts |
| `.adversarial/scripts/review_implementation.sh` | Same |
| `.adversarial/scripts/validate_tests.sh` | Same |
| `adversarial_workflow/templates/.aider.conf.yml.template` | `init` used to copy this — no longer needed |
| `adversarial_workflow/templates/evaluate_plan.sh.template` | Template for shell script evaluators — dead |
| `adversarial_workflow/templates/proofread_content.sh.template` | Same |
| `adversarial_workflow/templates/review_implementation.sh.template` | Same |
| `adversarial_workflow/templates/validate_tests.sh.template` | Same |
| `.adversarial/investigation/` (all 8 files) | Old aider file-size investigation — historical, no value |

### Category 2: Update Live Code

#### `adversarial_workflow/cli.py` (27 references)

- **`init` command** (~line 640, 740-743): Remove `.aider.conf.yml.template` from template list, stop copying it to project root
- **`check` command** (~line 335): Remove `"✓ .aider.conf.yml"` from success output
- **`check` command** (~line 868-883): Remove `shutil.which("aider")` check and version retrieval
- **`check` command** (~line 1331-1345): Remove second aider version check block
- **`_print_getting_started`** (~line 1909-1920): Remove "aider not found" warning and install instructions
- **`check` command** (~line 668): Remove aider config documentation link
- **General**: Remove `"aider"` from any feature descriptions or help text (line 496)

#### `scripts/core/project` (3 references)

- **Line 250**: Remove `.aider` from `exclude_dirs` set (or leave — harmless)
- **Lines 573-598**: Remove Python <3.13 upper bound check and aider-chat constraint message. Python 3.13+ is now supported.

#### `adversarial_workflow/evaluators/runner.py` (0 references — already clean from ADV-0065)

Confirmed clean — no action needed.

### Category 3: Update Tests

#### `tests/conftest.py` (10 references)

- **Line 31**: Remove `aider_model: gpt-4o` from sample config fixture
- **Lines 104-108**: Remove/update "mock subprocess.run to avoid running actual aider" comments
- **Line 127**: Remove `"aider_model"` from config dict
- **Lines 170-208**: Remove `mock_aider_command` fixture entirely — dead after LiteLLM migration

#### `tests/test_cli_core.py` (31 references)

- **Lines 116-124**: Update `test_init_creates_aider_config` — remove or convert to negative test (init should NOT create `.aider.conf.yml`)
- **Lines 288, 333, 349, etc.**: ~20 places mock `shutil.which` returning `/usr/bin/aider` — remove these mocks from tests that don't specifically test aider detection
- **Lines 312-324**: `test_check_aider_not_installed` — remove entirely
- **Lines 324-349**: `test_check_aider_installed` — remove entirely
- **Lines 811-837**: `test_check_aider_version_retrieval` — remove entirely
- **Line 1413**: Remove `.aider.conf` from copy assertion

#### `tests/test_evaluate.py` (14 references)

- **Line 47-53**: `test_evaluate_aider_not_found` — remove entirely (aider is no longer checked)
- **Lines 75, 115, 154, etc.**: Remove `mock_which.return_value = "/usr/bin/aider"` from remaining tests
- **Line 447**: `test_evaluate_with_sample_task` — update mock from aider to litellm

#### `tests/test_config.py` (1 reference)

- **Line 154**: Remove assertion for `aider_model` in sample config

#### `tests/test_python_version.py` (2 references)

- **Lines 5, 29**: Remove aider-chat constraint comments. Python 3.13+ is now supported — update test to reflect new `requires-python` range.

#### `tests/test_litellm_transport.py` (1 reference)

- **Line 3, 353**: Comment/docstring references — update wording from "replaces subprocess.run(["aider"])" to past tense or remove

### Category 4: Update CI/Config

#### `.github/workflows/test-package.yml`

- **Line 89-91**: Remove `Install aider-chat` step (`pip install aider-chat`)
- **Line 125**: Remove `.aider.conf.yml` existence assertion (`test -f .aider.conf.yml || exit 1`)

#### `.github/dependabot.yml`

- **Line 29**: Remove `"aider-chat"` from dependency ignore list

#### `.gitignore`

- Remove `.aider*` line (optional — harmless to keep, but signals dead config)

#### `uv.lock`

- Regenerate after `pyproject.toml` no longer lists `aider-chat` (already done in ADV-0065, but verify)

### Category 5: Update User-Facing Docs

#### `README.md` (~20 references)

- Remove Python 3.13 warning (line 136)
- Remove "including aider-chat" from install note (line 162)
- Update architecture description: "Evaluator (aider + GPT-4o)" → "Evaluator (LiteLLM + configured model)" (lines 347, 361, 368)
- Remove "No special agent system — just aider + API keys" (line 382)
- Remove aider workflow examples (lines 389, 401, 406, 410, 420-423, 773-782)
- Update config example: remove `evaluator_model` aider reference (line 457)
- Update `adversarial check` description (line 470)

#### `SETUP.md`

- Remove "Python 3.11+ required for aider compatibility" (line 11)
- Update prerequisites

#### `QUICK_START.md` (~15 references)

- Remove entire "Step 1: Install aider" section (lines 28-45)
- Remove aider workflow examples (lines 349, 471-472)
- Update workflow to show `adversarial <evaluator>` directly

#### `UPGRADE.md`

- Add v1.0.0 migration note: aider no longer required, install litellm instead

#### `AGENT_INTEGRATION.md`

- Update any aider references to LiteLLM

### Category 6: Update Agent/Workflow Docs

#### `.agent-context/workflows/AGENT-CREATION-WORKFLOW.md`

- Update any aider references

#### `.claude/agents/onboarding.md`

- Remove aider from onboarding checks

#### `.claude/agents/AGENT-TEMPLATE.md`

- Remove aider references if present

#### `.claude/agents/pypi-publisher.md`

- Remove aider from dependency notes

#### `.serena/memories/project-overview.md`, `.serena/memories/suggested_commands.md`

- Update to reflect LiteLLM transport

### DO NOT TOUCH (historical records)

- `docs/decisions/adr/` — ADRs are historical; aider references are accurate for when they were written
- `delegation/tasks/5-done/` — Completed task specs
- `delegation/tasks/8-archive/` — Archived tasks
- `delegation/handoffs/` — Historical handoffs
- `docs/project-history/` — Phase completion summaries
- `docs/proposals/` — Historical proposals
- `docs/internal/` — Internal docs
- `docs/decisions/archive/` — Archived decisions
- `CHANGELOG.md` — Historical entries stay; add new entry under [Unreleased] noting removal
- `audit-results/` — Historical audits
- `.adversarial/logs/` — Evaluation outputs
- `.agent-context/retros/` — Session retrospectives
- `.agent-context/reviews/` — Review outputs
- `.adversarial/inputs/` — Evaluator input snapshots

## TDD Workflow (Mandatory)

**Test-Driven Development Approach**:

1. **Red**: Update tests first — remove aider mocks, aider-specific test cases
2. **Green**: Update CLI code to remove aider checks, update init/check commands
3. **Refactor**: Delete dead files, update docs
4. **Commit**: Pre-commit hook runs tests automatically

### Test Requirements
- [ ] All aider-specific test mocks removed or migrated
- [ ] `test_init_creates_aider_config` removed or inverted
- [ ] `test_check_aider_not_installed` and `test_check_aider_installed` removed
- [ ] `mock_aider_command` fixture removed from conftest.py
- [ ] No test references `shutil.which("aider")` or `/usr/bin/aider`
- [ ] All remaining tests pass
- [ ] Coverage: 80%+ for modified code

**Test files to modify**:
- `tests/conftest.py`
- `tests/test_cli_core.py`
- `tests/test_evaluate.py`
- `tests/test_config.py`
- `tests/test_python_version.py`
- `tests/test_litellm_transport.py` (minor — comment update)

## Implementation Plan

### Approach

**Step 1: Update Tests (Red → Green)**
1. Remove `mock_aider_command` fixture from `conftest.py`
2. Remove aider-specific test cases from `test_cli_core.py` and `test_evaluate.py`
3. Remove `shutil.which` aider mocks from remaining tests
4. Update `test_config.py` to remove `aider_model` assertion
5. Update `test_python_version.py` to remove <3.13 constraint
6. Run test suite — some tests will fail because CLI still checks for aider

**Step 2: Update CLI Code (Green)**
1. Remove aider checks from `init` command (stop copying `.aider.conf.yml`)
2. Remove aider checks from `check` command (remove `shutil.which("aider")`)
3. Remove aider warning from `_print_getting_started`
4. Run test suite — all should pass

**Step 3: Update scripts/core/project**
1. Remove Python <3.13 upper bound check
2. Optionally remove `.aider` from exclude_dirs

**Step 4: Update CI**
1. Remove `pip install aider-chat` from `.github/workflows/test-package.yml`
2. Remove `.aider.conf.yml` existence check
3. Remove `aider-chat` from `.github/dependabot.yml`

**Step 5: Delete Dead Files**
1. `git rm` all files in Category 1
2. Remove `.aider*` from `.gitignore` (optional)

**Step 6: Update User-Facing Docs**
1. Update README.md, SETUP.md, QUICK_START.md, UPGRADE.md
2. Update agent/workflow docs

**Step 7: Lock file + CHANGELOG + Final Verify**
1. Regenerate `uv.lock`: `uv lock` (verify aider-chat is gone from lock file)
2. Add entry under [Unreleased]: "Removed: Aider dependency and all related artifacts"
3. Run full test suite: `pytest tests/ -v`
4. Run `./scripts/core/ci-check.sh`
5. Final sweep: `grep -ri aider adversarial_workflow/ scripts/ tests/ .github/ .claude/ .agent-context/workflows/ README.md SETUP.md QUICK_START.md UPGRADE.md` — confirm only historical/archival hits remain

## Acceptance Criteria

### Must Have
- [ ] Zero `shutil.which("aider")` calls in live code
- [ ] Zero `pip install aider-chat` in CI
- [ ] All 5 shell script templates deleted
- [ ] All 3 shell scripts deleted
- [ ] `.adversarial/investigation/` directory deleted
- [ ] `init` command no longer creates `.aider.conf.yml`
- [ ] `check` command no longer checks for aider
- [ ] Python <3.13 constraint removed from `scripts/core/project`
- [ ] All tests passing
- [ ] No regressions
- [ ] README and QUICK_START no longer tell users to install aider

### Should Have
- [ ] `mock_aider_command` fixture removed from conftest.py
- [ ] All aider-specific test cases removed
- [ ] UPGRADE.md documents the migration
- [ ] CHANGELOG.md updated

### Must Have (continued)
- [ ] Final `grep -ri aider` on live code confirms only historical/archival references remain

### Nice to Have
- [ ] `.aider*` removed from `.gitignore`

## Success Metrics

### Quantitative
- Test pass rate: 100%
- Live code aider references: 0 (down from 82)
- Files deleted: ~16
- Lines removed: ~200+

### Qualitative
- New user running `adversarial init && adversarial check` sees no mention of aider
- README gives accurate setup instructions (LiteLLM, not aider)
- CI pipeline is leaner (no aider-chat install step)

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| Update tests (remove aider mocks) | 1 hour | [ ] |
| Update CLI code (init, check) | 1 hour | [ ] |
| Update CI + delete dead files | 0.5 hours | [ ] |
| Update docs (README, SETUP, etc.) | 1 hour | [ ] |
| Full test suite + verify | 0.5 hours | [ ] |
| **Total** | **4 hours** | [ ] |

## PR Plan

Single PR — ~300 lines changed, ~400 deleted. Comfortable single-PR scope.

**Branch**: `feature/ADV-0066-remove-aider-remnants`

## References

- **Predecessor**: ADV-0065 (PR #60, merged 2026-04-10)
- **GitHub Issue**: #59 (covers both ADV-0065 and this cleanup)
- **Testing**: `pytest tests/ -v`
- **Coverage**: `pytest tests/ --cov=adversarial_workflow`
- **Pre-commit**: `pre-commit run --all-files`

---

**Template Version**: 2.0.0
**Project**: adversarial-workflow
**Last Updated**: 2026-04-10
