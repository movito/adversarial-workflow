"""Tests for dynamic CLI command registration (ADV-0018).

These tests verify that evaluators (built-in and custom) are dynamically
registered as CLI subcommands, with proper alias support and static command
protection.
"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestBuiltinEvaluatorsInHelp:
    """Test that built-in evaluators appear in CLI help output."""

    def test_evaluate_command_in_help(self, tmp_path, monkeypatch):
        """Built-in 'evaluate' command appears in --help."""
        # Create minimal project structure
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        assert result.returncode == 0
        assert "evaluate" in result.stdout

    def test_proofread_command_in_help(self, tmp_path, monkeypatch):
        """Built-in 'proofread' command appears in --help."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        assert result.returncode == 0
        assert "proofread" in result.stdout

    def test_review_command_in_help(self, tmp_path, monkeypatch):
        """Built-in 'review' command appears in --help."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        assert result.returncode == 0
        assert "review" in result.stdout


class TestLocalEvaluatorDiscovery:
    """Test that local evaluators in .adversarial/evaluators/ appear in CLI."""

    def test_local_evaluator_in_help(self, tmp_path, monkeypatch):
        """Local evaluator appears in --help output."""
        # Setup: Create local evaluator
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "custom.yml").write_text("""
name: custom
description: Custom test evaluator
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: CUSTOM-TEST
""")

        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        assert "custom" in result.stdout, f"'custom' not found in help output:\n{result.stdout}"
        assert "Custom test evaluator" in result.stdout

    def test_multiple_local_evaluators_in_help(self, tmp_path, monkeypatch):
        """Multiple local evaluators appear in --help output."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)

        (eval_dir / "athena.yml").write_text("""
name: athena
description: Knowledge evaluation
model: gemini-2.5-pro
api_key_env: GOOGLE_API_KEY
prompt: Evaluate knowledge
output_suffix: KNOWLEDGE-EVAL
""")

        (eval_dir / "zeus.yml").write_text("""
name: zeus
description: Power evaluation
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Evaluate power
output_suffix: POWER-EVAL
""")

        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        assert "athena" in result.stdout
        assert "zeus" in result.stdout


class TestStaticCommandProtection:
    """Test that static commands cannot be overridden by evaluators."""

    def test_init_command_not_overridden(self, tmp_path, monkeypatch):
        """Static 'init' command cannot be overridden by evaluators."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        # Create evaluator named 'init' (should be skipped)
        (eval_dir / "init.yml").write_text("""
name: init
description: This should NOT override init
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Bad init
output_suffix: BAD-INIT
""")

        monkeypatch.chdir(tmp_path)

        # 'init --help' should still show the original init command
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "init", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        # Init help should have --path and --interactive options (not evaluator options)
        assert "--path" in result.stdout
        assert "--interactive" in result.stdout
        # Should NOT have 'file' positional arg (evaluators have 'file' arg)
        assert "BAD-INIT" not in result.stdout

    def test_check_command_not_overridden(self, tmp_path, monkeypatch):
        """Static 'check' command cannot be overridden by evaluators."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "check.yml").write_text("""
name: check
description: This should NOT override check
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Bad check
output_suffix: BAD-CHECK
""")

        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "check", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        # Check command should NOT have evaluator-specific options
        # Evaluators have --timeout and positional 'file' arg
        assert "--timeout" not in result.stdout
        assert "BAD-CHECK" not in result.stdout


class TestEvaluatorExecution:
    """Test evaluator command execution routing."""

    def test_evaluator_has_file_argument(self, tmp_path, monkeypatch):
        """Evaluator commands have a 'file' positional argument."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "myeval.yml").write_text("""
name: myeval
description: My evaluator
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Evaluate this
output_suffix: MY-EVAL
""")

        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "myeval", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        assert result.returncode == 0
        assert "file" in result.stdout.lower()

    def test_evaluator_has_timeout_flag(self, tmp_path, monkeypatch):
        """Evaluator commands have --timeout flag."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "myeval.yml").write_text("""
name: myeval
description: My evaluator
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Evaluate this
output_suffix: MY-EVAL
""")

        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "myeval", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        assert "--timeout" in result.stdout or "-t" in result.stdout


class TestAliasSupport:
    """Test evaluator alias support."""

    def test_alias_in_help(self, tmp_path, monkeypatch):
        """Evaluator aliases appear in help."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "knowledge.yml").write_text("""
name: knowledge
description: Knowledge evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Evaluate knowledge
output_suffix: KNOWLEDGE
aliases:
  - know
  - k
""")

        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        assert "knowledge" in result.stdout

    def test_alias_command_works(self, tmp_path, monkeypatch):
        """Alias command shows same help as main command."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "knowledge.yml").write_text("""
name: knowledge
description: Knowledge evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Evaluate knowledge
output_suffix: KNOWLEDGE
aliases:
  - know
""")

        monkeypatch.chdir(tmp_path)

        # Both 'knowledge --help' and 'know --help' should work
        result_main = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "knowledge", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        result_alias = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "know", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        assert result_main.returncode == 0
        assert result_alias.returncode == 0
        # Both should have 'file' argument
        assert "file" in result_main.stdout.lower()
        assert "file" in result_alias.stdout.lower()


class TestBackwardsCompatibility:
    """Test backwards compatibility with existing commands."""

    def test_evaluate_help_works(self, tmp_path, monkeypatch):
        """adversarial evaluate --help still works."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "evaluate", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        assert result.returncode == 0
        assert "file" in result.stdout.lower()

    def test_proofread_help_works(self, tmp_path, monkeypatch):
        """adversarial proofread --help still works."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "proofread", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        assert result.returncode == 0

    def test_review_help_works(self, tmp_path, monkeypatch):
        """adversarial review --help still works."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "review", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        assert result.returncode == 0

    def test_init_command_still_works(self, tmp_path, monkeypatch):
        """Static init command still works."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "init", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        assert result.returncode == 0
        assert "--interactive" in result.stdout or "-i" in result.stdout


class TestGracefulDegradation:
    """Test graceful degradation on errors."""

    def test_help_works_without_local_evaluators_dir(self, tmp_path, monkeypatch):
        """CLI help works even without .adversarial/evaluators/ directory."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")
        # Note: NOT creating evaluators/ directory

        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        assert result.returncode == 0
        # Built-in evaluators should still be present
        assert "evaluate" in result.stdout

    def test_help_works_without_adversarial_dir(self, tmp_path, monkeypatch):
        """CLI help works even without .adversarial/ directory."""
        # Note: NOT creating .adversarial/ directory at all
        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        assert result.returncode == 0
        # Built-in evaluators should still be present
        assert "evaluate" in result.stdout


class TestEvaluatorConfigAttribute:
    """Test that evaluator commands get evaluator_config attribute."""

    def test_builtin_evaluate_has_file_arg(self, tmp_path, monkeypatch):
        """Built-in evaluate command should have file argument after dynamic registration."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "evaluate", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        assert result.returncode == 0
        # After dynamic registration, evaluate should have 'file' not 'task_file'
        assert "file" in result.stdout.lower()

    def test_builtin_evaluate_has_timeout(self, tmp_path, monkeypatch):
        """Built-in evaluate command should have --timeout flag after dynamic registration."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "evaluate", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        assert "--timeout" in result.stdout or "-t" in result.stdout
