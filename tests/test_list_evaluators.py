"""Tests for adversarial list-evaluators command."""

import subprocess
import sys


class TestListEvaluatorsCommand:
    """Tests for list-evaluators CLI command."""

    def test_list_evaluators_shows_builtins(self, tmp_path, monkeypatch):
        """Built-in evaluators appear in output."""
        monkeypatch.chdir(tmp_path)
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "list-evaluators"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Built-in Evaluators" in result.stdout
        assert "evaluate" in result.stdout
        assert "proofread" in result.stdout
        assert "review" in result.stdout

    def test_list_evaluators_no_local_message(self, tmp_path, monkeypatch):
        """Shows helpful message when no local evaluators."""
        monkeypatch.chdir(tmp_path)
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "list-evaluators"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "No local evaluators" in result.stdout
        assert ".adversarial/evaluators/*.yml" in result.stdout

    def test_list_evaluators_with_local(self, tmp_path, monkeypatch):
        """Shows local evaluators when present."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "test.yml").write_text(
            """
name: test
description: Test evaluator
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: TEST
aliases:
  - t
"""
        )

        monkeypatch.chdir(tmp_path)
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "list-evaluators"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Local Evaluators" in result.stdout
        assert "test" in result.stdout
        assert "aliases: t" in result.stdout
        assert "model: gpt-4o-mini" in result.stdout

    def test_list_evaluators_help(self, tmp_path, monkeypatch):
        """list-evaluators appears in --help."""
        monkeypatch.chdir(tmp_path)
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "--help"],
            capture_output=True,
            text=True,
        )
        assert "list-evaluators" in result.stdout

    def test_list_evaluators_skips_alias_duplicates(self, tmp_path, monkeypatch):
        """Aliases do not cause duplicate entries in output."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "athena.yml").write_text(
            """
name: athena
description: Knowledge evaluation using Gemini 2.5 Pro
model: gemini-2.5-pro
api_key_env: GEMINI_API_KEY
prompt: Athena evaluation prompt
output_suffix: KNOWLEDGE-EVALUATION
aliases:
  - knowledge
  - research
"""
        )

        monkeypatch.chdir(tmp_path)
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "list-evaluators"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        # Should only show athena once, not three times (name + 2 aliases)
        assert result.stdout.count("Knowledge evaluation") == 1
        assert "aliases: knowledge, research" in result.stdout

    def test_list_evaluators_shows_version_if_not_default(self, tmp_path, monkeypatch):
        """Shows version only when it differs from default 1.0.0."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "custom.yml").write_text(
            """
name: custom
description: Custom evaluator v2
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Custom prompt
output_suffix: CUSTOM
version: 2.0.0
"""
        )

        monkeypatch.chdir(tmp_path)
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "list-evaluators"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "version: 2.0.0" in result.stdout
