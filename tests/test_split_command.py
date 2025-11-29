"""Tests for the split CLI command integration."""

import tempfile
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from adversarial_workflow.cli import split


class TestSplitCommand:
    """Test the CLI split command functionality."""
    
    def test_split_nonexistent_file(self):
        """split command should return 1 for nonexistent files."""
        result = split("nonexistent.md")
        assert result == 1
    
    def test_split_small_file_no_splitting_needed(self):
        """Small files should not need splitting."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Small File\n\nJust a few lines.")
            temp_path = f.name
        
        try:
            result = split(temp_path)
            assert result == 0
        finally:
            os.unlink(temp_path)
    
    @patch('adversarial_workflow.cli.prompt_user')
    def test_split_large_file_user_cancels(self, mock_prompt):
        """User cancelling split should not create files."""
        mock_prompt.return_value = "n"
        
        # Create a large file
        content = "# Large File\n\n" + "Content line.\n" * 600
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = split(temp_path)
            assert result == 0
            
            # Should not create splits directory
            splits_dir = os.path.join(os.path.dirname(temp_path), "splits")
            assert not os.path.exists(splits_dir)
        finally:
            os.unlink(temp_path)
    
    @patch('adversarial_workflow.cli.prompt_user')
    def test_split_large_file_user_accepts(self, mock_prompt):
        """User accepting split should create files."""
        mock_prompt.return_value = "y"
        
        # Create a large file with sections
        content = """# Large File

## Section 1
Content for section 1.

""" + "Line of content.\n" * 600

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = split(temp_path)
            assert result == 0
            
            # Should create splits directory with files
            splits_dir = os.path.join(os.path.dirname(temp_path), "splits")
            assert os.path.exists(splits_dir)
            
            split_files = os.listdir(splits_dir)
            assert len(split_files) > 1  # Should create multiple files
            
            # Clean up splits
            import shutil
            shutil.rmtree(splits_dir)
            
        finally:
            os.unlink(temp_path)
    
    def test_split_invalid_strategy(self):
        """Invalid split strategy should return error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# File\n\n" + "Content.\n" * 600)
            temp_path = f.name
        
        try:
            result = split(temp_path, strategy="invalid")
            assert result == 1
        finally:
            os.unlink(temp_path)
    
    def test_split_dry_run_no_files_created(self):
        """Dry run mode should not create any files."""
        content = "# Large File\n\n" + "Content line.\n" * 600
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = split(temp_path, dry_run=True)
            assert result == 0
            
            # Should not create splits directory
            splits_dir = os.path.join(os.path.dirname(temp_path), "splits")
            assert not os.path.exists(splits_dir)
        finally:
            os.unlink(temp_path)
    
    def test_split_phases_strategy(self):
        """Phases strategy should work correctly."""
        content = """# Project Plan

Overview content.

## Phase 1: Analysis
Phase 1 content.

## Phase 2: Design
Phase 2 content.
""" + "Extra content.\n" * 600

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = split(temp_path, strategy="phases", dry_run=True)
            assert result == 0
        finally:
            os.unlink(temp_path)