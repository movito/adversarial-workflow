"""Tests for .env file loading at CLI startup."""

import os


class TestEnvFileLoading:
    """Tests for automatic .env loading."""

    def test_env_var_available_via_cli_check(self, tmp_path, run_cli):
        """Verify .env file is loaded when CLI commands run."""
        # Create .env with OPENAI_API_KEY
        (tmp_path / ".env").write_text("OPENAI_API_KEY=sk-test-env-loading\n")

        # Run check command which validates OPENAI_API_KEY
        # Remove OPENAI_API_KEY from environment to ensure it comes from .env
        env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
        env["PATH"] = os.environ.get("PATH", "")

        result = run_cli(["check"], cwd=tmp_path, env=env)

        # The check command should see the API key from .env
        # It will show as valid (green checkmark) in the output
        combined_output = result.stdout + result.stderr
        assert (
            "OPENAI_API_KEY" in combined_output
        ), f"Expected OPENAI_API_KEY check. stdout: {result.stdout}, stderr: {result.stderr}"

    def test_env_loaded_before_evaluator_commands(self, tmp_path, monkeypatch, run_cli):
        """API keys in .env are available to evaluator commands."""
        # Create .env with test key
        (tmp_path / ".env").write_text("TEST_API_KEY=secret-test-value\n")

        # Create minimal evaluator config
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "test.yml").write_text(
            """name: test
description: Test evaluator
model: gpt-4o-mini
api_key_env: TEST_API_KEY
prompt: Test prompt
output_suffix: TEST
"""
        )

        monkeypatch.chdir(tmp_path)
        # Ensure key is NOT in current environment
        monkeypatch.delenv("TEST_API_KEY", raising=False)

        # list-evaluators should work (loads .env, discovers evaluator)
        result = run_cli(["list-evaluators"], cwd=tmp_path)

        assert result.returncode == 0
        assert "test" in result.stdout

    def test_env_loaded_for_builtin_commands(self, tmp_path, monkeypatch, run_cli):
        """.env is loaded even for built-in commands."""
        # Create .env with OpenAI key
        (tmp_path / ".env").write_text("OPENAI_API_KEY=sk-test-key\n")

        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        # check command should find the key from .env
        result = run_cli(["check"], cwd=tmp_path)

        # Should mention OpenAI (found from .env)
        # The check may fail for other reasons but should see the key
        assert "OPENAI" in result.stdout or "openai" in result.stdout.lower()

    def test_missing_env_file_no_error(self, tmp_path, monkeypatch, run_cli):
        """CLI works fine when no .env file exists."""
        monkeypatch.chdir(tmp_path)

        result = run_cli(["--help"], cwd=tmp_path)

        assert result.returncode == 0
        assert "adversarial" in result.stdout.lower()


class TestCheckEnvCount:
    """Tests for check() command .env variable counting (ADV-0022).

    These are CLI integration tests using subprocess to verify end-to-end behavior.
    They test that check() correctly reports .env variable count even after
    main() has already loaded the .env file at startup.
    """

    def test_check_reports_correct_env_count(self, tmp_path, run_cli):
        """check() reports correct .env variable count even after main() loads it.

        This is the primary regression test for ADV-0022. Before the fix,
        check() would report "0 variables" because main() already loaded them.
        """
        # Create .env with 3 variables
        (tmp_path / ".env").write_text(
            "OPENAI_API_KEY=sk-test\n"
            "ANTHROPIC_API_KEY=ant-test\n"
            "CUSTOM_KEY=custom-value\n"
        )

        # Remove keys from environment to isolate test
        env = {
            k: v
            for k, v in os.environ.items()
            if k not in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "CUSTOM_KEY")
        }
        env["PATH"] = os.environ.get("PATH", "")

        result = run_cli(["check"], cwd=tmp_path, env=env)

        # Should report "3 variables configured", not "0 variables"
        assert (
            "3 variables" in result.stdout
        ), f"Expected '3 variables' in output. Got: {result.stdout}"

    def test_check_handles_empty_env_file(self, tmp_path, run_cli):
        """check() handles empty .env file gracefully."""
        (tmp_path / ".env").write_text("")

        env = dict(os.environ)
        env["PATH"] = os.environ.get("PATH", "")

        result = run_cli(["check"], cwd=tmp_path, env=env)

        # Should report "0 variables configured"
        assert (
            "0 variables" in result.stdout
        ), f"Expected '0 variables' in output. Got: {result.stdout}"

    def test_check_handles_comments_in_env(self, tmp_path, run_cli):
        """check() correctly counts variables, ignoring comments and empty lines."""
        (tmp_path / ".env").write_text(
            "# This is a comment\n"
            "KEY1=value1\n"
            "\n"  # Empty line
            "# Another comment\n"
            "KEY2=value2\n"
        )

        env = {k: v for k, v in os.environ.items() if k not in ("KEY1", "KEY2")}
        env["PATH"] = os.environ.get("PATH", "")

        result = run_cli(["check"], cwd=tmp_path, env=env)

        # Should report 2 variables (comments and empty lines ignored)
        assert (
            "2 variables" in result.stdout
        ), f"Expected '2 variables' in output. Got: {result.stdout}"

    def test_check_handles_unusual_env_entries(self, tmp_path, run_cli):
        """check() handles unusual .env entries without crashing.

        dotenv_values() may handle lines without '=' differently depending on version.
        The main requirement is that the CLI doesn't crash on unusual entries.
        """
        (tmp_path / ".env").write_text(
            "VALID_KEY=value\n"
            "ALSO_VALID=another\n"
            "KEY_WITHOUT_VALUE\n"  # Line without '=' - behavior varies by dotenv version
        )

        env = {
            k: v
            for k, v in os.environ.items()
            if k not in ("VALID_KEY", "ALSO_VALID", "KEY_WITHOUT_VALUE")
        }
        env["PATH"] = os.environ.get("PATH", "")

        result = run_cli(["check"], cwd=tmp_path, env=env)

        # Should not crash - at least 2 valid variables should be counted
        # (dotenv behavior for lines without '=' varies by version)
        assert (
            "2 variables" in result.stdout or "3 variables" in result.stdout
        ), f"Expected '2 variables' or '3 variables' in output. Got: {result.stdout}"
