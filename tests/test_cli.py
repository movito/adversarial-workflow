"""
Tests for the adversarial CLI.

Comprehensive smoke tests for all CLI commands to ensure basic functionality
works correctly before refactoring the monolithic cli.py.
"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from adversarial_workflow.cli import check, health, load_config, main


class TestCLISmoke:
    """Basic smoke tests to verify CLI is functional."""

    def test_version_flag(self):
        """Test that --version returns version info."""
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "0.4.0" in result.stdout or "0.4.0" in result.stderr

    def test_help_flag(self):
        """Test that --help returns help text."""
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        help_text = result.stdout.lower()
        assert any(cmd in help_text for cmd in ["evaluate", "init", "check", "health"])

    def test_no_command_shows_help(self):
        """Test that no command shows help text."""
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        help_text = result.stdout.lower()
        assert "usage" in help_text or "help" in help_text

    def test_evaluate_without_file_shows_error(self):
        """Test that evaluate without a file shows an error."""
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "evaluate"],
            capture_output=True,
            text=True,
        )
        # Should fail because no file was provided
        assert result.returncode != 0

    def test_init_help(self):
        """Test that init command help works."""
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "init", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "workflow" in result.stdout.lower() or "init" in result.stdout.lower()

    def test_check_help(self):
        """Test that check command help works."""
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "check", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "validate" in result.stdout.lower() or "check" in result.stdout.lower()

    def test_health_help(self):
        """Test that health command help works."""
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "health", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "health" in result.stdout.lower()


class TestCLIDirectImport:
    """Test CLI functions by importing them directly."""

    def test_main_function_exists(self):
        """Test that main function can be imported."""
        assert callable(main)

    def test_load_config_function_exists(self):
        """Test that load_config function can be imported."""
        assert callable(load_config)

    def test_check_function_exists(self):
        """Test that check function can be imported."""
        assert callable(check)

    def test_health_function_exists(self):
        """Test that health function can be imported."""
        assert callable(health)

    @patch("sys.argv", ["adversarial", "--version"])
    @patch("sys.exit")
    def test_main_with_version_arg(self, mock_exit):
        """Test main function with version argument."""
        with patch("builtins.print") as mock_print:
            try:
                main()
            except SystemExit:
                pass
        # Should have called print or exit
        assert mock_exit.called or mock_print.called

    @patch("sys.argv", ["adversarial"])
    def test_main_with_no_args(self):
        """Test main function with no arguments shows help."""
        result = main()
        # Should return 0 (showing help is not an error)
        assert result == 0

    @patch("os.path.exists", return_value=False)
    def test_load_config_missing_file(self, mock_exists):
        """Test load_config with missing config file."""
        result = load_config("nonexistent.yaml")
        # Should return default configuration for missing file
        assert isinstance(result, dict)
        assert "evaluator_model" in result

    @patch("subprocess.run")
    def test_check_function_basic(self, mock_run):
        """Test check function basic execution."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        # Should not raise an exception
        result = check()
        # check() function should return an integer exit code
        assert isinstance(result, int)

    @patch("subprocess.run")
    def test_health_function_basic(self, mock_run):
        """Test health function basic execution."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        # Should not raise an exception
        result = health()
        # health() function should return an integer exit code
        assert isinstance(result, int)


class TestCLIErrorHandling:
    """Test CLI error handling scenarios."""

    def test_invalid_command(self):
        """Test that invalid command shows error."""
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "invalid_command"],
            capture_output=True,
            text=True,
        )
        # Should show help (return code 1) for invalid command
        assert result.returncode != 0 or "usage" in result.stdout.lower()

    def test_evaluate_with_nonexistent_file(self):
        """Test evaluate command with nonexistent file."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "adversarial_workflow.cli",
                "evaluate",
                "nonexistent.md",
            ],
            capture_output=True,
            text=True,
        )
        # Should fail with appropriate error
        assert result.returncode != 0

    def test_agent_without_subcommand(self):
        """Test agent command without subcommand shows error."""
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "agent"],
            capture_output=True,
            text=True,
        )
        # Should fail and show usage
        assert result.returncode != 0
