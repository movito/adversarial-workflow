# ADV-0055: Enhance `adversarial health` with Script & Config Validation

**Status**: Todo
**Priority**: Medium
**Type**: Enhancement
**Estimated Effort**: 2-3 hours
**Created**: 2026-03-15
**Depends On**: ADV-0054

## Summary

`adversarial health` currently checks that workflow scripts exist and are executable, but
doesn't validate their **content**, **version**, or **compatibility** with the installed
package. This gap allowed stale scripts in downstream projects (research-method-matrix,
epistemic-drift) to go undetected until they failed at runtime.

Enhance the health check to catch these issues proactively.

## Background

The RMM-0001 incident (see ADV-0054) revealed that a project duplicated from
epistemic-drift inherited `review_implementation.sh` at `SCRIPT_VERSION: 0.9.8` while the
installed CLI was `0.9.9`. The health check reported the script as healthy because it
existed and was executable — but it was missing critical fixes (`mkdir -p`, branch-aware
`git diff`).

## New Checks to Add

### 1. Script version comparison

Parse `SCRIPT_VERSION:` from local `.adversarial/scripts/*.sh` and compare against the
version embedded in the installed package's templates.

```
✅ review_implementation.sh - v0.9.9 (matches package)
⚠️  evaluate_plan.sh - v0.9.6 (package has v0.9.9, run: adversarial upgrade)
```

**Implementation notes**:
- Add a `SCRIPT_VERSION` comment to each template if not already present
- Store the package version in the template (e.g., via `__version__` import or hardcoded)
- Use semver comparison — warn if local < package, info if local > package (custom fork)

### 2. Artifacts directory check

Add `.adversarial/artifacts/` to the directory checks alongside `log_directory` and
`task_directory`.

```
✅ artifacts_directory: .adversarial/artifacts/ (writable)
❌ artifacts_directory: .adversarial/artifacts/ (not found)
   Fix: mkdir -p .adversarial/artifacts/
```

### 3. Config completeness

Warn when `config.yml` is missing fields that the scripts depend on (with defaults shown).

```
⚠️  artifacts_directory not set in config.yml (default: .adversarial/artifacts/)
```

**Fields to check**: `evaluator_model`, `task_directory`, `log_directory`,
`artifacts_directory`, `test_command`.

### 4. Skill command validation (optional, nice-to-have)

Scan `.claude/commands/*.md` for `adversarial <subcommand>` invocations and verify each
subcommand exists in the CLI's registered commands.

```
❌ check-spec.md references 'adversarial spec-compliance-fast' — command not found
   Closest match: adversarial evaluate --evaluator spec-compliance
```

**Implementation notes**:
- Parse markdown code blocks for `adversarial ` patterns
- Compare against the known subcommands set in `cli.py`
- This is a nice-to-have — don't block the task on it

## Acceptance Criteria

- [ ] `adversarial health` reports script version vs. package version mismatch
- [ ] `adversarial health` checks artifacts directory exists and is writable
- [ ] `adversarial health` warns on missing config fields with defaults
- [ ] All existing health check tests still pass
- [ ] New checks have test coverage

## Should Have

- [ ] Skill command validation (check `.claude/commands/*.md` references)

## Files to Modify

1. `adversarial_workflow/cli.py` — `health()` function (~line 1098)
2. `adversarial_workflow/templates/*.sh.template` — ensure `SCRIPT_VERSION` is present
3. Tests — new test cases for the added health checks

## Notes

- ADV-0054 fixes the bugs themselves; this task makes them detectable before they cause failures
- Consider whether `adversarial check` (the simpler command) should also gain some of these checks, or keep them in `health` only
- The script version check is the foundation for ADV-0056 (`adversarial upgrade`)
