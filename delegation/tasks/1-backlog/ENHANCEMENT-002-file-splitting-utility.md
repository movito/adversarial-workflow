# ENHANCEMENT-002: File Splitting Utility for Large Task Specifications

**Created**: 2025-10-30
**Priority**: MEDIUM
**Type**: Enhancement / Tool
**Estimated Time**: 3-4 hours
**Parent Task**: TASK-2025-0037 (follow-up)

---

## Context

TASK-2025-0037 investigation showed that files >500 lines exceed OpenAI rate limits (30k TPM for Tier 1). Rather than requiring tier upgrades, provide tooling to help users split large task specifications into manageable chunks.

## Objective

Create a utility to help users split large task specification files into multiple smaller files that can be evaluated independently.

## Requirements

### Core Functionality

**Command**: `adversarial split <task_file>`

**Behavior**:
1. Analyze task file structure (detect markdown sections)
2. Suggest natural split points (e.g., by section, by phase)
3. Generate multiple smaller files
4. Maintain cross-references between files
5. Preserve file numbering/naming conventions

### Example Usage

```bash
$ adversarial split delegation/tasks/active/TASK-2025-026-aaf-export.md

📄 Analyzing task file...
   Lines: 1,065
   Estimated tokens: ~42,000

⚠️  File exceeds recommended limit (500 lines, ~20k tokens)

💡 Suggested splits:

Option 1: Split by major sections (3 files)
  - TASK-2025-026-part1-overview.md (350 lines)
  - TASK-2025-026-part2-implementation.md (450 lines)
  - TASK-2025-026-part3-testing.md (265 lines)

Option 2: Split by implementation phases (4 files)
  - TASK-2025-026-part1-design.md (280 lines)
  - TASK-2025-026-part2-core-logic.md (320 lines)
  - TASK-2025-026-part3-integration.md (240 lines)
  - TASK-2025-026-part4-docs-tests.md (225 lines)

Select split strategy [1/2] or (c)ancel: 1

✅ Created 3 files:
   delegation/tasks/active/TASK-2025-026-part1-overview.md (350 lines)
   delegation/tasks/active/TASK-2025-026-part2-implementation.md (450 lines)
   delegation/tasks/active/TASK-2025-026-part3-testing.md (265 lines)

📋 Next steps:
   1. Review each part for completeness
   2. Evaluate each part independently:
      adversarial evaluate delegation/tasks/active/TASK-2025-026-part1-overview.md
      adversarial evaluate delegation/tasks/active/TASK-2025-026-part2-implementation.md
      adversarial evaluate delegation/tasks/active/TASK-2025-026-part3-testing.md
   3. Address feedback in each part
   4. Proceed with implementation using all parts
```

### Split Strategies

1. **By Sections** (default):
   - Parse markdown headings
   - Group related sections
   - Aim for ~400-500 lines per file

2. **By Phases**:
   - Split by implementation phases
   - Detect keywords: "Phase 1", "Phase 2", etc.
   - Each phase becomes a file

3. **Manual Split Points**:
   - User specifies line numbers: `--split-at 300,600,900`
   - Utility creates files at those boundaries

### Features

- **Validation**: Ensure splits don't break markdown structure
- **Cross-references**: Add links between split files
- **Metadata**: Add header to each file indicating it's part of a set
- **Naming**: Intelligent naming (part1, part2, etc.)
- **Dry-run**: `--dry-run` flag to preview splits without creating files

## Implementation Plan

### Phase 1: Core Splitting Logic (2 hours)

1. **File Analysis**:
   ```python
   def analyze_task_file(file_path: str) -> dict:
       """Analyze file structure and suggest split points."""
       # Parse markdown headings
       # Estimate tokens per section
       # Identify natural boundaries
   ```

2. **Split Strategies**:
   ```python
   def split_by_sections(content: str, max_lines: int = 500) -> list[dict]:
       """Split file by markdown sections."""

   def split_by_phases(content: str) -> list[dict]:
       """Split file by implementation phases."""

   def split_at_lines(content: str, line_numbers: list[int]) -> list[dict]:
       """Split at specified line numbers."""
   ```

3. **File Generation**:
   ```python
   def generate_split_files(
       original_file: str,
       splits: list[dict],
       output_dir: str
   ) -> list[str]:
       """Generate split files with metadata and cross-references."""
   ```

### Phase 2: CLI Integration (1 hour)

1. Add `split` command to `adversarial_workflow/cli.py`
2. Implement interactive split strategy selection
3. Add validation and error handling

### Phase 3: Documentation & Testing (1 hour)

1. Update README.md with `adversarial split` usage
2. Add examples to EXAMPLES.md
3. Manual testing with large files
4. Update troubleshooting guide

## Deliverables

1. **Code**:
   - `adversarial_workflow/utils/file_splitter.py` (splitting logic)
   - `adversarial_workflow/cli.py` (add `split` command)

2. **Documentation**:
   - README.md: Add `adversarial split` to commands section
   - EXAMPLES.md: Add example of splitting large files
   - TROUBLESHOOTING.md: Add "File too large" solution

3. **Tests** (optional):
   - Unit tests for splitting logic
   - Integration test with sample large file

## Success Criteria

- ✅ `adversarial split` command implemented
- ✅ Supports section-based splitting (default)
- ✅ Supports phase-based splitting
- ✅ Generates properly formatted split files
- ✅ Adds metadata and cross-references
- ✅ Interactive user experience
- ✅ Documented in README and EXAMPLES
- ✅ Tested with 1000+ line files

## User Experience Improvements

1. **Automatic detection**: Run pre-flight check, suggest splitting automatically
2. **Merge utility**: `adversarial merge <part1> <part2>...` to recombine
3. **Evaluation workflow**: Automatically evaluate all parts in sequence
4. **Summary report**: Combine evaluation results from all parts

## Nice-to-Have Enhancements

- Smart section grouping (keep related sections together)
- Preserve code blocks across splits (don't break in middle)
- Generate index file linking to all parts
- Support for splitting test files, not just task specs

---

**Status**: BACKLOG (medium priority)
**Dependencies**: None (can implement independently)
**Assigned**: Unassigned
**Value**: HIGH (helps users work within rate limits without upgrading tier)
