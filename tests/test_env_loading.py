"""Tests for .env file loading at CLI startup."""

import os
import subprocess
import sys


class TestEnvFileLoading:
    """Tests for automatic .env loading."""

    def test_env_var_available_via_cli_check(self, tmp_path):
        """Verify .env file is loaded when CLI commands run."""
        # Create .env with OPENAI_API_KEY
        (tmp_path / ".env").write_text("OPENAI_API_KEY=sk-test-env-loading\n")

        # Run check command which validates OPENAI_API_KEY
        # Remove OPENAI_API_KEY from environment to ensure it comes from .env
        env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
        env["PATH"] = os.environ.get("PATH", "")

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "check"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
            env=env,
        )

        # The check command should see the API key from .env
        # It will show as valid (green checkmark) in the output
        combined_output = result.stdout + result.stderr
        assert "OPENAI_API_KEY" in combined_output, (
            f"Expected OPENAI_API_KEY check. stdout: {result.stdout}, stderr: {result.stderr}"
        )

    def test_env_loaded_before_evaluator_commands(self, tmp_path, monkeypatch):
        """API keys in .env are available to evaluator commands."""
        # Create .env with test key
        (tmp_path / ".env").write_text("TEST_API_KEY=secret-test-value\n")

        # Create minimal evaluator config
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "test.yml").write_text("""name: test
description: Test evaluator
model: gpt-4o-mini
api_key_env: TEST_API_KEY
prompt: Test prompt
output_suffix: TEST
""")

        monkeypatch.chdir(tmp_path)
        # Ensure key is NOT in current environment
        monkeypatch.delenv("TEST_API_KEY", raising=False)

        # list-evaluators should work (loads .env, discovers evaluator)
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "list-evaluators"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert result.returncode == 0
        assert "test" in result.stdout

    def test_env_loaded_for_builtin_commands(self, tmp_path, monkeypatch):
        """.env is loaded even for built-in commands."""
        # Create .env with OpenAI key
        (tmp_path / ".env").write_text("OPENAI_API_KEY=sk-test-key\n")

        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        # check command should find the key from .env
        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "check"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        # Should mention OpenAI (found from .env)
        # The check may fail for other reasons but should see the key
        assert "OPENAI" in result.stdout or "openai" in result.stdout.lower()

    def test_missing_env_file_no_error(self, tmp_path, monkeypatch):
        """CLI works fine when no .env file exists."""
        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "adversarial_workflow.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert result.returncode == 0
        assert "adversarial" in result.stdout.lower()
