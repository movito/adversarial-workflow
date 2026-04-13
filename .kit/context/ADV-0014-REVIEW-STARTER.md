# Review Starter: ADV-0014

**Task**: ADV-0014 - Evaluator Library CLI Enhancements
**Task File**: `delegation/tasks/4-in-review/ADV-0014-library-cli-enhancements.md`
**Branch**: feat/adv-0014-library-cli-enhancements → main
**PR**: https://github.com/movito/adversarial-workflow/pull/22

## Implementation Summary

- Added `adversarial library info <provider/name>` command for detailed evaluator info
- Added `--dry-run` flag to preview install/update without making changes
- Added `--category` flag to install all evaluators in a category at once
- Added `--yes` flag and non-TTY detection for CI/CD pipeline support
- Added configuration system with precedence: env vars > config file > defaults
  - `ADVERSARIAL_LIBRARY_URL`: Override library repository URL
  - `ADVERSARIAL_LIBRARY_NO_CACHE`: Disable caching
  - `ADVERSARIAL_LIBRARY_CACHE_TTL`: Override cache TTL
  - `.adversarial/config.yml` library section support

## Files Changed

- `adversarial_workflow/library/config.py` (new) - Configuration system
- `adversarial_workflow/library/client.py` (modified) - Use config, add fetch_readme
- `adversarial_workflow/library/commands.py` (modified) - Add info command, dry-run, category, yes flags
- `adversarial_workflow/library/__init__.py` (modified) - Export new functions
- `adversarial_workflow/cli.py` (modified) - Register new CLI options
- `tests/test_library_enhancements.py` (new) - 18 new tests
- `tests/test_library_commands.py` (modified) - Add isatty mock fixture
- `tests/test_library_integration.py` (modified) - Add isatty mock fixture

## Test Results

- 373 tests passing (18 new tests for this feature)
- 58% overall coverage (library module 65-84% coverage)
- CI passed on GitHub Actions

## Areas for Review Focus

1. **Config precedence logic** in `config.py` - env > file > defaults
2. **Non-TTY detection** - Proper error handling when stdin is not a terminal
3. **Dry-run implementation** - Preview mode for install and update
4. **Category installation** - Batch install logic with confirmation prompt
5. **Error handling** - Graceful failures for network errors, missing evaluators

## Related ADRs

None specifically, but follows patterns from ADV-0013 (Library CLI Core).

---

## Round 2 Fixes (2026-02-05)

Addressed all HIGH and MEDIUM priority findings from Round 1:

1. **HIGH: Config precedence bug** - Fixed by reordering: `CACHE_TTL` is now processed before `NO_CACHE`, so `NO_CACHE` always wins
2. **MEDIUM: Non-TTY detection** - Added `not dry_run` condition so dry-run works in CI/CD without `--yes`
3. **MEDIUM: Dry-run success count** - Added `preview_success` flag to only count successful previews

Added new test: `test_config_no_cache_takes_precedence_over_ttl`

All 374 tests passing. CI passed on GitHub Actions (12/12 jobs).

---
**Ready for code-reviewer Round 2 in new tab**
