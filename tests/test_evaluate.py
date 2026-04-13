"""
Tests for the evaluate command functionality.

Tests the evaluate function which runs Phase 1: Plan evaluation using LiteLLM.
This includes error handling, file validation, and output parsing.

Note: validate_evaluation_output tests are in test_utils_validation.py (canonical location).
The cli.py duplicate was removed in ADV-0067.
"""

from unittest.mock import patch

from adversarial_workflow.cli import (
    evaluate,
    validate,
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
    def test_evaluate_successful(
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
        assert "Evaluation complete!" in captured.out

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
