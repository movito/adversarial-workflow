# ADV-0003: File Splitting Utility for Large Task Specifications

**Status**: Backlog
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 3-4 hours
**Created**: 2025-10-30

## Related Tasks

**Depends On**: None (can implement independently)
**Blocks**: None
**Related**: ADV-0002 (tier upgrade analysis - alternative solution)

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
- [ ] Performance: Split operation completes in <5 seconds
- [ ] Reliability: Never break markdown structure across splits
- [ ] Maintainability: Clean separation of analysis and generation logic

## TDD Workflow (Mandatory)

**Test-Driven Development Approach**:

1. **Red**: Write failing tests for splitting logic
2. **Green**: Implement minimum code until tests pass
3. **Refactor**: Improve code while keeping tests green
4. **Commit**: Pre-commit hook runs tests automatically

### Test Requirements
- [ ] Unit tests for file analysis functions
- [ ] Unit tests for each split strategy
- [ ] Error handling tests for edge cases (empty files, no sections)
- [ ] Coverage: 80%+ for new code

**Test files to create**:
- `tests/test_file_splitter.py` - Main test suite

## Implementation Plan

### Files to Modify

1. `adversarial_workflow/cli.py` - Add `split` command
   - Function: New `cmd_split()` function
   - Change: Add command to CLI parser

### Files to Create

1. `adversarial_workflow/utils/file_splitter.py` - Splitting logic
   - Purpose: Core file analysis and splitting functionality

2. `tests/test_file_splitter.py` - Test suite
   - Purpose: Test coverage for splitting functionality

### Approach

**Step 1: Core Analysis Logic**

Implement file structure analysis.

**TDD cycle**:
1. Write tests: Test `analyze_task_file()` returns section info
2. Run tests (should fail): `pytest tests/test_file_splitter.py -v`
3. Implement feature: Parse markdown headings, estimate tokens
4. Run tests (should pass): `pytest tests/test_file_splitter.py -v`

```python
def analyze_task_file(file_path: str) -> dict:
    """Analyze file structure and suggest split points."""
    # Parse markdown headings
    # Estimate tokens per section
    # Identify natural boundaries
```

**Step 2: Split Strategies**

Implement different splitting approaches.

**TDD cycle**:
1. Write tests: Test each split strategy
2. Run tests (should fail): `pytest tests/test_file_splitter.py -v`
3. Implement feature: `split_by_sections()`, `split_by_phases()`, `split_at_lines()`
4. Run tests (should pass): `pytest tests/test_file_splitter.py -v`

```python
def split_by_sections(content: str, max_lines: int = 500) -> list[dict]:
    """Split file by markdown sections."""

def split_by_phases(content: str) -> list[dict]:
    """Split file by implementation phases."""

def split_at_lines(content: str, line_numbers: list[int]) -> list[dict]:
    """Split at specified line numbers."""
```

**Step 3: CLI Integration**

Add `split` command to CLI.

**TDD cycle**:
1. Write tests: Test CLI command invocation
2. Run tests (should fail): `pytest tests/test_file_splitter.py -v`
3. Implement feature: Add command to cli.py, wire up to splitter
4. Run tests (should pass): `pytest tests/test_file_splitter.py -v`

## Acceptance Criteria

### Must Have
- [ ] `adversarial split` command implemented
- [ ] Supports section-based splitting (default)
- [ ] Supports phase-based splitting
- [ ] Generates properly formatted split files
- [ ] All tests passing
- [ ] Coverage targets met (80%+ new code)

### Should Have
- [ ] Adds metadata and cross-references between files
- [ ] Interactive user experience for strategy selection
- [ ] `--dry-run` flag to preview splits

## Success Metrics

### Quantitative
- Test pass rate: 100%
- Coverage: 80%+ for new code
- Handles files up to 2000+ lines

### Qualitative
- Split files are self-contained and readable
- Cross-references maintain context
- User experience is intuitive

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| Write failing tests | 1 hour | [ ] |
| Implement analysis logic | 1 hour | [ ] |
| Implement split strategies | 1 hour | [ ] |
| CLI integration | 0.5 hours | [ ] |
| Documentation | 0.5 hours | [ ] |
| **Total** | **4 hours** | [ ] |

## References

- **Testing**: `pytest tests/test_file_splitter.py -v`
- **Coverage**: `pytest tests/ --cov=adversarial_workflow`
- **Pre-commit**: `pre-commit run --all-files`
- **Example usage**: `adversarial split delegation/tasks/active/TASK-large.md`

---

**Template Version**: 2.0.0
**Project**: adversarial-workflow
**Last Updated**: 2025-11-28
