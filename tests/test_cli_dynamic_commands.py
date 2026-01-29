"""Tests for dynamic CLI command registration (ADV-0018).

These tests verify that evaluators (built-in and custom) are dynamically
registered as CLI subcommands, with proper alias support and static command
protection.
"""

from pathlib import Path
from unittest.mock import patch

import pytest


class TestBuiltinEvaluatorsInHelp:
    """Test that built-in evaluators appear in CLI help output."""

    def test_evaluate_command_in_help(self, tmp_path, monkeypatch, run_cli):
        """Built-in 'evaluate' command appears in --help."""
        # Create minimal project structure
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = run_cli(["--help"], cwd=tmp_path)
        assert result.returncode == 0
        assert "evaluate" in result.stdout

    def test_proofread_command_in_help(self, tmp_path, monkeypatch, run_cli):
        """Built-in 'proofread' command appears in --help."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = run_cli(["--help"], cwd=tmp_path)
        assert result.returncode == 0
        assert "proofread" in result.stdout

    def test_review_command_in_help(self, tmp_path, monkeypatch, run_cli):
        """Built-in 'review' command appears in --help."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = run_cli(["--help"], cwd=tmp_path)
        assert result.returncode == 0
        assert "review" in result.stdout


class TestLocalEvaluatorDiscovery:
    """Test that local evaluators in .adversarial/evaluators/ appear in CLI."""

    def test_local_evaluator_in_help(self, tmp_path, monkeypatch, run_cli):
        """Local evaluator appears in --help output."""
        # Setup: Create local evaluator
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "custom.yml").write_text(
            """
name: custom
description: Custom test evaluator
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: CUSTOM-TEST
"""
        )

        monkeypatch.chdir(tmp_path)

        result = run_cli(["--help"], cwd=tmp_path)
        assert "custom" in result.stdout, f"'custom' not found in help output:\n{result.stdout}"
        assert "Custom test evaluator" in result.stdout

    def test_multiple_local_evaluators_in_help(self, tmp_path, monkeypatch, run_cli):
        """Multiple local evaluators appear in --help output."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)

        (eval_dir / "athena.yml").write_text(
            """
name: athena
description: Knowledge evaluation
model: gemini-2.5-pro
api_key_env: GOOGLE_API_KEY
prompt: Evaluate knowledge
output_suffix: KNOWLEDGE-EVAL
"""
        )

        (eval_dir / "zeus.yml").write_text(
            """
name: zeus
description: Power evaluation
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Evaluate power
output_suffix: POWER-EVAL
"""
        )

        monkeypatch.chdir(tmp_path)

        result = run_cli(["--help"], cwd=tmp_path)
        assert "athena" in result.stdout
        assert "zeus" in result.stdout


class TestStaticCommandProtection:
    """Test that static commands cannot be overridden by evaluators."""

    def test_init_command_not_overridden(self, tmp_path, monkeypatch, run_cli):
        """Static 'init' command cannot be overridden by evaluators."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        # Create evaluator named 'init' (should be skipped)
        (eval_dir / "init.yml").write_text(
            """
name: init
description: This should NOT override init
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Bad init
output_suffix: BAD-INIT
"""
        )

        monkeypatch.chdir(tmp_path)

        # 'init --help' should still show the original init command
        result = run_cli(["init", "--help"], cwd=tmp_path)
        # Init help should have --path and --interactive options (not evaluator options)
        assert "--path" in result.stdout
        assert "--interactive" in result.stdout
        # Should NOT have 'file' positional arg (evaluators have 'file' arg)
        assert "BAD-INIT" not in result.stdout

    def test_check_command_not_overridden(self, tmp_path, monkeypatch, run_cli):
        """Static 'check' command cannot be overridden by evaluators."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "check.yml").write_text(
            """
name: check
description: This should NOT override check
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Bad check
output_suffix: BAD-CHECK
"""
        )

        monkeypatch.chdir(tmp_path)

        result = run_cli(["check", "--help"], cwd=tmp_path)
        # Check command should NOT have evaluator-specific options
        # Evaluators have --timeout and positional 'file' arg
        assert "--timeout" not in result.stdout
        assert "BAD-CHECK" not in result.stdout


class TestEvaluatorExecution:
    """Test evaluator command execution routing."""

    def test_evaluator_has_file_argument(self, tmp_path, monkeypatch, run_cli):
        """Evaluator commands have a 'file' positional argument."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "myeval.yml").write_text(
            """
name: myeval
description: My evaluator
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Evaluate this
output_suffix: MY-EVAL
"""
        )

        monkeypatch.chdir(tmp_path)

        result = run_cli(["myeval", "--help"], cwd=tmp_path)
        assert result.returncode == 0
        assert "file" in result.stdout.lower()

    def test_evaluator_has_timeout_flag(self, tmp_path, monkeypatch, run_cli):
        """Evaluator commands have --timeout flag."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "myeval.yml").write_text(
            """
name: myeval
description: My evaluator
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Evaluate this
output_suffix: MY-EVAL
"""
        )

        monkeypatch.chdir(tmp_path)

        result = run_cli(["myeval", "--help"], cwd=tmp_path)
        assert "--timeout" in result.stdout or "-t" in result.stdout


class TestAliasSupport:
    """Test evaluator alias support."""

    def test_alias_in_help(self, tmp_path, monkeypatch, run_cli):
        """Evaluator aliases appear in help."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "knowledge.yml").write_text(
            """
name: knowledge
description: Knowledge evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Evaluate knowledge
output_suffix: KNOWLEDGE
aliases:
  - know
  - k
"""
        )

        monkeypatch.chdir(tmp_path)

        result = run_cli(["--help"], cwd=tmp_path)
        assert "knowledge" in result.stdout

    def test_alias_command_works(self, tmp_path, monkeypatch, run_cli):
        """Alias command shows same help as main command."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "knowledge.yml").write_text(
            """
name: knowledge
description: Knowledge evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Evaluate knowledge
output_suffix: KNOWLEDGE
aliases:
  - know
"""
        )

        monkeypatch.chdir(tmp_path)

        # Both 'knowledge --help' and 'know --help' should work
        result_main = run_cli(["knowledge", "--help"], cwd=tmp_path)
        result_alias = run_cli(["know", "--help"], cwd=tmp_path)
        assert result_main.returncode == 0
        assert result_alias.returncode == 0
        # Both should have 'file' argument
        assert "file" in result_main.stdout.lower()
        assert "file" in result_alias.stdout.lower()


class TestBackwardsCompatibility:
    """Test backwards compatibility with existing commands."""

    def test_evaluate_help_works(self, tmp_path, monkeypatch, run_cli):
        """adversarial evaluate --help still works."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = run_cli(["evaluate", "--help"], cwd=tmp_path)
        assert result.returncode == 0
        assert "file" in result.stdout.lower()

    def test_proofread_help_works(self, tmp_path, monkeypatch, run_cli):
        """adversarial proofread --help still works."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = run_cli(["proofread", "--help"], cwd=tmp_path)
        assert result.returncode == 0

    def test_review_help_works(self, tmp_path, monkeypatch, run_cli):
        """adversarial review --help still works."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = run_cli(["review", "--help"], cwd=tmp_path)
        assert result.returncode == 0

    def test_init_command_still_works(self, tmp_path, monkeypatch, run_cli):
        """Static init command still works."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = run_cli(["init", "--help"], cwd=tmp_path)
        assert result.returncode == 0
        assert "--interactive" in result.stdout or "-i" in result.stdout


class TestGracefulDegradation:
    """Test graceful degradation on errors."""

    def test_help_works_without_local_evaluators_dir(self, tmp_path, monkeypatch, run_cli):
        """CLI help works even without .adversarial/evaluators/ directory."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")
        # Note: NOT creating evaluators/ directory

        monkeypatch.chdir(tmp_path)

        result = run_cli(["--help"], cwd=tmp_path)
        assert result.returncode == 0
        # Built-in evaluators should still be present
        assert "evaluate" in result.stdout

    def test_help_works_without_adversarial_dir(self, tmp_path, monkeypatch, run_cli):
        """CLI help works even without .adversarial/ directory."""
        # Note: NOT creating .adversarial/ directory at all
        monkeypatch.chdir(tmp_path)

        result = run_cli(["--help"], cwd=tmp_path)
        assert result.returncode == 0
        # Built-in evaluators should still be present
        assert "evaluate" in result.stdout


class TestEvaluatorConfigAttribute:
    """Test that evaluator commands get evaluator_config attribute."""

    def test_builtin_evaluate_has_file_arg(self, tmp_path, monkeypatch, run_cli):
        """Built-in evaluate command should have file argument after dynamic registration."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = run_cli(["evaluate", "--help"], cwd=tmp_path)
        assert result.returncode == 0
        # After dynamic registration, evaluate should have 'file' not 'task_file'
        assert "file" in result.stdout.lower()

    def test_builtin_evaluate_has_timeout(self, tmp_path, monkeypatch, run_cli):
        """Built-in evaluate command should have --timeout flag after dynamic registration."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = run_cli(["evaluate", "--help"], cwd=tmp_path)
        assert "--timeout" in result.stdout or "-t" in result.stdout


class TestReviewCommandBackwardsCompatibility:
    """Test that review command maintains backwards compatibility."""

    def test_review_does_not_require_file(self, tmp_path, monkeypatch, run_cli):
        """Review command should NOT require a file argument (reviews git changes)."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = run_cli(["review", "--help"], cwd=tmp_path)
        assert result.returncode == 0
        # Review should NOT have --timeout flag (that's for evaluators)
        assert "--timeout" not in result.stdout

    def test_review_command_not_overridden_by_evaluator(self, tmp_path, monkeypatch, run_cli):
        """Review command cannot be overridden by local evaluator."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        # Create evaluator named 'review' (should be skipped)
        (eval_dir / "review.yml").write_text(
            """
name: review
description: This should NOT override review
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Bad review
output_suffix: BAD-REVIEW
"""
        )

        monkeypatch.chdir(tmp_path)

        result = run_cli(["review", "--help"], cwd=tmp_path)
        # Review should still be the static command
        assert "--timeout" not in result.stdout
        assert "BAD-REVIEW" not in result.stdout


class TestAliasStaticCommandProtection:
    """Test that evaluator aliases cannot override static commands."""

    def test_alias_cannot_override_static_command(self, tmp_path, monkeypatch, run_cli):
        """Evaluator alias matching static command should be skipped."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        # Create evaluator with alias 'init' (alias should be skipped)
        (eval_dir / "badeval.yml").write_text(
            """
name: badeval
description: Evaluator with bad alias
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test
output_suffix: BAD-EVAL
aliases:
  - init
  - safe_alias
"""
        )

        monkeypatch.chdir(tmp_path)

        # The CLI should not crash
        result = run_cli(["--help"], cwd=tmp_path)
        assert result.returncode == 0
        # badeval should be registered
        assert "badeval" in result.stdout
        # safe_alias should work
        assert "safe_alias" in result.stdout
        # 'init' should still be the static command
        result_init = run_cli(["init", "--help"], cwd=tmp_path)
        assert "--path" in result_init.stdout
        assert "--interactive" in result_init.stdout

    def test_evaluator_with_conflicting_name_and_alias(self, tmp_path, monkeypatch, run_cli):
        """Evaluator with conflicting name doesn't crash when alias is processed."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        # Create evaluator named 'init' with alias 'myalias'
        # The name conflicts, but the alias dict entry might try to re-register
        (eval_dir / "init.yml").write_text(
            """
name: init
description: Conflicting name evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test
output_suffix: INIT-EVAL
aliases:
  - myalias
"""
        )

        monkeypatch.chdir(tmp_path)

        # The CLI should not crash
        result = run_cli(["--help"], cwd=tmp_path)
        assert result.returncode == 0
        # 'init' should still be the static command
        assert "init" in result.stdout


class TestTimeoutConfiguration:
    """Test timeout configuration from YAML and CLI."""

    def test_evaluator_config_timeout_in_yaml(self, tmp_path, monkeypatch, run_cli):
        """Evaluator YAML timeout appears in help text."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "slow-model.yml").write_text(
            """
name: slow-model
description: Slow model evaluator
model: mistral/mistral-large-latest
api_key_env: MISTRAL_API_KEY
prompt: Evaluate this
output_suffix: SLOW-EVAL
timeout: 300
"""
        )

        monkeypatch.chdir(tmp_path)

        result = run_cli(["slow-model", "--help"], cwd=tmp_path)
        assert result.returncode == 0
        # Help should mention timeout flag with updated text
        assert "--timeout" in result.stdout or "-t" in result.stdout
        # Help text mentions evaluator config (may wrap across lines)
        assert "evaluator config" in result.stdout
        assert "max: 600" in result.stdout

    def test_timeout_help_text_updated(self, tmp_path, monkeypatch, run_cli):
        """Timeout help text shows it can come from config."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = run_cli(["evaluate", "--help"], cwd=tmp_path)
        assert result.returncode == 0
        # New help text mentioning evaluator config (may wrap across lines)
        assert "evaluator config" in result.stdout
        # Max 600 mentioned
        assert "max: 600" in result.stdout
