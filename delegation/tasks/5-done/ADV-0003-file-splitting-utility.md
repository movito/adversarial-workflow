# ADV-0003: File Splitting Utility for Large Task Specifications

**Status**: Done
**Priority**: medium
**Assigned To**: feature-developer
**Estimated Effort**: 3-4 hours
**Created**: 2025-10-30
**Completed**: 2025-11-29

## Related Tasks

**Depends On**: None
**Blocks**: None
**Related**: ADV-0002 (tier upgrade analysis - alternative solution provided)

## Overview

Create a utility to help users split large task specification files into multiple smaller files that can be evaluated independently. Files >500 lines exceed OpenAI rate limits (30k TPM for Tier 1).

**Context**: Rather than requiring tier upgrades, provide tooling to help users work within existing rate limits by splitting large specifications into manageable chunks.

## Requirements

### Functional Requirements
1. Analyze task file structure and detect markdown sections
2. Suggest natural split points (by section, by phase)
3. Generate multiple smaller files with cross-references
4. Preserve file numbering/naming conventions
5. Support multiple split strategies (sections, phases, manual)

### Non-Functional Requirements
- [x] Performance: Split operation completes in <5 seconds
- [x] Reliability: Never break markdown structure across splits
- [x] Maintainability: Clean separation of analysis and generation logic

## Acceptance Criteria

### Must Have
- [x] `adversarial split` command implemented
- [x] Supports section-based splitting (default)
- [x] Supports phase-based splitting
- [x] Generates properly formatted split files
- [x] All tests passing (72 total, 19 new)
- [x] Coverage targets met (87% for new code)

### Should Have
- [x] Adds metadata and cross-references between files
- [x] Interactive user experience for strategy selection
- [x] `--dry-run` flag to preview splits

## Completion Summary

### Features Delivered

**Core Splitting Logic** (`adversarial_workflow/utils/file_splitter.py`):
- `analyze_task_file()` - Analyze file structure and detect sections
- `split_by_sections()` - Split by markdown headings with max line limits
- `split_by_phases()` - Split by Phase N patterns
- `split_at_lines()` - Manual splitting at specified line numbers
- `generate_split_files()` - Create split files with metadata

**CLI Integration** (`adversarial_workflow/cli.py`):
- New `adversarial split` command
- `--strategy` flag: 'sections' (default) or 'phases'
- `--max-lines` flag: configure limit (default: 500)
- `--dry-run` flag: preview without creating files
- Interactive confirmation before file creation

### Usage

```bash
# Analyze and split by sections (default)
adversarial split large-task.md

# Split by implementation phases
adversarial split large-task.md --strategy phases

# Preview without creating files
adversarial split large-task.md --dry-run

# Custom line limit
adversarial split large-task.md --max-lines 300
```

### Test Results
- All tests passing: 72 total (19 new)
- Coverage: 87% for new utils module
- Edge cases covered: empty files, small files, large files, invalid strategies

### Files Created/Modified
- `adversarial_workflow/utils/__init__.py` (new)
- `adversarial_workflow/utils/file_splitter.py` (new, 378 lines)
- `adversarial_workflow/cli.py` (modified, +714 lines)
- `tests/test_file_splitter.py` (new, 312 lines)
- `tests/test_split_command.py` (new, 138 lines)

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| Write failing tests | 1 hour | [x] |
| Implement analysis logic | 1 hour | [x] |
| Implement split strategies | 1 hour | [x] |
| CLI integration | 0.5 hours | [x] |
| Documentation | 0.5 hours | [x] |
| **Total** | **4 hours** | [x] |

## References

- **Commit**: `0a150bf`
- **Testing**: `pytest tests/test_file_splitter.py tests/test_split_command.py -v`
- **Coverage**: `pytest tests/ --cov=adversarial_workflow.utils`

---

**Template Version**: 2.0.0
**Project**: adversarial-workflow
**Last Updated**: 2025-11-29
