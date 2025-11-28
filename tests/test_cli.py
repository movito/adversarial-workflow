"""
Tests for the adversarial CLI.

This is the initial test file for TDD. Start with basic smoke tests
and expand as you refactor the monolithic cli.py.
"""

import subprocess
import sys


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
        assert "evaluate" in result.stdout.lower() or "usage" in result.stdout.lower()

    def test_evaluate_without_file_shows_error(self):
        """Test that evaluate without a file shows an error."""
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "evaluate"],
            capture_output=True,
            text=True,
        )
        # Should fail because no file was provided
        assert result.returncode != 0 or "error" in result.stderr.lower()
