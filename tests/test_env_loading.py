"""
Tests for .env file loading functionality.

These tests verify:
1. ADV-0024: Custom evaluators can access API keys from .env file
2. ADV-0025: Built-in evaluator conflicts don't produce warnings
"""

import os
import subprocess
import sys

import pytest


class TestCustomEvaluatorEnvLoading:
    """Tests for custom evaluator .env loading (ADV-0024)."""

    def test_custom_evaluator_sees_env_variables(self, tmp_path):
        """Custom evaluators can access API keys from .env file."""
        # Create .env with custom key
        (tmp_path / ".env").write_text("TEST_CUSTOM_KEY=test-secret-value\n")

        # Create custom evaluator config
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "test-env.yml").write_text("""name: test-env
description: Test .env loading
model: gpt-4o-mini
api_key_env: TEST_CUSTOM_KEY
prompt: Test prompt
output_suffix: TEST-ENV
""")

        # Create minimal project config
        adv_dir = tmp_path / ".adversarial"
        (adv_dir / "config.yml").write_text("evaluator_model: gpt-4o\nlog_directory: .adversarial/logs/\n")

        # Remove key from current environment
        env = {k: v for k, v in os.environ.items() if k != "TEST_CUSTOM_KEY"}
        env["PATH"] = os.environ.get("PATH", "")

        # List evaluators - should find test-env without error
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "list-evaluators"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
            env=env,
        )

        assert result.returncode == 0
        assert "test-env" in result.stdout, f"Expected test-env evaluator. Got: {result.stdout}"


class TestEvaluatorConflictWarning:
    """Tests for evaluator naming conflict warnings (ADV-0025)."""

    def test_no_warning_for_builtin_review_conflict(self, tmp_path):
        """Built-in 'review' evaluator should not trigger warning."""
        # Create minimal setup
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir()
        (adv_dir / "config.yml").write_text("evaluator_model: gpt-4o\n")

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "check"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        # Should NOT contain the conflict warning
        combined = result.stdout + result.stderr
        assert "conflicts with CLI command" not in combined, (
            f"Unexpected conflict warning in output: {combined}"
        )

    def test_warning_for_user_defined_conflict(self, tmp_path):
        """User-defined evaluator conflicting with CLI command should warn."""
        # Create custom evaluator that conflicts with 'check' command
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "check.yml").write_text("""name: check
description: Conflicts with CLI check command
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Test
output_suffix: TEST
""")

        adv_dir = tmp_path / ".adversarial"
        (adv_dir / "config.yml").write_text("evaluator_model: gpt-4o\n")

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "list-evaluators"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        # Should contain warning for user-defined conflict
        combined = result.stdout + result.stderr
        assert "check" in combined.lower() and "conflict" in combined.lower(), (
            f"Expected conflict warning for user-defined 'check' evaluator. Got: {combined}"
        )


class TestCheckEnvCount:
    """Tests for check() .env variable count (ADV-0022).
    
    The check() command should report accurate variable counts from .env files,
    even when main() has already loaded the environment variables.
    """

    def test_check_reports_correct_env_count(self, tmp_path):
        """check() reports correct count when .env has multiple variables."""
        # Create .env with 3 variables
        (tmp_path / ".env").write_text("KEY1=value1\nKEY2=value2\nKEY3=value3\n")

        # Create minimal project config
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir()
        (adv_dir / "config.yml").write_text("evaluator_model: gpt-4o\n")

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "check"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        # Should report 3 variables
        combined = result.stdout + result.stderr
        assert "3 variables" in combined, (
            f"Expected '.env file found and loaded (3 variables)'. Got: {combined}"
        )

    def test_check_handles_empty_env_file(self, tmp_path):
        """check() reports 0 variables for empty .env file."""
        # Create empty .env
        (tmp_path / ".env").write_text("")

        # Create minimal project config
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir()
        (adv_dir / "config.yml").write_text("evaluator_model: gpt-4o\n")

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "check"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        # Should report 0 variables
        combined = result.stdout + result.stderr
        assert "0 variables" in combined, (
            f"Expected '.env file found and loaded (0 variables)'. Got: {combined}"
        )

    def test_check_handles_comments_in_env(self, tmp_path):
        """check() only counts actual variables, not comments."""
        # Create .env with comments and 2 actual variables
        (tmp_path / ".env").write_text(
            "# This is a comment\n"
            "KEY1=value1\n"
            "# Another comment\n"
            "KEY2=value2\n"
            "\n"  # Empty line
        )

        # Create minimal project config
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir()
        (adv_dir / "config.yml").write_text("evaluator_model: gpt-4o\n")

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "check"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        # Should report 2 variables (not counting comments)
        combined = result.stdout + result.stderr
        assert "2 variables" in combined, (
            f"Expected '.env file found and loaded (2 variables)'. Got: {combined}"
        )

    def test_check_handles_unusual_env_entries(self, tmp_path):
        """check() handles various .env formats correctly."""
        # Create .env with unusual but valid entries
        (tmp_path / ".env").write_text(
            "SIMPLE=value\n"
            "EMPTY_VALUE=\n"  # Empty string value - counts as a variable
            "QUOTED='quoted value'\n"
            "WITH_SPACES=value with spaces\n"
        )

        # Create minimal project config
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir()
        (adv_dir / "config.yml").write_text("evaluator_model: gpt-4o\n")

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "check"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        # Should report 4 variables (EMPTY_VALUE= has empty string value, still counts)
        combined = result.stdout + result.stderr
        assert "4 variables" in combined, (
            f"Expected '.env file found and loaded (4 variables)'. Got: {combined}"
        )
