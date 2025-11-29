"""
Tests for the evaluate command functionality.

Tests the evaluate function which runs Phase 1: Plan evaluation using aider.
This includes error handling, file validation, subprocess management, and output parsing.
"""

import os
import platform
import pytest
import subprocess
from pathlib import Path
from unittest.mock import patch, Mock, mock_open

from adversarial_workflow.cli import evaluate, validate_evaluation_output, verify_token_count


class TestEvaluate:
    """Test the evaluate command with various scenarios."""

    def test_evaluate_nonexistent_file(self, capsys):
        """Test evaluate with nonexistent task file returns error."""
        result = evaluate("nonexistent_task.md")
        
        assert result == 1
        captured = capsys.readouterr()
        assert "ERROR: Task file not found" in captured.out

    @patch('adversarial_workflow.cli.load_config')
    def test_evaluate_config_load_error(self, mock_load_config, tmp_path, capsys):
        """Test evaluate handles config loading errors."""
        # Create a test file
        task_file = tmp_path / "test_task.md"
        task_file.write_text("# Test task")
        
        # Mock config loading to raise FileNotFoundError
        mock_load_config.side_effect = FileNotFoundError("Config not found")
        
        result = evaluate(str(task_file))
        
        assert result == 1
        captured = capsys.readouterr()
        assert "Not initialized" in captured.out

    @patch('shutil.which')
    @patch('adversarial_workflow.cli.load_config')
    def test_evaluate_aider_not_found(self, mock_load_config, mock_which, tmp_path, capsys):
        """Test evaluate when aider is not available."""
        # Create a test file
        task_file = tmp_path / "test_task.md"
        task_file.write_text("# Test task")
        
        # Mock aider not being found
        mock_which.return_value = None
        mock_load_config.return_value = {"log_directory": ".adversarial/logs/"}
        
        result = evaluate(str(task_file))
        
        assert result == 1
        captured = capsys.readouterr()
        assert "Aider not found" in captured.out

    @patch('shutil.which')
    @patch('adversarial_workflow.cli.load_config')
    @patch('os.path.exists')
    def test_evaluate_missing_script(self, mock_exists, mock_load_config, mock_which, tmp_path, capsys):
        """Test evaluate when evaluation script is missing."""
        # Create a test file
        task_file = tmp_path / "test_task.md"
        task_file.write_text("# Test task")
        
        # Mock dependencies
        mock_which.return_value = "/usr/bin/aider"
        mock_load_config.return_value = {"log_directory": ".adversarial/logs/"}
        
        # Mock script file not existing
        def mock_exists_side_effect(path):
            if path.endswith("evaluate_plan.sh"):
                return False
            return True
            
        mock_exists.side_effect = mock_exists_side_effect
        
        result = evaluate(str(task_file))
        
        assert result == 1
        captured = capsys.readouterr()
        assert "Script not found" in captured.out

    @patch('shutil.which')
    @patch('adversarial_workflow.cli.load_config') 
    @patch('os.path.exists')
    @patch('subprocess.run')
    @patch('adversarial_workflow.cli.validate_evaluation_output')
    @patch('adversarial_workflow.cli.verify_token_count')
    def test_evaluate_successful_approved(self, mock_verify, mock_validate, mock_run, mock_exists, 
                                        mock_load_config, mock_which, tmp_path, capsys):
        """Test successful evaluate with APPROVED verdict."""
        # Create a test file
        task_file = tmp_path / "test_task.md"
        task_file.write_text("# Test task")
        
        # Mock dependencies
        mock_which.return_value = "/usr/bin/aider"
        mock_load_config.return_value = {"log_directory": ".adversarial/logs/"}
        mock_exists.return_value = True
        
        # Mock successful subprocess run
        mock_run.return_value = Mock(returncode=0, stdout="Success", stderr="")
        
        # Mock successful validation
        mock_validate.return_value = (True, "APPROVED", "Plan approved")
        
        result = evaluate(str(task_file))
        
        assert result == 0
        captured = capsys.readouterr()
        assert "APPROVED" in captured.out

    @patch('shutil.which')
    @patch('adversarial_workflow.cli.load_config')
    @patch('os.path.exists') 
    @patch('subprocess.run')
    @patch('adversarial_workflow.cli.validate_evaluation_output')
    @patch('adversarial_workflow.cli.verify_token_count')
    def test_evaluate_needs_revision(self, mock_verify, mock_validate, mock_run, mock_exists,
                                   mock_load_config, mock_which, tmp_path, capsys):
        """Test evaluate with NEEDS_REVISION verdict."""
        # Create a test file
        task_file = tmp_path / "test_task.md" 
        task_file.write_text("# Test task")
        
        # Mock dependencies
        mock_which.return_value = "/usr/bin/aider"
        mock_load_config.return_value = {"log_directory": ".adversarial/logs/"}
        mock_exists.return_value = True
        
        # Mock successful subprocess run
        mock_run.return_value = Mock(returncode=0, stdout="Success", stderr="")
        
        # Mock needs revision validation
        mock_validate.return_value = (True, "NEEDS_REVISION", "Plan needs work")
        
        result = evaluate(str(task_file))
        
        assert result == 1
        captured = capsys.readouterr()
        assert "NEEDS_REVISION" in captured.out

    @patch('shutil.which')
    @patch('adversarial_workflow.cli.load_config')
    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_evaluate_rate_limit_error(self, mock_run, mock_exists, mock_load_config, 
                                     mock_which, tmp_path, capsys):
        """Test evaluate handles rate limit errors."""
        # Create a test file
        task_file = tmp_path / "test_task.md"
        task_file.write_text("# Test task")
        
        # Mock dependencies
        mock_which.return_value = "/usr/bin/aider"
        mock_load_config.return_value = {"log_directory": ".adversarial/logs/"}
        mock_exists.return_value = True
        
        # Mock rate limit error in subprocess output
        mock_run.return_value = Mock(
            returncode=1, 
            stdout="RateLimitError: tokens per min (TPM) limit exceeded",
            stderr=""
        )
        
        result = evaluate(str(task_file))
        
        assert result == 1
        captured = capsys.readouterr()
        assert "rate limit exceeded" in captured.out

    @patch('shutil.which')
    @patch('adversarial_workflow.cli.load_config')
    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_evaluate_timeout(self, mock_run, mock_exists, mock_load_config, 
                            mock_which, tmp_path, capsys):
        """Test evaluate handles subprocess timeout."""
        # Create a test file
        task_file = tmp_path / "test_task.md"
        task_file.write_text("# Test task")
        
        # Mock dependencies
        mock_which.return_value = "/usr/bin/aider"
        mock_load_config.return_value = {"log_directory": ".adversarial/logs/"}
        mock_exists.return_value = True
        
        # Mock timeout exception
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 180)
        
        result = evaluate(str(task_file))
        
        assert result == 1
        captured = capsys.readouterr()
        assert "timed out" in captured.out

    @patch('platform.system')
    @patch('shutil.which')
    @patch('adversarial_workflow.cli.load_config')
    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_evaluate_windows_error(self, mock_run, mock_exists, mock_load_config, 
                                  mock_which, mock_system, tmp_path, capsys):
        """Test evaluate handles Windows platform issues."""
        # Create a test file
        task_file = tmp_path / "test_task.md"
        task_file.write_text("# Test task")
        
        # Mock dependencies
        mock_which.return_value = "/usr/bin/aider"
        mock_load_config.return_value = {"log_directory": ".adversarial/logs/"}
        mock_exists.return_value = True
        mock_system.return_value = "Windows"
        
        # Mock FileNotFoundError (bash script not found on Windows)
        mock_run.side_effect = FileNotFoundError("Script not found")
        
        result = evaluate(str(task_file))
        
        assert result == 1
        captured = capsys.readouterr()
        assert "Windows" in captured.out and "WSL" in captured.out

    def test_evaluate_large_file_warning(self, mock_subprocess, tmp_path, capsys):
        """Test evaluate warns about large files."""
        # Create a large test file (>500 lines)
        task_file = tmp_path / "large_task.md"
        large_content = "# Test task\n" + "Line content\n" * 600
        task_file.write_text(large_content)
        
        with patch('shutil.which', return_value="/usr/bin/aider"), \
             patch('adversarial_workflow.cli.load_config', return_value={"log_directory": ".adversarial/logs/"}), \
             patch('os.path.exists', return_value=True), \
             patch('adversarial_workflow.cli.validate_evaluation_output', return_value=(True, "APPROVED", "OK")), \
             patch('adversarial_workflow.cli.verify_token_count'):
            
            result = evaluate(str(task_file))
        
        captured = capsys.readouterr()
        assert "Large file detected" in captured.out

    def test_evaluate_very_large_file_prompt(self, tmp_path):
        """Test evaluate prompts for confirmation on very large files."""
        # Create a very large test file (>700 lines)
        task_file = tmp_path / "very_large_task.md"
        very_large_content = "# Test task\n" + "Line content\n" * 800
        task_file.write_text(very_large_content)
        
        with patch('shutil.which', return_value="/usr/bin/aider"), \
             patch('adversarial_workflow.cli.load_config', return_value={"log_directory": ".adversarial/logs/"}), \
             patch('os.path.exists', return_value=True), \
             patch('builtins.input', return_value='n'):  # User says no
            
            result = evaluate(str(task_file))
            assert result == 0  # Cancelled, not error


class TestValidateEvaluationOutput:
    """Test the validate_evaluation_output helper function."""

    def test_validate_evaluation_output_missing_file(self):
        """Test validation with missing log file."""
        is_valid, verdict, message = validate_evaluation_output("nonexistent.md")
        
        assert not is_valid
        assert "not found" in message.lower()

    def test_validate_evaluation_output_approved(self, tmp_path):
        """Test validation with APPROVED verdict."""
        log_file = tmp_path / "test-evaluation.md"
        log_content = """# PLAN EVALUATION

## Evaluation Summary

The plan is well structured and feasible. It includes proper requirements analysis,
clear implementation steps, and appropriate acceptance criteria. The architecture 
choices are sound and the timeline is realistic. All dependencies are properly 
identified and the testing strategy is comprehensive. The documentation is clear
and follows project standards. Resource allocation seems appropriate for the scope.

## Technical Analysis

The technical approach leverages existing patterns and doesn't introduce unnecessary
complexity. The proposed abstractions are clean and maintainable. Performance 
considerations have been addressed appropriately. Security implications have been
reviewed and addressed. The error handling strategy is robust and user-friendly.

## Verdict: APPROVED

The plan looks good and can proceed to implementation phase.

## Tokens: 1500
Input tokens: 1000  
Output tokens: 500
Total cost: $0.15
"""
        log_file.write_text(log_content)
        
        is_valid, verdict, message = validate_evaluation_output(str(log_file))
        
        assert is_valid
        assert verdict == "APPROVED"

    def test_validate_evaluation_output_rejected(self, tmp_path):
        """Test validation with REJECTED verdict."""
        log_file = tmp_path / "test-evaluation.md"
        log_content = """# PLAN EVALUATION

## Evaluation Summary

The plan has fundamental issues that need to be addressed before implementation
can proceed. The requirements analysis is incomplete, lacking clarity on key 
functional requirements. The proposed architecture introduces unnecessary complexity
without clear benefits. The implementation timeline is unrealistic given the scope.
Dependencies are not properly identified or analyzed. Testing strategy is insufficient
for the complexity of the proposed solution. Documentation standards are not met.

## Issues Identified

1. Incomplete requirements - missing key functional specifications
2. Over-engineered architecture - unnecessary abstractions
3. Unrealistic timeline - insufficient time allocation 
4. Missing dependencies - external service requirements not addressed
5. Inadequate testing - no integration test strategy
6. Documentation gaps - missing technical specifications

## Verdict: REJECTED

Major issues found in the implementation approach that require significant revision.

## Tokens: 1200
Input tokens: 800
Output tokens: 400
Total cost: $0.12
"""
        log_file.write_text(log_content)
        
        is_valid, verdict, message = validate_evaluation_output(str(log_file))
        
        assert is_valid
        assert verdict == "REJECTED"

    def test_validate_evaluation_output_empty_file(self, tmp_path):
        """Test validation with empty log file."""
        log_file = tmp_path / "empty-evaluation.md"
        log_file.write_text("")
        
        is_valid, verdict, message = validate_evaluation_output(str(log_file))
        
        assert not is_valid
        assert "too small" in message.lower()


class TestVerifyTokenCount:
    """Test the verify_token_count helper function."""

    @patch('adversarial_workflow.cli.estimate_file_tokens')
    @patch('adversarial_workflow.cli.extract_token_count_from_log')
    def test_verify_token_count_normal(self, mock_extract, mock_estimate, tmp_path, capsys):
        """Test normal token count verification."""
        task_file = tmp_path / "task.md"
        log_file = tmp_path / "log.md"
        task_file.write_text("# Task")
        log_file.write_text("# Log")
        
        # Mock reasonable token counts
        mock_estimate.return_value = 100
        mock_extract.return_value = 50
        
        # Should not raise or warn for normal counts
        verify_token_count(str(task_file), str(log_file))
        
        captured = capsys.readouterr()
        # Should not warn for reasonable token usage
        assert "suspiciously low" not in captured.out

    @patch('adversarial_workflow.cli.estimate_file_tokens')
    @patch('adversarial_workflow.cli.extract_token_count_from_log')
    def test_verify_token_count_low_warning(self, mock_extract, mock_estimate, tmp_path, capsys):
        """Test token count verification warns on suspiciously low usage."""
        task_file = tmp_path / "task.md"
        log_file = tmp_path / "log.md"
        task_file.write_text("# Task")
        log_file.write_text("# Log")
        
        # Mock high input but very low output tokens
        mock_estimate.return_value = 1000
        mock_extract.return_value = 5  # Suspiciously low
        
        verify_token_count(str(task_file), str(log_file))
        
        captured = capsys.readouterr()
        assert "lower than expected" in captured.out


class TestEvaluateIntegration:
    """Integration tests for evaluate command with fixtures."""

    def test_evaluate_with_sample_task(self, sample_task_file, mock_aider_command):
        """Test evaluate with sample task file from fixture."""
        with patch('shutil.which', return_value="/usr/bin/aider"), \
             patch('adversarial_workflow.cli.load_config', return_value={"log_directory": ".adversarial/logs/"}), \
             patch('os.path.exists', return_value=True), \
             patch('adversarial_workflow.cli.validate_evaluation_output', return_value=(True, "APPROVED", "OK")), \
             patch('adversarial_workflow.cli.verify_token_count'):
            
            result = evaluate(str(sample_task_file))
            assert isinstance(result, int)