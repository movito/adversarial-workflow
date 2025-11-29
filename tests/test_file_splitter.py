"""Tests for file_splitter module following TDD approach.

These tests should fail initially (RED phase) then pass after implementation (GREEN phase).
"""
import pytest
import tempfile
import os
from pathlib import Path

from adversarial_workflow.utils.file_splitter import (
    analyze_task_file,
    split_by_sections,
    split_by_phases,
    split_at_lines,
    generate_split_files,
)


# Test fixtures
SAMPLE_MARKDOWN_WITH_SECTIONS = """# Main Title

## Introduction
This is the introduction section.
It spans multiple lines.

## Requirements
- Requirement 1
- Requirement 2
- Requirement 3

## Implementation Plan

### Phase 1
Step 1: Do something
Step 2: Do something else

### Phase 2  
Step 1: More work
Step 2: Final work

## Conclusion
End of document.
"""

SAMPLE_MARKDOWN_WITH_PHASES = """# Project Plan

Overview of the project.

## Phase 1: Analysis
Analyze requirements.
Research solutions.

## Phase 2: Design
Create architecture.
Design components.

## Phase 3: Implementation
Write code.
Test functionality.

## Phase 4: Deployment
Deploy to production.
Monitor performance.
"""

LARGE_MARKDOWN_600_LINES = "# Large File\n\n" + "Line content here.\n" * 598


class TestAnalyzeTaskFile:
    """Test file analysis functionality."""
    
    def test_analyze_task_file_returns_sections(self):
        """analyze_task_file() returns dict with sections and line counts."""
        # Create temporary file with sample content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(SAMPLE_MARKDOWN_WITH_SECTIONS)
            temp_path = f.name
        
        try:
            result = analyze_task_file(temp_path)
            
            # Should return dict with expected structure
            assert isinstance(result, dict)
            assert 'total_lines' in result
            assert 'sections' in result
            assert 'estimated_tokens' in result
            assert 'suggested_splits' in result
            
            # Should detect sections
            sections = result['sections']
            assert len(sections) >= 4  # Main Title, Introduction, Requirements, Implementation Plan, Conclusion
            
            # Should calculate line counts
            assert result['total_lines'] > 0
            assert result['estimated_tokens'] > 0
            
        finally:
            os.unlink(temp_path)
    
    def test_analyze_empty_file_raises_error(self):
        """Empty files raise appropriate error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="File is empty or too small"):
                analyze_task_file(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_analyze_nonexistent_file_raises_error(self):
        """Non-existent files raise appropriate error."""
        with pytest.raises(FileNotFoundError):
            analyze_task_file("/path/does/not/exist.md")


class TestSplitBySection:
    """Test section-based splitting functionality."""
    
    def test_split_by_sections_respects_max_lines(self):
        """split_by_sections() creates chunks under max_lines."""
        content = LARGE_MARKDOWN_600_LINES
        max_lines = 200
        
        splits = split_by_sections(content, max_lines=max_lines)
        
        # Should create multiple splits
        assert len(splits) > 1
        
        # Each split should respect max_lines (except last one might be smaller)
        for split in splits[:-1]:  # All but last
            assert split['line_count'] <= max_lines
            
        # All splits should have required metadata
        for split in splits:
            assert 'content' in split
            assert 'start_line' in split
            assert 'end_line' in split
            assert 'line_count' in split
            assert 'title' in split
    
    def test_split_by_sections_preserves_markdown_structure(self):
        """Splits don't break code blocks or lists."""
        content_with_code = """# Title

## Section 1
Some text here.

```python
def example():
    return "code block"
```

More text.

## Section 2
- List item 1
- List item 2

End of section.
"""
        splits = split_by_sections(content_with_code, max_lines=10)
        
        # Should create splits that preserve structure
        assert len(splits) >= 1
        
        # Check that code blocks are not broken across splits
        for split in splits:
            content = split['content']
            # If contains code block start, should contain end
            code_starts = content.count('```python')
            code_ends = content.count('```\n') + content.count('```')
            if code_starts > 0:
                assert code_ends >= code_starts
    
    def test_split_single_section_under_limit(self):
        """Files under limit return single split."""
        short_content = "# Title\n\nShort content."
        splits = split_by_sections(short_content, max_lines=500)
        
        assert len(splits) == 1
        assert splits[0]['line_count'] < 500


class TestSplitByPhases:
    """Test phase-based splitting functionality."""
    
    def test_split_by_phases_detects_phase_markers(self):
        """split_by_phases() splits on 'Phase N' patterns."""
        content = SAMPLE_MARKDOWN_WITH_PHASES
        
        splits = split_by_phases(content)
        
        # Should create multiple splits for each phase
        assert len(splits) >= 4  # Overview + 4 phases
        
        # Each split should have metadata
        for split in splits:
            assert 'content' in split
            assert 'phase_number' in split or split['title'] == 'Overview'
            assert 'title' in split
            assert 'line_count' in split
    
    def test_split_by_phases_no_phases_returns_single_split(self):
        """Content without phases returns single split."""
        content = "# Title\n\nNo phases here."
        splits = split_by_phases(content)
        
        assert len(splits) == 1
        assert splits[0]['title'] == 'Full Document'


class TestSplitAtLines:
    """Test manual line-based splitting functionality."""
    
    def test_split_at_lines_creates_expected_chunks(self):
        """split_at_lines() splits at specified line numbers."""
        content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6"
        line_numbers = [2, 4]  # Split after lines 2 and 4
        
        splits = split_at_lines(content, line_numbers)
        
        assert len(splits) == 3  # 3 chunks from 2 split points
        
        # First chunk: lines 1-2
        assert "Line 1" in splits[0]['content']
        assert "Line 2" in splits[0]['content']
        assert "Line 3" not in splits[0]['content']
        
        # Second chunk: lines 3-4
        assert "Line 3" in splits[1]['content']
        assert "Line 4" in splits[1]['content']
        assert "Line 2" not in splits[1]['content']
        assert "Line 5" not in splits[1]['content']
        
        # Third chunk: lines 5-6
        assert "Line 5" in splits[2]['content']
        assert "Line 6" in splits[2]['content']
    
    def test_split_at_lines_empty_list_returns_single_split(self):
        """Empty line numbers list returns original content."""
        content = "Line 1\nLine 2\nLine 3"
        splits = split_at_lines(content, [])
        
        assert len(splits) == 1
        assert splits[0]['content'].strip() == content.strip()


class TestGenerateSplitFiles:
    """Test file generation functionality."""
    
    def test_generate_split_files_creates_files(self):
        """generate_split_files() creates files with proper names and content."""
        original_file = "test-task.md"
        splits = [
            {
                'content': '# Part 1\n\nContent 1',
                'title': 'Part 1',
                'line_count': 3,
                'start_line': 1,
                'end_line': 3
            },
            {
                'content': '# Part 2\n\nContent 2',
                'title': 'Part 2', 
                'line_count': 3,
                'start_line': 4,
                'end_line': 6
            }
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            created_files = generate_split_files(original_file, splits, temp_dir)
            
            # Should create 2 files
            assert len(created_files) == 2
            
            # Files should exist
            for file_path in created_files:
                assert os.path.exists(file_path)
                
                # Files should contain metadata headers
                with open(file_path, 'r') as f:
                    content = f.read()
                    assert "<!-- Split from" in content
                    assert "Part" in content
    
    def test_generate_split_files_adds_metadata(self):
        """Generated files have part headers and cross-references."""
        original_file = "large-task.md"
        splits = [
            {
                'content': '# Introduction\n\nContent here',
                'title': 'Introduction',
                'line_count': 3,
                'start_line': 1,
                'end_line': 3
            }
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            created_files = generate_split_files(original_file, splits, temp_dir)
            
            # Check metadata content
            with open(created_files[0], 'r') as f:
                content = f.read()
                
                # Should have metadata header
                assert "<!-- Split from large-task.md -->" in content
                assert "Part 1 of 1" in content
                assert "Lines 1-3" in content