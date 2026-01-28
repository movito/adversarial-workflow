"""Integration tests for timeout configuration flow.

These tests verify that timeout values flow correctly through the entire stack:
YAML config -> CLI parsing -> runner execution.
"""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from adversarial_workflow.evaluators.config import EvaluatorConfig


class TestTimeoutIntegration:
    """Integration tests for timeout configuration."""

    def test_yaml_timeout_flows_to_runner(self, tmp_path, monkeypatch):
        """Timeout from YAML config flows through to run_evaluator."""
        from adversarial_workflow.cli import main

        # Setup project structure
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        # Create evaluator with custom timeout
        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "slow-model.yml").write_text(
            """
name: slow-model
description: Slow model evaluator
model: mistral/mistral-large-latest
api_key_env: MISTRAL_API_KEY
prompt: Evaluate this document
output_suffix: SLOW-EVAL
timeout: 300
"""
        )

        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test document")

        monkeypatch.chdir(tmp_path)

        # Mock run_evaluator to capture the timeout parameter
        captured_timeout = []

        def mock_run_evaluator(config, file_path, timeout):
            captured_timeout.append(timeout)
            return 0

        with patch("adversarial_workflow.evaluators.run_evaluator", mock_run_evaluator):
            with patch("sys.argv", ["adversarial", "slow-model", str(test_file)]):
                result = main()

        assert result == 0
        assert len(captured_timeout) == 1
        assert captured_timeout[0] == 300  # from YAML

    def test_cli_timeout_overrides_yaml(self, tmp_path, monkeypatch):
        """CLI --timeout flag overrides YAML timeout value."""
        from adversarial_workflow.cli import main

        # Setup project structure
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        # Create evaluator with custom timeout
        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "slow-model.yml").write_text(
            """
name: slow-model
description: Slow model evaluator
model: mistral/mistral-large-latest
api_key_env: MISTRAL_API_KEY
prompt: Evaluate this document
output_suffix: SLOW-EVAL
timeout: 300
"""
        )

        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test document")

        monkeypatch.chdir(tmp_path)

        # Mock run_evaluator to capture the timeout parameter
        captured_timeout = []

        def mock_run_evaluator(config, file_path, timeout):
            captured_timeout.append(timeout)
            return 0

        with patch("adversarial_workflow.evaluators.run_evaluator", mock_run_evaluator):
            with patch(
                "sys.argv",
                ["adversarial", "slow-model", "--timeout", "400", str(test_file)],
            ):
                result = main()

        assert result == 0
        assert len(captured_timeout) == 1
        assert captured_timeout[0] == 400  # CLI override

    def test_default_timeout_when_not_specified(self, tmp_path, monkeypatch):
        """Default 180s used when timeout not in YAML or CLI."""
        from adversarial_workflow.cli import main

        # Setup project structure
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        # Create evaluator without timeout field
        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "basic.yml").write_text(
            """
name: basic
description: Basic evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Evaluate this document
output_suffix: BASIC-EVAL
"""
        )

        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test document")

        monkeypatch.chdir(tmp_path)

        # Mock run_evaluator to capture the timeout parameter
        captured_timeout = []

        def mock_run_evaluator(config, file_path, timeout):
            captured_timeout.append(timeout)
            return 0

        with patch("adversarial_workflow.evaluators.run_evaluator", mock_run_evaluator):
            with patch("sys.argv", ["adversarial", "basic", str(test_file)]):
                result = main()

        assert result == 0
        assert len(captured_timeout) == 1
        assert captured_timeout[0] == 180  # default

    def test_cli_timeout_clamped_to_600(self, tmp_path, monkeypatch, capsys):
        """CLI timeout >600 is clamped to 600 with warning."""
        from adversarial_workflow.cli import main

        # Setup project structure
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        # Create basic evaluator
        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "basic.yml").write_text(
            """
name: basic
description: Basic evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Evaluate this document
output_suffix: BASIC-EVAL
"""
        )

        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test document")

        monkeypatch.chdir(tmp_path)

        # Mock run_evaluator to capture the timeout parameter
        captured_timeout = []

        def mock_run_evaluator(config, file_path, timeout):
            captured_timeout.append(timeout)
            return 0

        with patch("adversarial_workflow.evaluators.run_evaluator", mock_run_evaluator):
            with patch(
                "sys.argv",
                ["adversarial", "basic", "--timeout", "999", str(test_file)],
            ):
                result = main()

        assert result == 0
        assert len(captured_timeout) == 1
        assert captured_timeout[0] == 600  # clamped

        # Check warning was printed
        captured = capsys.readouterr()
        assert "Warning" in captured.out
        assert "exceeds maximum" in captured.out
        assert "600" in captured.out

    def test_timeout_source_logged_cli(self, tmp_path, monkeypatch, capsys):
        """Timeout source is logged as 'CLI override' when using --timeout."""
        from adversarial_workflow.cli import main

        # Setup project structure
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        # Create evaluator
        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "test-eval.yml").write_text(
            """
name: test-eval
description: Test evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test
output_suffix: TEST
timeout: 200
"""
        )

        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        monkeypatch.chdir(tmp_path)

        def mock_run_evaluator(config, file_path, timeout):
            return 0

        with patch("adversarial_workflow.evaluators.run_evaluator", mock_run_evaluator):
            with patch(
                "sys.argv",
                ["adversarial", "test-eval", "--timeout", "300", str(test_file)],
            ):
                main()

        captured = capsys.readouterr()
        assert "Using timeout: 300s (CLI override)" in captured.out

    def test_timeout_source_logged_yaml(self, tmp_path, monkeypatch, capsys):
        """Timeout source is logged as 'evaluator config' when from YAML."""
        from adversarial_workflow.cli import main

        # Setup project structure
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        # Create evaluator with non-default timeout
        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "custom-eval.yml").write_text(
            """
name: custom-eval
description: Custom timeout evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test
output_suffix: CUSTOM
timeout: 250
"""
        )

        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        monkeypatch.chdir(tmp_path)

        def mock_run_evaluator(config, file_path, timeout):
            return 0

        with patch("adversarial_workflow.evaluators.run_evaluator", mock_run_evaluator):
            with patch("sys.argv", ["adversarial", "custom-eval", str(test_file)]):
                main()

        captured = capsys.readouterr()
        assert "Using timeout: 250s (evaluator config)" in captured.out

    def test_timeout_source_logged_default(self, tmp_path, monkeypatch, capsys):
        """Timeout source is logged as 'default' when using default 180s."""
        from adversarial_workflow.cli import main

        # Setup project structure
        adv_dir = tmp_path / ".adversarial"
        adv_dir.mkdir(parents=True)
        (adv_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        # Create evaluator without timeout field (uses default)
        eval_dir = adv_dir / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "default-eval.yml").write_text(
            """
name: default-eval
description: Default timeout evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test
output_suffix: DEFAULT
"""
        )

        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        monkeypatch.chdir(tmp_path)

        def mock_run_evaluator(config, file_path, timeout):
            return 0

        with patch("adversarial_workflow.evaluators.run_evaluator", mock_run_evaluator):
            with patch("sys.argv", ["adversarial", "default-eval", str(test_file)]):
                main()

        captured = capsys.readouterr()
        assert "Using timeout: 180s (default)" in captured.out
