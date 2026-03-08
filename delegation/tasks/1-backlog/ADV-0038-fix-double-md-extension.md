# ADV-0038: Fix Double `.md.md` Extension in Evaluator Output Filenames

**Status**: Backlog
**Priority**: Medium
**Type**: Bug Fix
**Estimated Effort**: 30 minutes
**Created**: 2026-02-28

## Problem

Every evaluator output file in `.adversarial/logs/` has a double `.md.md`
extension. For example:

```text
DSP-0055-spec-compliance-input--spec-compliance.md.md
dispatch-kit-design--gemini-deep.md.md
DSP-0008-arch-planner-input--architecture-planner.md.md
```

This affects **all** evaluator outputs across all downstream projects
(dispatch-kit, agentive-starter-kit, etc.).

## Root Cause

Double appending of `.md` in `evaluators/runner.py`:

1. Evaluator YAML files define `output_suffix` **with** `.md`:

   ```yaml
   output_suffix: -spec-compliance.md
   ```

2. Runner code **also appends** `.md`:

   ```python
   # runner.py line 132 (_run_custom_evaluator)
   output_file = logs_dir / f"{file_basename}-{config.output_suffix}.md"

   # runner.py line 255 (_execute_script)
   log_file = Path(project_config["log_directory"]) / f"{file_basename}-{config.output_suffix}.md"
   ```

3. Result: `{basename}-{suffix}.md` → `{basename}--spec-compliance.md.md`

## Fix Options

### Option A: Strip `.md` from suffix in runner (recommended)

Backward-compatible. Handles both old and new YAML definitions.

```python
# In both locations in runner.py:
suffix = config.output_suffix
if suffix.endswith(".md"):
    suffix = suffix[:-3]
output_file = logs_dir / f"{file_basename}-{suffix}.md"
```

### Option B: Remove `.md` from all evaluator YAML files

Cleaner but requires updating every evaluator YAML (including library
evaluators in adversarial-evaluator-library).

```yaml
# Before:
output_suffix: -spec-compliance.md
# After:
output_suffix: -spec-compliance
```

## Scope

- `adversarial_workflow/evaluators/runner.py`: Fix lines 132 and 255
- Tests: Update filename expectations in test suite
- Consider: migration note for existing `.md.md` files in downstream projects

## Discovered By

CodeRabbit flagged the double extension in dispatch-kit PR #55
([comment](https://github.com/movito/dispatch-kit/pull/55#discussion_r2866874965)).
Confirmed systematic across 80+ files in dispatch-kit's `.adversarial/logs/`.
