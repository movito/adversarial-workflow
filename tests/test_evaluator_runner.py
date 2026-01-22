"""Tests for the generic evaluator runner."""

import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from adversarial_workflow.evaluators.config import EvaluatorConfig
from adversarial_workflow.evaluators.runner import (
    run_evaluator,
    _check_file_size,
    _report_verdict,
)


@pytest.fixture
def sample_config():
    """Create a sample evaluator config for testing."""
    return EvaluatorConfig(
        name="test",
        description="Test evaluator",
        model="gpt-4o",
        api_key_env="OPENAI_API_KEY",
        prompt="Test prompt",
        output_suffix="TEST-EVAL",
        source="custom",
    )


@pytest.fixture
def builtin_config():
    """Create a built-in evaluator config for testing."""
    return EvaluatorConfig(
        name="evaluate",
        description="Plan evaluation",
        model="gpt-4o",
        api_key_env="OPENAI_API_KEY",
        prompt="",
        output_suffix="PLAN-EVALUATION",
        source="builtin",
    )


class TestRunEvaluatorErrors:
    """Test error handling in run_evaluator."""

    def test_file_not_found(self, sample_config, capsys):
        """Error when file doesn't exist."""
        result = run_evaluator(sample_config, "/nonexistent/file.md")
        assert result == 1
        captured = capsys.readouterr()
        assert "File not found" in captured.out

    def test_not_initialized(self, sample_config, tmp_path, monkeypatch, capsys):
        """Error when project not initialized."""
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        # Change to tmp_path (no .adversarial directory)
        monkeypatch.chdir(tmp_path)

        result = run_evaluator(sample_config, str(test_file))
        assert result == 1
        captured = capsys.readouterr()
        assert "Not initialized" in captured.out or "init" in captured.out.lower()

    def test_no_api_key(self, sample_config, tmp_path, monkeypatch, capsys):
        """Error when API key not set."""
        # Create test file and config
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        config_dir = tmp_path / ".adversarial"
        config_dir.mkdir()
        (config_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/bin/aider")

        result = run_evaluator(sample_config, str(test_file))
        assert result == 1
        captured = capsys.readouterr()
        assert "OPENAI_API_KEY" in captured.out

    def test_no_aider(self, sample_config, tmp_path, monkeypatch, capsys):
        """Error when aider not installed."""
        # Create test file and config
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        config_dir = tmp_path / ".adversarial"
        config_dir.mkdir()
        (config_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setattr(shutil, "which", lambda _: None)

        result = run_evaluator(sample_config, str(test_file))
        assert result == 1
        captured = capsys.readouterr()
        assert "Aider not found" in captured.out


class TestCheckFileSize:
    """Test file size checking."""

    def test_small_file(self, tmp_path):
        """Small file returns correct counts."""
        test_file = tmp_path / "small.md"
        test_file.write_text("Line 1\nLine 2\nLine 3")

        lines, tokens = _check_file_size(str(test_file))
        assert lines == 3
        assert tokens > 0

    def test_large_file(self, tmp_path):
        """Large file returns correct counts."""
        test_file = tmp_path / "large.md"
        content = "x" * 10000  # 10k characters
        test_file.write_text(content)

        lines, tokens = _check_file_size(str(test_file))
        assert tokens == 2500  # 10000 / 4


class TestReportVerdict:
    """Test verdict reporting."""

    def test_approved(self, sample_config, tmp_path, capsys):
        """APPROVED verdict returns 0."""
        log_file = tmp_path / "test.md"
        log_file.write_text("test")

        result = _report_verdict("APPROVED", log_file, sample_config)
        assert result == 0
        captured = capsys.readouterr()
        assert "APPROVED" in captured.out

    def test_needs_revision(self, sample_config, tmp_path, capsys):
        """NEEDS_REVISION verdict returns 1."""
        log_file = tmp_path / "test.md"
        log_file.write_text("test")

        result = _report_verdict("NEEDS_REVISION", log_file, sample_config)
        assert result == 1
        captured = capsys.readouterr()
        assert "NEEDS_REVISION" in captured.out

    def test_rejected(self, sample_config, tmp_path, capsys):
        """REJECTED verdict returns 1."""
        log_file = tmp_path / "test.md"
        log_file.write_text("test")

        result = _report_verdict("REJECTED", log_file, sample_config)
        assert result == 1
        captured = capsys.readouterr()
        assert "REJECTED" in captured.out

    def test_unknown_verdict(self, sample_config, tmp_path, capsys):
        """Unknown verdict returns 0."""
        log_file = tmp_path / "test.md"
        log_file.write_text("test")

        result = _report_verdict(None, log_file, sample_config)
        assert result == 0


class TestBuiltinEvaluators:
    """Test built-in evaluator configurations."""

    def test_builtin_evaluators_exist(self):
        """All built-in evaluators are defined."""
        from adversarial_workflow.evaluators.builtins import BUILTIN_EVALUATORS

        assert "evaluate" in BUILTIN_EVALUATORS
        assert "proofread" in BUILTIN_EVALUATORS
        assert "review" in BUILTIN_EVALUATORS

    def test_builtin_evaluators_are_builtin_source(self):
        """Built-in evaluators have source='builtin'."""
        from adversarial_workflow.evaluators.builtins import BUILTIN_EVALUATORS

        for name, config in BUILTIN_EVALUATORS.items():
            assert config.source == "builtin", f"{name} should have source='builtin'"


class TestGetAllEvaluators:
    """Test get_all_evaluators function."""

    def test_returns_builtins(self, tmp_path, monkeypatch):
        """Returns built-in evaluators when no local evaluators."""
        monkeypatch.chdir(tmp_path)

        from adversarial_workflow.evaluators import get_all_evaluators
        evaluators = get_all_evaluators()

        assert "evaluate" in evaluators
        assert "proofread" in evaluators
        assert "review" in evaluators

    def test_local_overrides_builtin(self, tmp_path, monkeypatch):
        """Local evaluator overrides built-in with same name."""
        # Create local evaluator that overrides 'evaluate'
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "evaluate.yml").write_text("""
name: evaluate
description: Custom evaluate
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Custom prompt
output_suffix: CUSTOM-EVAL
""")

        monkeypatch.chdir(tmp_path)

        from adversarial_workflow.evaluators import get_all_evaluators
        evaluators = get_all_evaluators()

        # Should have the local version
        assert evaluators["evaluate"].model == "gpt-4o-mini"
        assert evaluators["evaluate"].source == "local"


class TestUtilsModule:
    """Test utils module exports."""

    def test_colors_import(self):
        """Color constants are importable."""
        from adversarial_workflow.utils.colors import (
            RESET, BOLD, GREEN, YELLOW, RED, CYAN, GRAY
        )
        assert RESET == "\033[0m"
        assert BOLD == "\033[1m"

    def test_config_import(self):
        """load_config is importable."""
        from adversarial_workflow.utils.config import load_config
        assert callable(load_config)

    def test_validation_import(self):
        """validate_evaluation_output is importable."""
        from adversarial_workflow.utils.validation import validate_evaluation_output
        assert callable(validate_evaluation_output)
