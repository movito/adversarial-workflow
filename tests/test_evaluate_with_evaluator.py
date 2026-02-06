"""Tests for evaluate command with --evaluator flag (ADV-0031).

Tests the ability to select and run library-installed evaluators
via the `adversarial evaluate --evaluator <name>` command.
"""

import pytest


class TestEvaluatorFlagInHelp:
    """Test that --evaluator flag appears in evaluate command help."""

    def test_evaluate_has_evaluator_flag(self, tmp_path, monkeypatch, run_cli):
        """The evaluate command should have --evaluator flag in help."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        result = run_cli(["evaluate", "--help"], cwd=tmp_path)
        assert result.returncode == 0
        assert "--evaluator" in result.stdout
        assert "-e" in result.stdout
        assert ".adversarial/evaluators" in result.stdout

    def test_other_evaluators_no_evaluator_flag(self, tmp_path, monkeypatch, run_cli):
        """Other evaluator commands should NOT have --evaluator flag."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)

        # Check proofread - should NOT have --evaluator
        result = run_cli(["proofread", "--help"], cwd=tmp_path)
        assert result.returncode == 0
        assert "--evaluator" not in result.stdout


class TestEvaluatorNotFound:
    """Test error handling when evaluator is not found."""

    def test_no_evaluators_installed(self, tmp_path, monkeypatch, run_cli):
        """Error when no evaluators are installed."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")
        # Create empty evaluators directory
        (adv_dir / "evaluators").mkdir()

        monkeypatch.chdir(tmp_path)

        # Create a dummy file to evaluate
        task_file = tmp_path / "task.md"
        task_file.write_text("# Test task")

        result = run_cli(["evaluate", "--evaluator", "nonexistent", str(task_file)], cwd=tmp_path)
        assert result.returncode == 1
        assert "No evaluators installed" in result.stdout

    def test_evaluator_not_found_shows_available(self, tmp_path, monkeypatch, run_cli):
        """Error message shows available evaluators when not found."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir()
        (eval_dir / "available-evaluator.yml").write_text(
            """
name: available-evaluator
description: An available evaluator
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: TEST
"""
        )

        monkeypatch.chdir(tmp_path)

        task_file = tmp_path / "task.md"
        task_file.write_text("# Test task")

        result = run_cli(["evaluate", "--evaluator", "nonexistent", str(task_file)], cwd=tmp_path)
        assert result.returncode == 1
        assert "not found" in result.stdout
        assert "Available evaluators" in result.stdout
        assert "available-evaluator" in result.stdout


class TestEvaluatorSelection:
    """Test evaluator selection by name and alias."""

    def test_evaluator_selected_by_name(self, tmp_path, monkeypatch, run_cli):
        """Evaluator can be selected by its name."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")
        (adv_dir / "logs").mkdir()

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir()
        (eval_dir / "my-evaluator.yml").write_text(
            """
name: my-evaluator
description: My test evaluator
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: MY-EVAL
"""
        )

        monkeypatch.chdir(tmp_path)

        task_file = tmp_path / "task.md"
        task_file.write_text("# Test task")

        result = run_cli(
            ["evaluate", "--evaluator", "my-evaluator", str(task_file)],
            cwd=tmp_path,
        )

        # Should show "Using evaluator" message - the key assertion
        assert "Using evaluator: my-evaluator" in result.stdout
        # Should use the evaluator's model (shown in output)
        assert "gpt-4o-mini" in result.stdout

    def test_evaluator_selected_by_alias(self, tmp_path, monkeypatch, run_cli):
        """Evaluator can be selected by its alias."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")
        (adv_dir / "logs").mkdir()

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir()
        (eval_dir / "my-evaluator.yml").write_text(
            """
name: my-evaluator
description: My test evaluator
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: MY-EVAL
aliases:
  - me
  - myeval
"""
        )

        monkeypatch.chdir(tmp_path)

        task_file = tmp_path / "task.md"
        task_file.write_text("# Test task")

        result = run_cli(
            ["evaluate", "--evaluator", "me", str(task_file)],
            cwd=tmp_path,
        )

        # Should resolve alias to main name
        assert "Using evaluator: my-evaluator" in result.stdout

    def test_short_flag_works(self, tmp_path, monkeypatch, run_cli):
        """The -e short flag works same as --evaluator."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")
        (adv_dir / "logs").mkdir()

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir()
        (eval_dir / "short-test.yml").write_text(
            """
name: short-test
description: Short flag test
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: SHORT
"""
        )

        monkeypatch.chdir(tmp_path)

        task_file = tmp_path / "task.md"
        task_file.write_text("# Test task")

        result = run_cli(
            ["evaluate", "-e", "short-test", str(task_file)],
            cwd=tmp_path,
        )

        # Should work with -e flag
        assert "Using evaluator: short-test" in result.stdout


class TestBackwardCompatibility:
    """Test that evaluate without --evaluator flag works as before."""

    def test_no_flag_uses_builtin(self, tmp_path, monkeypatch, run_cli):
        """Without --evaluator, uses the built-in evaluate behavior."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")
        (adv_dir / "logs").mkdir()

        # Create some local evaluators
        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir()
        (eval_dir / "local-eval.yml").write_text(
            """
name: local-eval
description: Local evaluator
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Local prompt
output_suffix: LOCAL
"""
        )

        monkeypatch.chdir(tmp_path)

        task_file = tmp_path / "task.md"
        task_file.write_text("# Test task")

        result = run_cli(
            ["evaluate", str(task_file)],
            cwd=tmp_path,
        )

        # Should NOT show "Using evaluator" message (uses builtin)
        assert "Using evaluator:" not in result.stdout
        # Should show timeout from default
        assert "Using timeout:" in result.stdout


class TestAliasDisplay:
    """Test that aliases are displayed properly in error messages."""

    def test_aliases_shown_in_available_list(self, tmp_path, monkeypatch, run_cli):
        """Aliases are shown when listing available evaluators."""
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir()
        (eval_dir / "aliased-eval.yml").write_text(
            """
name: aliased-eval
description: Evaluator with aliases
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: ALIASED
aliases:
  - ae
  - aliased
"""
        )

        monkeypatch.chdir(tmp_path)

        task_file = tmp_path / "task.md"
        task_file.write_text("# Test task")

        result = run_cli(["evaluate", "--evaluator", "nonexistent", str(task_file)], cwd=tmp_path)

        assert result.returncode == 1
        assert "aliased-eval" in result.stdout
        assert "aliases:" in result.stdout
        assert "ae" in result.stdout
        assert "aliased" in result.stdout
