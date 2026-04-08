"""Tests for the generic evaluator runner."""

from unittest.mock import MagicMock, patch

import pytest

from adversarial_workflow.evaluators.config import EvaluatorConfig, ModelRequirement
from adversarial_workflow.evaluators.runner import (
    _check_file_size,
    _confirm_continue,
    _normalize_output_suffix,
    _print_platform_error,
    _print_rate_limit_error,
    _print_timeout_error,
    _report_verdict,
    _run_custom_evaluator,
    _warn_large_file,
    run_evaluator,
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

        result = run_evaluator(sample_config, str(test_file))
        assert result == 1
        captured = capsys.readouterr()
        assert "OPENAI_API_KEY" in captured.out


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

    def test_builtin_evaluators_have_prompts(self):
        """Built-in evaluators have inline prompts (ADV-0065)."""
        from adversarial_workflow.evaluators.builtins import BUILTIN_EVALUATORS

        for name, config in BUILTIN_EVALUATORS.items():
            assert len(config.prompt) > 100, f"{name} should have a non-trivial prompt"


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
        (eval_dir / "evaluate.yml").write_text(
            """
name: evaluate
description: Custom evaluate
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Custom prompt
output_suffix: CUSTOM-EVAL
"""
        )

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
            BOLD,
            RESET,
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


class TestModelResolutionInRunner:
    """Test model resolution integration with runner (ADV-0015)."""

    def test_legacy_model_field_still_works(self, tmp_path, monkeypatch):
        """Legacy evaluator with only model field still works (backwards compat)."""
        # Create test file and config
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        config_dir = tmp_path / ".adversarial"
        config_dir.mkdir()
        (config_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        # Mock litellm.completion
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "Evaluation details. " * 30 + "\nVerdict: APPROVED"
        )
        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            return_value=mock_response,
        ) as mock_completion:
            # Legacy config with only model field
            legacy_config = EvaluatorConfig(
                name="legacy-eval",
                description="Legacy evaluator",
                model="gpt-4o",
                api_key_env="OPENAI_API_KEY",
                prompt="Test prompt",
                output_suffix="TEST",
                source="local",
            )

            # This should work without model_requirement
            run_evaluator(legacy_config, str(test_file))

            # Verify litellm was called with the legacy model
            assert mock_completion.called, "litellm.completion should have been called"
            call_kwargs = mock_completion.call_args.kwargs
            assert call_kwargs["model"] == "gpt-4o"

    def test_model_requirement_resolves_correctly(self, tmp_path, monkeypatch):
        """Evaluator with model_requirement gets resolved to actual model ID."""
        # Create test file and config
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        config_dir = tmp_path / ".adversarial"
        config_dir.mkdir()
        (config_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        # Mock litellm.completion
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "Evaluation details. " * 30 + "\nVerdict: APPROVED"
        )
        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            return_value=mock_response,
        ) as mock_completion:
            # Config with model_requirement only
            config = EvaluatorConfig(
                name="new-eval",
                description="New evaluator",
                model="",
                api_key_env="",
                prompt="Test prompt",
                output_suffix="TEST",
                model_requirement=ModelRequirement(family="claude", tier="opus"),
                source="local",
            )

            run_evaluator(config, str(test_file))

            # Verify litellm was called with a resolved claude model
            assert mock_completion.called, "litellm.completion should have been called"
            call_kwargs = mock_completion.call_args.kwargs
            resolved_model = call_kwargs["model"]
            assert "claude" in resolved_model.lower()
            assert "opus" in resolved_model.lower()

    def test_model_field_takes_priority_over_requirement(self, tmp_path, monkeypatch):
        """Explicit model field takes priority over model_requirement (ADV-0032)."""
        # Create test file and config
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        config_dir = tmp_path / ".adversarial"
        config_dir.mkdir()
        (config_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")  # For explicit model

        # Mock litellm.completion
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "Evaluation details. " * 30 + "\nVerdict: APPROVED"
        )
        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            return_value=mock_response,
        ) as mock_completion:
            # Config with both fields - explicit model should win
            config = EvaluatorConfig(
                name="priority-eval",
                description="Priority test evaluator",
                model="gpt-4o",  # Explicit - should win
                api_key_env="OPENAI_API_KEY",
                prompt="Test prompt",
                output_suffix="TEST",
                model_requirement=ModelRequirement(
                    family="gemini", tier="flash"
                ),  # Should be ignored
                source="local",
            )

            run_evaluator(config, str(test_file))

            # Verify litellm was called with explicit model, not resolved gemini
            assert mock_completion.called, "litellm.completion should have been called"
            call_kwargs = mock_completion.call_args.kwargs
            resolved_model = call_kwargs["model"]
            assert resolved_model == "gpt-4o"
            assert "gemini" not in resolved_model.lower()

    def test_model_used_directly_with_invalid_requirement(self, tmp_path, monkeypatch):
        """Model field used directly even when requirement is invalid (ADV-0032)."""
        # Create test file and config
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        config_dir = tmp_path / ".adversarial"
        config_dir.mkdir()
        (config_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        # Mock litellm.completion
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "Evaluation details. " * 30 + "\nVerdict: APPROVED"
        )
        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            return_value=mock_response,
        ) as mock_completion:
            # Config with invalid model_requirement but valid model field
            config = EvaluatorConfig(
                name="direct-model-eval",
                description="Direct model evaluator",
                model="gpt-4o",  # Explicit - takes priority
                api_key_env="OPENAI_API_KEY",
                prompt="Test prompt",
                output_suffix="TEST",
                model_requirement=ModelRequirement(family="unknown", tier="unknown"),
                source="local",
            )

            # No warning - model field takes priority, requirement ignored
            run_evaluator(config, str(test_file))

            # Verify litellm was called with explicit model
            assert mock_completion.called, "litellm.completion should have been called"
            call_kwargs = mock_completion.call_args.kwargs
            assert call_kwargs["model"] == "gpt-4o"

    def test_resolution_error_when_no_fallback(self, tmp_path, monkeypatch, capsys):
        """ResolutionError when model_requirement fails and no legacy fallback."""
        # Create test file and config
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        config_dir = tmp_path / ".adversarial"
        config_dir.mkdir()
        (config_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("SOME_API_KEY", "test-key")

        # Config with invalid model_requirement and no legacy fallback
        config = EvaluatorConfig(
            name="error-eval",
            description="Error evaluator",
            model="",  # No fallback
            api_key_env="",
            prompt="Test prompt",
            output_suffix="TEST",
            model_requirement=ModelRequirement(family="unknown", tier="unknown"),
            source="local",
        )

        result = run_evaluator(config, str(test_file))

        # Should return error code 1
        assert result == 1
        captured = capsys.readouterr()
        assert "Unknown model family" in captured.out or "resolution" in captured.out.lower()


class TestOutputFilenameExtension:
    """Test that output filenames don't get double .md extension (issue #30)."""

    def test_suffix_without_md_extension(self, tmp_path, monkeypatch):
        """Suffix without .md produces single .md extension."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        config_dir = tmp_path / ".adversarial"
        config_dir.mkdir()
        logs_dir = config_dir / "logs"
        (config_dir / "config.yml").write_text(f"log_directory: {logs_dir}")

        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "Evaluation details. " * 30 + "\nVerdict: APPROVED"
        )
        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            return_value=mock_response,
        ):
            config = EvaluatorConfig(
                name="test-eval",
                description="Test",
                model="gpt-4o",
                api_key_env="OPENAI_API_KEY",
                prompt="Test prompt",
                output_suffix="TEST-EVAL",
                source="custom",
            )

            run_evaluator(config, str(test_file))

            # Check the output file was written with single .md
            written_files = list(logs_dir.glob("*"))
            assert len(written_files) == 1
            assert written_files[0].name == "test-TEST-EVAL.md"

    def test_suffix_with_md_extension_no_double(self, tmp_path, monkeypatch):
        """Suffix ending in .md does NOT produce double .md.md extension."""
        test_file = tmp_path / "task-spec.md"
        test_file.write_text("# Test")

        config_dir = tmp_path / ".adversarial"
        config_dir.mkdir()
        logs_dir = config_dir / "logs"
        (config_dir / "config.yml").write_text(f"log_directory: {logs_dir}")

        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "Evaluation details. " * 30 + "\nVerdict: APPROVED"
        )
        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            return_value=mock_response,
        ):
            config = EvaluatorConfig(
                name="arch-review",
                description="Test",
                model="gpt-4o",
                api_key_env="OPENAI_API_KEY",
                prompt="Test prompt",
                output_suffix="-arch-review.md",
                source="custom",
            )

            run_evaluator(config, str(test_file))

            # Check output file has single .md, not .md.md
            written_files = list(logs_dir.glob("*"))
            assert len(written_files) == 1
            assert written_files[0].name == "task-spec--arch-review.md"
            assert not written_files[0].name.endswith(".md.md")

    def test_builtin_suffix_with_md_extension_no_double(self, tmp_path, monkeypatch):
        """Built-in evaluator path also normalizes suffix (no double .md)."""
        test_file = tmp_path / "task-spec.md"
        test_file.write_text("# Test")

        config_dir = tmp_path / ".adversarial"
        config_dir.mkdir()
        logs_dir = config_dir / "logs"
        (config_dir / "config.yml").write_text(f"log_directory: {logs_dir}")

        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "Evaluation details. " * 30 + "\nVerdict: APPROVED"
        )
        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            return_value=mock_response,
        ):
            config = EvaluatorConfig(
                name="evaluate",
                description="Plan evaluation",
                model="gpt-4o",
                api_key_env="OPENAI_API_KEY",
                prompt="Test prompt",
                output_suffix="PLAN-EVAL.md",
                source="custom",
            )

            run_evaluator(config, str(test_file))

            written_files = list(logs_dir.glob("*"))
            assert len(written_files) == 1
            assert written_files[0].name == "task-spec-PLAN-EVAL.md"
            assert not (logs_dir / "task-spec-PLAN-EVAL.md.md").exists()

    def test_normalize_output_suffix_lowercase(self):
        """Helper strips lowercase .md."""
        assert _normalize_output_suffix("-arch-review.md") == "-arch-review"

    def test_normalize_output_suffix_uppercase(self):
        """Helper strips uppercase .MD."""
        assert _normalize_output_suffix("-arch-review.MD") == "-arch-review"

    def test_normalize_output_suffix_mixed_case(self):
        """Helper strips mixed-case .Md."""
        assert _normalize_output_suffix("-arch-review.Md") == "-arch-review"

    def test_normalize_output_suffix_no_extension(self):
        """Helper leaves suffix without .md unchanged."""
        assert _normalize_output_suffix("TEST-EVAL") == "TEST-EVAL"


class TestLiteLLMCompletionFlags:
    """Test litellm.completion() call parameters (ADV-0065, replaces ADV-0037)."""

    def test_litellm_called_with_correct_params(self, tmp_path, monkeypatch):
        """Verify litellm.completion() is called with model, messages, and timeout."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        config_dir = tmp_path / ".adversarial"
        config_dir.mkdir()
        (config_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "Evaluation details. " * 30 + "\nVerdict: APPROVED"
        )
        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            return_value=mock_response,
        ) as mock_completion:
            config = EvaluatorConfig(
                name="test-eval",
                description="Test evaluator",
                model="gpt-4o",
                api_key_env="OPENAI_API_KEY",
                prompt="Test prompt",
                output_suffix="TEST",
                source="custom",
            )

            run_evaluator(config, str(test_file))

            assert mock_completion.called, "litellm.completion should have been called"
            call_kwargs = mock_completion.call_args.kwargs
            assert call_kwargs["model"] == "gpt-4o"
            assert "messages" in call_kwargs
            assert "timeout" in call_kwargs


# ---------------------------------------------------------------------------
# New tests for uncovered error paths (ADV-0035)
# ---------------------------------------------------------------------------


class TestRunEvaluatorLargeFile:
    """Test large file handling paths in run_evaluator (lines 83-86)."""

    def _setup_env(self, tmp_path, monkeypatch, config):
        """Create the minimal filesystem+env for run_evaluator to reach the file-size check."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test", encoding="utf-8")

        config_dir = tmp_path / ".adversarial"
        config_dir.mkdir()
        (config_dir / "config.yml").write_text(
            "log_directory: .adversarial/logs/", encoding="utf-8"
        )

        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv(config.api_key_env, "test-key")
        return test_file

    def test_large_file_user_declines_returns_zero(
        self, sample_config, tmp_path, monkeypatch, capsys
    ):
        """Large file (>700 lines) + user declining cancels evaluation and returns 0."""
        test_file = self._setup_env(tmp_path, monkeypatch, sample_config)

        with (
            patch(
                "adversarial_workflow.evaluators.runner._check_file_size",
                return_value=(800, 25000),
            ),
            patch(
                "adversarial_workflow.evaluators.runner._confirm_continue",
                return_value=False,
            ),
        ):
            result = run_evaluator(sample_config, str(test_file))

        assert result == 0
        captured = capsys.readouterr()
        assert "Evaluation cancelled" in captured.out

    def test_large_file_warning_displayed(self, sample_config, tmp_path, monkeypatch, capsys):
        """Large file triggers the large-file warning before prompting."""
        test_file = self._setup_env(tmp_path, monkeypatch, sample_config)

        with (
            patch(
                "adversarial_workflow.evaluators.runner._check_file_size",
                return_value=(800, 25000),
            ),
            patch(
                "adversarial_workflow.evaluators.runner._confirm_continue",
                return_value=False,
            ),
        ):
            run_evaluator(sample_config, str(test_file))

        captured = capsys.readouterr()
        assert "Large file detected" in captured.out

    def test_large_file_user_accepts_continues(self, sample_config, tmp_path, monkeypatch):
        """Large file + user accepting continues to evaluation (doesn't return 0 early)."""
        test_file = self._setup_env(tmp_path, monkeypatch, sample_config)

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "Evaluation details. " * 30 + "\nVerdict: APPROVED"
        )
        with (
            patch(
                "adversarial_workflow.evaluators.runner._check_file_size",
                return_value=(800, 25000),
            ),
            patch(
                "adversarial_workflow.evaluators.runner._confirm_continue",
                return_value=True,
            ),
            patch(
                "adversarial_workflow.evaluators.runner.litellm.completion",
                return_value=mock_response,
            ) as mock_completion,
        ):
            result = run_evaluator(sample_config, str(test_file))

        # litellm was invoked — proves evaluation was not cancelled
        assert mock_completion.called
        # Evaluation succeeds with APPROVED verdict
        assert result == 0


class TestWarnLargeFile:
    """Direct tests for _warn_large_file helper (lines 312-315)."""

    def test_prints_large_file_detected(self, capsys):
        """Prints 'Large file detected' heading."""
        _warn_large_file(600, 25000)
        captured = capsys.readouterr()
        assert "Large file detected" in captured.out

    def test_prints_line_count(self, capsys):
        """Prints formatted line count."""
        _warn_large_file(600, 25000)
        captured = capsys.readouterr()
        assert "600" in captured.out

    def test_prints_token_estimate(self, capsys):
        """Prints formatted estimated token count."""
        _warn_large_file(600, 25000)
        captured = capsys.readouterr()
        assert "25,000" in captured.out


class TestConfirmContinue:
    """Direct tests for _confirm_continue helper (lines 320-321)."""

    def test_y_returns_true(self):
        """User typing 'y' means continue."""
        with patch("builtins.input", return_value="y"):
            assert _confirm_continue() is True

    def test_yes_returns_true(self):
        """User typing 'yes' means continue."""
        with patch("builtins.input", return_value="yes"):
            assert _confirm_continue() is True

    def test_uppercase_y_returns_true(self):
        """User typing 'Y' (uppercase) is treated as yes after lower()."""
        with patch("builtins.input", return_value="Y"):
            assert _confirm_continue() is True

    def test_n_returns_false(self):
        """User typing 'n' means cancel."""
        with patch("builtins.input", return_value="n"):
            assert _confirm_continue() is False

    def test_empty_returns_false(self):
        """Empty input (pressing Enter) defaults to No."""
        with patch("builtins.input", return_value=""):
            assert _confirm_continue() is False

    def test_arbitrary_text_returns_false(self):
        """Any other input defaults to No."""
        with patch("builtins.input", return_value="maybe"):
            assert _confirm_continue() is False


class TestBuiltinEvaluatorPath:
    """Test built-in evaluators use the LiteLLM path (ADV-0065)."""

    def test_builtin_uses_litellm_not_scripts(self, tmp_path, monkeypatch):
        """run_evaluator routes builtin evaluators through litellm.completion()."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test", encoding="utf-8")

        config_dir = tmp_path / ".adversarial"
        config_dir.mkdir()
        (config_dir / "config.yml").write_text(
            "log_directory: .adversarial/logs/", encoding="utf-8"
        )

        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        from adversarial_workflow.evaluators.builtins import BUILTIN_EVALUATORS

        config = BUILTIN_EVALUATORS["evaluate"]

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "Evaluation details. " * 30 + "\nVerdict: APPROVED"
        )
        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            return_value=mock_response,
        ) as mock_completion:
            result = run_evaluator(config, str(test_file))
            assert result == 0
        mock_completion.assert_called_once()

    def test_builtin_prompt_included_in_messages(self, tmp_path, monkeypatch):
        """Built-in evaluator prompt is passed in the litellm messages."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test", encoding="utf-8")

        config_dir = tmp_path / ".adversarial"
        config_dir.mkdir()
        (config_dir / "config.yml").write_text(
            "log_directory: .adversarial/logs/", encoding="utf-8"
        )

        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        from adversarial_workflow.evaluators.builtins import BUILTIN_EVALUATORS

        config = BUILTIN_EVALUATORS["evaluate"]

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "Evaluation details. " * 30 + "\nVerdict: APPROVED"
        )
        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            return_value=mock_response,
        ) as mock_completion:
            run_evaluator(config, str(test_file))

        call_kwargs = mock_completion.call_args.kwargs
        messages = call_kwargs["messages"]
        content = messages[0]["content"]
        assert "REVIEWER" in content
        assert "design review" in content.lower()


class TestRunCustomEvaluatorErrors:
    """Test error paths in _run_custom_evaluator with LiteLLM (ADV-0065)."""

    def _make_config(self):
        return EvaluatorConfig(
            name="test-eval",
            description="Test",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            prompt="Test prompt",
            output_suffix="TEST",
            source="custom",
        )

    def test_rate_limit_error(self, tmp_path, capsys):
        """litellm.RateLimitError returns 1 with rate-limit message."""
        import litellm

        test_file = tmp_path / "test.md"
        test_file.write_text("# Test content", encoding="utf-8")
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()

        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            side_effect=litellm.RateLimitError(
                message="Rate limit exceeded",
                model="gpt-4o",
                llm_provider="openai",
            ),
        ):
            result = _run_custom_evaluator(
                self._make_config(), str(test_file), {"log_directory": str(logs_dir)}, 30, "gpt-4o"
            )

        assert result == 1
        captured = capsys.readouterr()
        assert "rate limit" in captured.out.lower()

    def test_timeout_error_returns_one(self, tmp_path, capsys):
        """litellm.Timeout returns 1 with timeout message."""
        import litellm

        test_file = tmp_path / "test.md"
        test_file.write_text("# Test content", encoding="utf-8")
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()

        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            side_effect=litellm.Timeout(
                message="Request timed out",
                model="gpt-4o",
                llm_provider="openai",
            ),
        ):
            result = _run_custom_evaluator(
                self._make_config(), str(test_file), {"log_directory": str(logs_dir)}, 30, "gpt-4o"
            )

        assert result == 1
        captured = capsys.readouterr()
        assert "timed out" in captured.out.lower()

    def test_auth_error_returns_one(self, tmp_path, capsys):
        """litellm.AuthenticationError returns 1 with auth error message."""
        import litellm

        test_file = tmp_path / "test.md"
        test_file.write_text("# Test content", encoding="utf-8")
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()

        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            side_effect=litellm.AuthenticationError(
                message="Invalid API key",
                model="gpt-4o",
                llm_provider="openai",
            ),
        ):
            result = _run_custom_evaluator(
                self._make_config(), str(test_file), {"log_directory": str(logs_dir)}, 30, "gpt-4o"
            )

        assert result == 1
        captured = capsys.readouterr()
        assert "api key" in captured.out.lower() or "auth" in captured.out.lower()

    def test_generic_exception_returns_one(self, tmp_path, capsys):
        """Generic exception from litellm returns 1."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test content", encoding="utf-8")
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()

        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            side_effect=Exception("Unexpected error"),
        ):
            result = _run_custom_evaluator(
                self._make_config(), str(test_file), {"log_directory": str(logs_dir)}, 30, "gpt-4o"
            )

        assert result == 1
        captured = capsys.readouterr()
        assert "error" in captured.out.lower()

    def test_successful_evaluation_calls_report_verdict(self, tmp_path, capsys):
        """On valid output, calls _report_verdict and returns its result."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test content", encoding="utf-8")
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()

        # Produce enough content so header + response >= 500 bytes, with a clear verdict
        large_content = "Verdict: APPROVED\n\n" + "Evaluation details. " * 30

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = large_content
        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            return_value=mock_response,
        ):
            result = _run_custom_evaluator(
                self._make_config(), str(test_file), {"log_directory": str(logs_dir)}, 30, "gpt-4o"
            )

        assert result == 0
        captured = capsys.readouterr()
        assert "APPROVED" in captured.out


class TestNoneResponseContent:
    """Test None response content handling (ADV-0065)."""

    def _make_config(self):
        return EvaluatorConfig(
            name="test-eval",
            description="Test",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            prompt="Test prompt",
            output_suffix="TEST",
            source="custom",
        )

    def test_none_content_writes_empty_output(self, tmp_path, capsys):
        """None response content produces empty output with warning."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test content", encoding="utf-8")
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None

        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            return_value=mock_response,
        ):
            result = _run_custom_evaluator(
                self._make_config(), str(test_file), {"log_directory": str(logs_dir)}, 30, "gpt-4o"
            )

        captured = capsys.readouterr()
        assert "empty response" in captured.out.lower() or result in (0, 1)


class TestHelperFunctions:
    """Direct tests for standalone helper functions (lines 334-354)."""

    def test_print_rate_limit_error_outputs_message(self, capsys):
        """_print_rate_limit_error prints rate limit message (lines 334-339)."""
        _print_rate_limit_error("test-file.md")
        captured = capsys.readouterr()
        assert "rate limit" in captured.out.lower()

    def test_print_rate_limit_error_includes_solutions(self, capsys):
        """_print_rate_limit_error prints the SOLUTIONS block."""
        _print_rate_limit_error("test-file.md")
        captured = capsys.readouterr()
        assert "SOLUTIONS" in captured.out

    def test_print_timeout_error_shows_duration(self, capsys):
        """_print_timeout_error prints timeout message with the configured duration (line 344)."""
        _print_timeout_error(300)
        captured = capsys.readouterr()
        assert "timed out" in captured.out.lower()
        assert "300" in captured.out

    def test_print_platform_error_non_windows(self, capsys):
        """_print_platform_error on Linux prints 'adversarial init' hint (lines 349-354)."""
        with patch("platform.system", return_value="Linux"):
            _print_platform_error()
        captured = capsys.readouterr()
        assert "Error" in captured.out
        assert "Script not found" in captured.out
        assert "adversarial init" in captured.out

    def test_print_platform_error_windows(self, capsys):
        """_print_platform_error on Windows mentions WSL (lines 349-354)."""
        with patch("platform.system", return_value="Windows"):
            _print_platform_error()
        captured = capsys.readouterr()
        assert "Windows" in captured.out
        assert "WSL" in captured.out


class TestReportVerdictAllTypes:
    """Test _report_verdict with every verdict string in each set."""

    @pytest.mark.parametrize("verdict", ["APPROVED", "PROCEED", "COMPLIANT", "PASS"])
    def test_pass_verdicts_return_zero(self, verdict, sample_config, tmp_path, capsys):
        """All PASS-set verdicts return 0."""
        log_file = tmp_path / "out.md"
        log_file.write_text("content", encoding="utf-8")
        result = _report_verdict(verdict, log_file, sample_config)
        assert result == 0
        captured = capsys.readouterr()
        assert verdict in captured.out

    @pytest.mark.parametrize(
        "verdict",
        ["NEEDS_REVISION", "REVISION_SUGGESTED", "MOSTLY_COMPLIANT", "CONCERNS"],
    )
    def test_revise_verdicts_return_one(self, verdict, sample_config, tmp_path, capsys):
        """All REVISE-set verdicts return 1."""
        log_file = tmp_path / "out.md"
        log_file.write_text("content", encoding="utf-8")
        result = _report_verdict(verdict, log_file, sample_config)
        assert result == 1
        captured = capsys.readouterr()
        assert verdict in captured.out

    @pytest.mark.parametrize(
        "verdict",
        ["REJECTED", "RETHINK", "RESTRUCTURE_NEEDED", "NON_COMPLIANT", "FAIL"],
    )
    def test_reject_verdicts_return_one(self, verdict, sample_config, tmp_path, capsys):
        """All REJECT-set verdicts return 1."""
        log_file = tmp_path / "out.md"
        log_file.write_text("content", encoding="utf-8")
        result = _report_verdict(verdict, log_file, sample_config)
        assert result == 1
        captured = capsys.readouterr()
        assert verdict in captured.out
