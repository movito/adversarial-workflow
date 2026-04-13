"""
Tests for the evaluate command functionality.

Tests the evaluate function which runs Phase 1: Plan evaluation using LiteLLM.
This includes error handling, file validation, and output parsing.
"""

from unittest.mock import patch

from adversarial_workflow.cli import (
    evaluate,
    validate,
    validate_evaluation_output,
    verify_token_count,
)


class TestEvaluate:
    """Test the evaluate command with various scenarios."""

    def test_evaluate_nonexistent_file(self, capsys):
        """Test evaluate with nonexistent task file returns error."""
        result = evaluate("nonexistent_task.md")

        assert result == 1
        captured = capsys.readouterr()
        assert "ERROR: Task file not found" in captured.out

    @patch("adversarial_workflow.cli.load_config")
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

    @patch("adversarial_workflow.cli.load_config")
    def test_evaluate_builtin_not_found(self, mock_load_config, tmp_path, capsys):
        """Test evaluate when built-in evaluator is missing."""
        task_file = tmp_path / "test_task.md"
        task_file.write_text("# Test task")

        mock_load_config.return_value = {"log_directory": ".adversarial/logs/"}

        with patch("adversarial_workflow.evaluators.builtins.BUILTIN_EVALUATORS", {}):
            result = evaluate(str(task_file))

        assert result == 1
        captured = capsys.readouterr()
        assert "evaluator not found" in captured.out

    @patch("adversarial_workflow.cli.load_config")
    def test_evaluate_successful_approved(
        self,
        mock_load_config,
        tmp_path,
        capsys,
    ):
        """Test successful evaluate — trusts run_evaluator exit code 0."""
        task_file = tmp_path / "test_task.md"
        task_file.write_text("# Test task")

        mock_load_config.return_value = {"log_directory": ".adversarial/logs/"}

        with patch("adversarial_workflow.evaluators.runner.run_evaluator", return_value=0):
            result = evaluate(str(task_file))

        assert result == 0
        captured = capsys.readouterr()
        assert "approved" in captured.out.lower()

    @patch("adversarial_workflow.cli.load_config")
    def test_evaluate_successful_does_not_call_validate_evaluation_output(
        self,
        mock_load_config,
        tmp_path,
    ):
        """Test evaluate() does NOT call validate_evaluation_output."""
        task_file = tmp_path / "test_task.md"
        task_file.write_text("# Test task")

        mock_load_config.return_value = {"log_directory": ".adversarial/logs/"}

        with (
            patch("adversarial_workflow.evaluators.runner.run_evaluator", return_value=0),
            patch("adversarial_workflow.cli.validate_evaluation_output") as mock_validate,
        ):
            result = evaluate(str(task_file))

        assert result == 0
        mock_validate.assert_not_called()

    @patch("adversarial_workflow.cli.load_config")
    def test_evaluate_needs_revision(
        self,
        mock_load_config,
        tmp_path,
        capsys,
    ):
        """Test evaluate returns non-zero when run_evaluator signals revision needed.

        run_evaluator returns 1 for NEEDS_REVISION verdicts, so evaluate()
        returns early.
        """
        task_file = tmp_path / "test_task.md"
        task_file.write_text("# Test task")

        mock_load_config.return_value = {"log_directory": ".adversarial/logs/"}

        with patch("adversarial_workflow.evaluators.runner.run_evaluator", return_value=1):
            result = evaluate(str(task_file))

        assert result == 1

    @patch("adversarial_workflow.cli.load_config")
    def test_evaluate_run_evaluator_failure(self, mock_load_config, tmp_path, capsys):
        """Test evaluate handles run_evaluator failure (e.g., rate limit, timeout)."""
        task_file = tmp_path / "test_task.md"
        task_file.write_text("# Test task")

        mock_load_config.return_value = {"log_directory": ".adversarial/logs/"}

        with patch("adversarial_workflow.evaluators.runner.run_evaluator", return_value=1):
            result = evaluate(str(task_file))

        assert result == 1

    def test_evaluate_delegates_to_run_evaluator(self, tmp_path, capsys):
        """Test evaluate delegates to run_evaluator and trusts its exit code."""
        task_file = tmp_path / "test_task.md"
        task_file.write_text("# Test task")

        with (
            patch(
                "adversarial_workflow.cli.load_config",
                return_value={"log_directory": ".adversarial/logs/"},
            ),
            patch(
                "adversarial_workflow.evaluators.runner.run_evaluator",
                return_value=0,
            ),
        ):
            result = evaluate(str(task_file))

        assert result == 0


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

    @patch("adversarial_workflow.cli.estimate_file_tokens")
    @patch("adversarial_workflow.cli.extract_token_count_from_log")
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

    @patch("adversarial_workflow.cli.estimate_file_tokens")
    @patch("adversarial_workflow.cli.extract_token_count_from_log")
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


class TestValidateCommand:
    """Test the validate CLI command (Phase 4: Test validation)."""

    @patch("adversarial_workflow.cli.load_config")
    def test_validate_empty_string_returns_error(self, mock_load_config, capsys):
        """Test validate('') returns 1 with error message, not ValueError."""
        mock_load_config.return_value = {"test_command": "pytest"}

        result = validate("")

        assert result == 1
        captured = capsys.readouterr()
        assert "Test command is empty" in captured.out

    @patch("adversarial_workflow.cli.load_config")
    def test_validate_whitespace_only_returns_error(self, mock_load_config, capsys):
        """Test validate('  ') returns 1 with error message, not ValueError."""
        mock_load_config.return_value = {"test_command": "pytest"}

        result = validate("  ")

        assert result == 1
        captured = capsys.readouterr()
        assert "Test command is empty" in captured.out

    @patch("adversarial_workflow.cli.load_config")
    def test_validate_none_uses_config_default(self, mock_load_config, capsys):
        """Test validate(None) falls back to config default."""
        mock_load_config.return_value = {"test_command": "echo hello"}

        # subprocess.run will execute "echo hello" which should succeed
        result = validate(None)

        assert result == 0

    @patch("adversarial_workflow.cli.load_config")
    def test_validate_config_not_initialized(self, mock_load_config, capsys):
        """Test validate handles missing config."""
        mock_load_config.side_effect = FileNotFoundError("Config not found")

        result = validate("pytest")

        assert result == 1
        captured = capsys.readouterr()
        assert "Not initialized" in captured.out


class TestEvaluateIntegration:
    """Integration tests for evaluate command with fixtures."""

    def test_evaluate_with_sample_task(self, sample_task_file, tmp_path):
        """Test evaluate with sample task file from fixture."""
        with (
            patch(
                "adversarial_workflow.cli.load_config",
                return_value={"log_directory": str(tmp_path) + "/"},
            ),
            patch(
                "adversarial_workflow.evaluators.runner.run_evaluator",
                return_value=0,
            ),
        ):
            result = evaluate(str(sample_task_file))
            assert isinstance(result, int)
            assert result == 0
