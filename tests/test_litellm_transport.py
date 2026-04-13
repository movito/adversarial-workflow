"""Tests for LiteLLM transport layer.

Tests litellm.completion() in _run_custom_evaluator(). Covers:
- Correct model string and prompt passthrough
- Response content extraction
- Error handling (rate limit, auth, timeout)
- Output writing to log file
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from adversarial_workflow.evaluators.config import EvaluatorConfig
from adversarial_workflow.evaluators.runner import (
    _run_custom_evaluator,
    run_evaluator,
)


@pytest.fixture
def custom_config():
    """Create a custom evaluator config for testing."""
    return EvaluatorConfig(
        name="test-eval",
        description="Test evaluator",
        model="gpt-4o",
        api_key_env="OPENAI_API_KEY",
        prompt="You are a reviewer. Evaluate this document.",
        output_suffix="TEST-EVAL",
        source="local",
    )


@pytest.fixture
def project_env(tmp_path, monkeypatch):
    """Set up a minimal project environment."""
    config_dir = tmp_path / ".adversarial"
    config_dir.mkdir()
    logs_dir = tmp_path / ".adversarial" / "logs"
    logs_dir.mkdir()
    (config_dir / "config.yml").write_text(f"log_directory: {logs_dir}/")

    test_file = tmp_path / "test-doc.md"
    test_file.write_text("# Test Document\n\nThis is test content for evaluation.")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-12345")

    return {"tmp_path": tmp_path, "test_file": test_file, "logs_dir": logs_dir}


class TestLiteLLMCompletion:
    """Test litellm.completion() call in _run_custom_evaluator."""

    def test_correct_model_passed(self, custom_config, project_env):
        """Model string from config is passed directly to litellm.completion()."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "Evaluation details. " * 30 + "\nVerdict: APPROVED"
        )

        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            return_value=mock_response,
        ) as mock_completion:
            project_config = {"log_directory": str(project_env["logs_dir"]) + "/"}
            _run_custom_evaluator(
                custom_config,
                str(project_env["test_file"]),
                project_config,
                180,
                "gpt-4o",
            )

            mock_completion.assert_called_once()
            call_kwargs = mock_completion.call_args
            assert call_kwargs.kwargs["model"] == "gpt-4o"

    def test_prompt_constructed_correctly(self, custom_config, project_env):
        """Full prompt includes evaluator prompt + document content."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "Evaluation details. " * 30 + "\nVerdict: APPROVED"
        )

        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            return_value=mock_response,
        ) as mock_completion:
            project_config = {"log_directory": str(project_env["logs_dir"]) + "/"}
            _run_custom_evaluator(
                custom_config,
                str(project_env["test_file"]),
                project_config,
                180,
                "gpt-4o",
            )

            call_kwargs = mock_completion.call_args
            messages = call_kwargs.kwargs["messages"]
            assert len(messages) == 1
            assert messages[0]["role"] == "user"
            # Prompt should contain both the evaluator prompt and the document content
            content = messages[0]["content"]
            assert "You are a reviewer" in content
            assert "Test Document" in content

    def test_timeout_passed(self, custom_config, project_env):
        """Timeout value is passed to litellm.completion()."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "Evaluation details. " * 30 + "\nVerdict: APPROVED"
        )

        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            return_value=mock_response,
        ) as mock_completion:
            project_config = {"log_directory": str(project_env["logs_dir"]) + "/"}
            _run_custom_evaluator(
                custom_config,
                str(project_env["test_file"]),
                project_config,
                300,
                "gpt-4o",
            )

            call_kwargs = mock_completion.call_args
            assert call_kwargs.kwargs["timeout"] == 300

    def test_response_content_extracted(self, custom_config, project_env):
        """Response content from choices[0].message.content is written to output."""
        eval_content = "Evaluation details. " * 30 + "\nVerdict: APPROVED"
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = eval_content

        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            return_value=mock_response,
        ):
            project_config = {"log_directory": str(project_env["logs_dir"]) + "/"}
            result = _run_custom_evaluator(
                custom_config,
                str(project_env["test_file"]),
                project_config,
                180,
                "gpt-4o",
            )

            assert result == 0
            # Check output file was written with response content
            output_files = list(project_env["logs_dir"].glob("*.md"))
            assert len(output_files) == 1
            output_content = output_files[0].read_text()
            assert "Verdict: APPROVED" in output_content

    def test_output_file_has_header(self, custom_config, project_env):
        """Output file includes metadata header before response content."""
        eval_content = "Evaluation details. " * 30 + "\nVerdict: APPROVED"
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = eval_content

        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            return_value=mock_response,
        ):
            project_config = {"log_directory": str(project_env["logs_dir"]) + "/"}
            _run_custom_evaluator(
                custom_config,
                str(project_env["test_file"]),
                project_config,
                180,
                "gpt-4o",
            )

            output_files = list(project_env["logs_dir"].glob("*.md"))
            output_content = output_files[0].read_text()
            assert "**Evaluator**: test-eval" in output_content
            assert "**Model**: gpt-4o" in output_content
            assert "**Source**:" in output_content


class TestLiteLLMErrorHandling:
    """Test error handling for LiteLLM exceptions."""

    def test_rate_limit_error(self, custom_config, project_env, capsys):
        """RateLimitError returns 1 with rate limit message."""
        import litellm

        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            side_effect=litellm.RateLimitError(
                message="Rate limit exceeded",
                model="gpt-4o",
                llm_provider="openai",
            ),
        ):
            project_config = {"log_directory": str(project_env["logs_dir"]) + "/"}
            result = _run_custom_evaluator(
                custom_config,
                str(project_env["test_file"]),
                project_config,
                180,
                "gpt-4o",
            )

            assert result == 1
            captured = capsys.readouterr()
            assert "rate limit" in captured.out.lower()

    def test_authentication_error(self, custom_config, project_env, capsys):
        """AuthenticationError returns 1 with auth error message including resolved key name."""
        import litellm

        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            side_effect=litellm.AuthenticationError(
                message="Invalid API key",
                model="gpt-4o",
                llm_provider="openai",
            ),
        ):
            project_config = {"log_directory": str(project_env["logs_dir"]) + "/"}
            result = _run_custom_evaluator(
                custom_config,
                str(project_env["test_file"]),
                project_config,
                180,
                "gpt-4o",
                resolved_api_key_env="OPENAI_API_KEY",
            )

            assert result == 1
            captured = capsys.readouterr()
            assert "OPENAI_API_KEY" in captured.out

    def test_authentication_error_with_model_requirement(self, project_env, capsys):
        """AuthenticationError uses resolved_api_key_env, not empty config.api_key_env."""
        import litellm

        config = EvaluatorConfig(
            name="test-eval",
            description="Test evaluator",
            model="",
            api_key_env="",
            prompt="Test prompt",
            output_suffix="TEST-EVAL",
            source="local",
        )

        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            side_effect=litellm.AuthenticationError(
                message="Invalid API key",
                model="anthropic/claude-4-opus-20260115",
                llm_provider="anthropic",
            ),
        ):
            project_config = {"log_directory": str(project_env["logs_dir"]) + "/"}
            result = _run_custom_evaluator(
                config,
                str(project_env["test_file"]),
                project_config,
                180,
                "anthropic/claude-4-opus-20260115",
                resolved_api_key_env="ANTHROPIC_API_KEY",
            )

            assert result == 1
            captured = capsys.readouterr()
            # Should show the resolved key name, not empty string
            assert "ANTHROPIC_API_KEY" in captured.out

    def test_timeout_error(self, custom_config, project_env, capsys):
        """Timeout returns 1 with timeout message."""
        import litellm

        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            side_effect=litellm.Timeout(
                message="Request timed out",
                model="gpt-4o",
                llm_provider="openai",
            ),
        ):
            project_config = {"log_directory": str(project_env["logs_dir"]) + "/"}
            result = _run_custom_evaluator(
                custom_config,
                str(project_env["test_file"]),
                project_config,
                180,
                "gpt-4o",
            )

            assert result == 1
            captured = capsys.readouterr()
            assert "timed out" in captured.out.lower() or "timeout" in captured.out.lower()

    def test_none_response_content(self, custom_config, project_env, capsys):
        """None response content is handled gracefully."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None

        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            return_value=mock_response,
        ):
            project_config = {"log_directory": str(project_env["logs_dir"]) + "/"}
            result = _run_custom_evaluator(
                custom_config,
                str(project_env["test_file"]),
                project_config,
                180,
                "gpt-4o",
            )

            # Should handle gracefully — either return error or write empty
            assert result in (0, 1)

    def test_generic_exception(self, custom_config, project_env, capsys):
        """Generic exception from litellm returns 1."""
        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            side_effect=Exception("Unexpected LiteLLM error"),
        ):
            project_config = {"log_directory": str(project_env["logs_dir"]) + "/"}
            result = _run_custom_evaluator(
                custom_config,
                str(project_env["test_file"]),
                project_config,
                180,
                "gpt-4o",
            )

            assert result == 1
            captured = capsys.readouterr()
            assert "error" in captured.out.lower()


class TestRunEvaluatorWithLiteLLM:
    """Test the full run_evaluator() flow with LiteLLM."""

    def test_no_external_binary_needed(self, custom_config, project_env, capsys):
        """run_evaluator() does not require external binaries on PATH."""
        eval_content = "Evaluation details. " * 30 + "\nVerdict: APPROVED"
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = eval_content

        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            return_value=mock_response,
        ):
            result = run_evaluator(custom_config, str(project_env["test_file"]))

            # Should succeed using only LiteLLM API calls
            assert result == 0

    def test_builtin_uses_litellm_path(self, project_env, capsys):
        """Built-in evaluators now use the same LiteLLM code path."""
        from adversarial_workflow.evaluators.builtins import BUILTIN_EVALUATORS

        config = BUILTIN_EVALUATORS["evaluate"]

        eval_content = "Evaluation details. " * 30 + "\nVerdict: APPROVED"
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = eval_content

        with patch(
            "adversarial_workflow.evaluators.runner.litellm.completion",
            return_value=mock_response,
        ):
            result = run_evaluator(config, str(project_env["test_file"]))

            # Built-in should now work via LiteLLM, not shell scripts
            assert result == 0
