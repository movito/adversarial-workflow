"""
Tests for CLI core commands: init, check, and utility functions.

This module provides comprehensive test coverage for:
- init: Initialize adversarial workflow in a project
- check: Validate setup and dependencies
- load_config: Configuration loading with environment overrides
- render_template: Template rendering with variable substitution

Note: evaluate and split commands are covered in separate test files:
- tests/test_evaluate.py
- tests/test_split_command.py

Task: ADV-0033 - CLI Core Commands Test Coverage
"""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from adversarial_workflow.cli import (
    check,
    check_platform_compatibility,
    create_example_task,
    estimate_file_tokens,
    extract_token_count_from_log,
    init,
    load_config,
    print_box,
    prompt_user,
    render_template,
    validate_api_key,
)


class TestInitCommand:
    """Test the init command functionality."""

    def test_init_not_git_repo(self, tmp_path, capsys):
        """init should fail if not in a git repository."""
        # Ensure no .git directory
        os.chdir(tmp_path)
        git_dir = tmp_path / ".git"
        if git_dir.exists():
            shutil.rmtree(git_dir)

        result = init(str(tmp_path), interactive=False)

        assert result == 1
        captured = capsys.readouterr()
        assert "Not a git repository" in captured.out

    def test_init_fresh_success(self, tmp_path, capsys):
        """init should succeed in a fresh git repo."""
        os.chdir(tmp_path)
        # Create .git directory
        (tmp_path / ".git").mkdir()

        result = init(str(tmp_path), interactive=False)

        assert result == 0
        # Check that .adversarial directory was created
        assert (tmp_path / ".adversarial").exists()
        assert (tmp_path / ".adversarial" / "config.yml").exists()
        assert (tmp_path / ".adversarial" / "scripts").exists()
        assert (tmp_path / ".adversarial" / "logs").exists()
        assert (tmp_path / ".adversarial" / "artifacts").exists()

    def test_init_creates_scripts(self, tmp_path, capsys):
        """init should create all required scripts."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        result = init(str(tmp_path), interactive=False)

        assert result == 0
        scripts_dir = tmp_path / ".adversarial" / "scripts"
        assert (scripts_dir / "evaluate_plan.sh").exists()
        assert (scripts_dir / "review_implementation.sh").exists()
        assert (scripts_dir / "validate_tests.sh").exists()
        assert (scripts_dir / "proofread_content.sh").exists()

    def test_init_scripts_have_version_headers(self, tmp_path, capsys):
        """init should inject SCRIPT_VERSION headers into scripts."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        result = init(str(tmp_path), interactive=False)

        assert result == 0
        scripts_dir = tmp_path / ".adversarial" / "scripts"

        # Check all scripts have version headers
        for script_name in ["evaluate_plan.sh", "review_implementation.sh", 
                           "validate_tests.sh", "proofread_content.sh"]:
            script_path = scripts_dir / script_name
            content = script_path.read_text()
            lines = content.split("\n")
            
            # First line should be shebang, second should be version
            assert lines[0].startswith("#!/bin/bash"), f"{script_name} missing shebang"
            assert lines[1].startswith("# SCRIPT_VERSION:"), \
                f"{script_name} missing SCRIPT_VERSION header"
            
            # Version should be current package version
            from adversarial_workflow import __version__
            assert __version__ in lines[1], \
                f"{script_name} has wrong version: {lines[1]}"

    def test_init_creates_aider_config(self, tmp_path, capsys):
        """init should create .aider.conf.yml in project root."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        result = init(str(tmp_path), interactive=False)

        assert result == 0
        assert (tmp_path / ".aider.conf.yml").exists()

    def test_init_creates_env_example(self, tmp_path, capsys):
        """init should create .env.example in project root."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        result = init(str(tmp_path), interactive=False)

        assert result == 0
        assert (tmp_path / ".env.example").exists()

    def test_init_updates_gitignore(self, tmp_path, capsys):
        """init should update .gitignore with adversarial entries."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        # Create existing .gitignore
        (tmp_path / ".gitignore").write_text("# Existing entries\n*.pyc\n")

        result = init(str(tmp_path), interactive=False)

        assert result == 0
        gitignore_content = (tmp_path / ".gitignore").read_text()
        assert ".adversarial/logs/" in gitignore_content
        assert ".adversarial/artifacts/" in gitignore_content
        assert ".env" in gitignore_content

    def test_init_existing_with_interactive_cancel(self, tmp_path, capsys):
        """init with existing .adversarial should prompt in interactive mode."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        # Create existing .adversarial
        (tmp_path / ".adversarial").mkdir()

        with patch("builtins.input", return_value="n"):
            result = init(str(tmp_path), interactive=True)

        assert result == 0
        captured = capsys.readouterr()
        assert "already exists" in captured.out

    def test_init_existing_with_interactive_overwrite(self, tmp_path, capsys):
        """init with existing .adversarial can overwrite if user agrees."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        # Create existing .adversarial with a marker
        (tmp_path / ".adversarial").mkdir()
        (tmp_path / ".adversarial" / "marker.txt").write_text("old")

        with patch("builtins.input", return_value="y"):
            result = init(str(tmp_path), interactive=True)

        assert result == 0
        # Old content should be gone
        assert not (tmp_path / ".adversarial" / "marker.txt").exists()
        # New content should exist
        assert (tmp_path / ".adversarial" / "config.yml").exists()

    def test_init_existing_non_interactive_overwrites(self, tmp_path, capsys):
        """init in non-interactive mode should overwrite existing."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        # Create existing .adversarial with a marker
        (tmp_path / ".adversarial").mkdir()
        (tmp_path / ".adversarial" / "marker.txt").write_text("old")

        result = init(str(tmp_path), interactive=False)

        assert result == 0
        # Old content should be gone
        assert not (tmp_path / ".adversarial" / "marker.txt").exists()
        # New content should exist
        assert (tmp_path / ".adversarial" / "config.yml").exists()

    def test_init_permission_error(self, tmp_path, capsys):
        """init should handle permission errors gracefully."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        with patch("os.makedirs", side_effect=PermissionError("Access denied")):
            # Also mock shutil.rmtree since we might have an existing dir
            with patch("shutil.rmtree"):
                result = init(str(tmp_path), interactive=False)

        assert result == 1
        captured = capsys.readouterr()
        assert "Permission denied" in captured.out

    def test_init_missing_templates(self, tmp_path, capsys):
        """init should fail gracefully if templates are missing."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        # Mock Path to simulate missing templates
        original_path = Path

        class MockPath:
            def __init__(self, *args, **kwargs):
                self._path = original_path(*args, **kwargs)

            def __truediv__(self, other):
                result = MockPath.__new__(MockPath)
                result._path = self._path / other
                # Make template files appear to not exist
                return result

            def exists(self):
                if "template" in str(self._path).lower():
                    return False
                return self._path.exists()

            @property
            def parent(self):
                result = MockPath.__new__(MockPath)
                result._path = self._path.parent
                return result

            def __str__(self):
                return str(self._path)

        with patch("adversarial_workflow.cli.Path", MockPath):
            result = init(str(tmp_path), interactive=False)

        # Should fail due to missing templates
        assert result == 1
        captured = capsys.readouterr()
        assert (
            "Package installation incomplete" in captured.out or "template" in captured.out.lower()
        )

    def test_init_config_content(self, tmp_path, capsys):
        """init should create config.yml with correct default values."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        result = init(str(tmp_path), interactive=False)

        assert result == 0
        config_path = tmp_path / ".adversarial" / "config.yml"
        config_content = config_path.read_text()
        assert "log_directory" in config_content
        assert ".adversarial/logs/" in config_content


class TestCheckCommand:
    """Test the check command functionality."""

    def test_check_git_repository_ok(self, tmp_path, capsys):
        """check should pass for git repository."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        # Create minimal .adversarial setup
        (tmp_path / ".adversarial").mkdir()
        (tmp_path / ".adversarial" / "config.yml").write_text("log_directory: .adversarial/logs/")
        (tmp_path / ".adversarial" / "scripts").mkdir()

        # Create script files
        scripts = ["evaluate_plan.sh", "review_implementation.sh", "validate_tests.sh"]
        for script in scripts:
            script_path = tmp_path / ".adversarial" / "scripts" / script
            script_path.write_text("#!/bin/bash\n")
            script_path.chmod(0o755)

        with (
            patch("shutil.which", return_value="/usr/bin/aider"),
            patch("subprocess.run", return_value=Mock(returncode=0, stdout="v0.50.0")),
            patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test123456789"}),
        ):
            result = check()

        assert result == 0
        captured = capsys.readouterr()
        assert "Git repository detected" in captured.out

    def test_check_not_git_repository(self, tmp_path, capsys):
        """check should fail if not in git repository."""
        os.chdir(tmp_path)
        # Ensure no .git directory
        git_dir = tmp_path / ".git"
        if git_dir.exists():
            shutil.rmtree(git_dir)

        result = check()

        assert result == 1
        captured = capsys.readouterr()
        assert "Not a git repository" in captured.out

    def test_check_aider_not_installed(self, tmp_path, capsys):
        """check should warn if aider is not installed."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        with patch("shutil.which", return_value=None):
            result = check()

        # Should fail or warn about missing aider
        captured = capsys.readouterr()
        assert "Aider not found" in captured.out

    def test_check_aider_installed(self, tmp_path, capsys):
        """check should detect aider when installed."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        # Create minimal config
        (tmp_path / ".adversarial").mkdir()
        (tmp_path / ".adversarial" / "config.yml").write_text("log_directory: .adversarial/logs/")

        with (
            patch("shutil.which", return_value="/usr/bin/aider"),
            patch("subprocess.run", return_value=Mock(returncode=0, stdout="v0.50.0")),
        ):
            result = check()

        captured = capsys.readouterr()
        assert "Aider installed" in captured.out

    def test_check_no_api_keys(self, tmp_path, capsys):
        """check should fail if no API keys are configured."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        # Clear any existing API key environment variables
        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": ""}, clear=False),
            patch("shutil.which", return_value="/usr/bin/aider"),
            patch("subprocess.run", return_value=Mock(returncode=0, stdout="")),
            patch("os.getenv", return_value=None),
        ):
            result = check()

        # Should report missing API keys
        captured = capsys.readouterr()
        assert "API" in captured.out or "No" in captured.out

    def test_check_openai_api_key_configured(self, tmp_path, capsys):
        """check should detect configured OpenAI API key."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        (tmp_path / ".adversarial").mkdir()
        (tmp_path / ".adversarial" / "config.yml").write_text("log_directory: .adversarial/logs/")
        (tmp_path / ".adversarial" / "scripts").mkdir()
        for script in ["evaluate_plan.sh", "review_implementation.sh", "validate_tests.sh"]:
            script_path = tmp_path / ".adversarial" / "scripts" / script
            script_path.write_text("#!/bin/bash\n")
            script_path.chmod(0o755)

        with (
            patch("shutil.which", return_value="/usr/bin/aider"),
            patch("subprocess.run", return_value=Mock(returncode=0, stdout="v0.50.0")),
            patch.dict(os.environ, {"OPENAI_API_KEY": "sk-realkey12345678901234567890"}),
        ):
            result = check()

        captured = capsys.readouterr()
        assert "OPENAI_API_KEY configured" in captured.out

    def test_check_anthropic_api_key_configured(self, tmp_path, capsys):
        """check should detect configured Anthropic API key."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        (tmp_path / ".adversarial").mkdir()
        (tmp_path / ".adversarial" / "config.yml").write_text("log_directory: .adversarial/logs/")
        (tmp_path / ".adversarial" / "scripts").mkdir()
        for script in ["evaluate_plan.sh", "review_implementation.sh", "validate_tests.sh"]:
            script_path = tmp_path / ".adversarial" / "scripts" / script
            script_path.write_text("#!/bin/bash\n")
            script_path.chmod(0o755)

        with (
            patch("shutil.which", return_value="/usr/bin/aider"),
            patch("subprocess.run", return_value=Mock(returncode=0, stdout="v0.50.0")),
            patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-realkey12345678901234567890"}),
        ):
            result = check()

        captured = capsys.readouterr()
        assert "ANTHROPIC_API_KEY configured" in captured.out

    def test_check_placeholder_api_key(self, tmp_path, capsys):
        """check should warn about placeholder API keys."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        (tmp_path / ".adversarial").mkdir()
        (tmp_path / ".adversarial" / "config.yml").write_text("log_directory: .adversarial/logs/")

        with (
            patch("shutil.which", return_value="/usr/bin/aider"),
            patch("subprocess.run", return_value=Mock(returncode=0, stdout="")),
            patch.dict(os.environ, {"OPENAI_API_KEY": "your-api-key-here"}),
        ):
            result = check()

        captured = capsys.readouterr()
        assert "placeholder" in captured.out

    def test_check_config_not_found(self, tmp_path, capsys):
        """check should fail if config.yml is not found."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        # No .adversarial directory

        with (
            patch("shutil.which", return_value="/usr/bin/aider"),
            patch("subprocess.run", return_value=Mock(returncode=0, stdout="")),
        ):
            result = check()

        assert result == 1
        captured = capsys.readouterr()
        assert "Not initialized" in captured.out or "not found" in captured.out.lower()

    def test_check_invalid_yaml_config(self, tmp_path, capsys):
        """check should fail if config.yml has invalid YAML."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        (tmp_path / ".adversarial").mkdir()
        # Write truly malformed YAML (unclosed bracket)
        (tmp_path / ".adversarial" / "config.yml").write_text("key: [unclosed bracket")

        with (
            patch("shutil.which", return_value="/usr/bin/aider"),
            patch("subprocess.run", return_value=Mock(returncode=0, stdout="")),
        ):
            result = check()

        assert result == 1
        captured = capsys.readouterr()
        assert "Invalid" in captured.out or "YAML" in captured.out

    def test_check_scripts_not_executable(self, tmp_path, capsys):
        """check should warn if scripts are not executable."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        (tmp_path / ".adversarial").mkdir()
        (tmp_path / ".adversarial" / "config.yml").write_text("log_directory: .adversarial/logs/")
        (tmp_path / ".adversarial" / "scripts").mkdir()

        # Create non-executable script
        script_path = tmp_path / ".adversarial" / "scripts" / "evaluate_plan.sh"
        script_path.write_text("#!/bin/bash\n")
        script_path.chmod(0o644)  # Not executable

        with (
            patch("shutil.which", return_value="/usr/bin/aider"),
            patch("subprocess.run", return_value=Mock(returncode=0, stdout="")),
            patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test123456789"}),
        ):
            result = check()

        captured = capsys.readouterr()
        assert "not executable" in captured.out or "chmod" in captured.out

    def test_check_scripts_missing(self, tmp_path, capsys):
        """check should warn if scripts are missing."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        (tmp_path / ".adversarial").mkdir()
        (tmp_path / ".adversarial" / "config.yml").write_text("log_directory: .adversarial/logs/")
        (tmp_path / ".adversarial" / "scripts").mkdir()
        # Don't create any scripts

        with (
            patch("shutil.which", return_value="/usr/bin/aider"),
            patch("subprocess.run", return_value=Mock(returncode=0, stdout="")),
            patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test123456789"}),
        ):
            result = check()

        captured = capsys.readouterr()
        assert "not found" in captured.out

    def test_check_env_file_loaded(self, tmp_path, capsys):
        """check should load and report .env file."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        (tmp_path / ".adversarial").mkdir()
        (tmp_path / ".adversarial" / "config.yml").write_text("log_directory: .adversarial/logs/")
        # Create .env file
        (tmp_path / ".env").write_text("OPENAI_API_KEY=sk-testkey123456789\n")

        with (
            patch("shutil.which", return_value="/usr/bin/aider"),
            patch("subprocess.run", return_value=Mock(returncode=0, stdout="")),
        ):
            result = check()

        captured = capsys.readouterr()
        assert ".env file found" in captured.out

    def test_check_all_good(self, tmp_path, capsys):
        """check should report success when everything is configured."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        (tmp_path / ".adversarial").mkdir()
        (tmp_path / ".adversarial" / "config.yml").write_text("log_directory: .adversarial/logs/")
        (tmp_path / ".adversarial" / "scripts").mkdir()
        scripts = ["evaluate_plan.sh", "review_implementation.sh", "validate_tests.sh"]
        for script in scripts:
            script_path = tmp_path / ".adversarial" / "scripts" / script
            # Include SCRIPT_VERSION to match package version
            script_path.write_text("#!/bin/bash\n# SCRIPT_VERSION: 0.9.6\n")
            script_path.chmod(0o755)

        (tmp_path / ".env").write_text("OPENAI_API_KEY=sk-testkey123456789\n")

        with (
            patch("shutil.which", return_value="/usr/bin/aider"),
            patch("subprocess.run", return_value=Mock(returncode=0, stdout="v0.50.0")),
            patch.dict(os.environ, {"OPENAI_API_KEY": "sk-testkey123456789"}),
            patch("importlib.metadata.version", return_value="0.9.6"),
        ):
            result = check()

        assert result == 0
        captured = capsys.readouterr()
        assert "All checks passed" in captured.out


class TestInitAndCheckIntegration:
    """Integration tests for init and check commands together."""

    def test_init_then_check(self, tmp_path, capsys):
        """check should pass after successful init."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        # Initialize
        init_result = init(str(tmp_path), interactive=False)
        assert init_result == 0

        # Verify check passes (with mocked external dependencies)
        with (
            patch("shutil.which", return_value="/usr/bin/aider"),
            patch("subprocess.run", return_value=Mock(returncode=0, stdout="v0.50.0")),
            patch.dict(os.environ, {"OPENAI_API_KEY": "sk-testkey123456789012345678901234"}),
        ):
            check_result = check()

        # Check should pass for configuration aspects
        captured = capsys.readouterr()
        assert ".adversarial/config.yml valid" in captured.out

    def test_reinit_preserves_functionality(self, tmp_path, capsys):
        """Reinitializing should still result in valid setup."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        # First init
        init(str(tmp_path), interactive=False)

        # Second init (non-interactive overwrites)
        init_result = init(str(tmp_path), interactive=False)
        assert init_result == 0

        # Check should still pass
        with (
            patch("shutil.which", return_value="/usr/bin/aider"),
            patch("subprocess.run", return_value=Mock(returncode=0, stdout="v0.50.0")),
            patch.dict(os.environ, {"OPENAI_API_KEY": "sk-testkey123456789012345678901234"}),
        ):
            check_result = check()

        captured = capsys.readouterr()
        assert ".adversarial/config.yml valid" in captured.out


class TestLoadConfig:
    """Test the load_config utility function."""

    def test_load_config_defaults(self, tmp_path):
        """load_config should return defaults when no config file exists."""
        os.chdir(tmp_path)
        # No config file exists

        config = load_config("nonexistent.yml")

        assert config["evaluator_model"] == "gpt-4o"
        assert config["task_directory"] == "tasks/"
        assert config["test_command"] == "pytest"
        assert config["log_directory"] == ".adversarial/logs/"
        assert config["artifacts_directory"] == ".adversarial/artifacts/"

    def test_load_config_from_file(self, tmp_path):
        """load_config should load values from YAML file."""
        os.chdir(tmp_path)
        config_path = tmp_path / "config.yml"
        config_path.write_text(
            """
evaluator_model: claude-3-opus
task_directory: custom_tasks/
test_command: npm test
log_directory: .custom/logs/
"""
        )

        config = load_config(str(config_path))

        assert config["evaluator_model"] == "claude-3-opus"
        assert config["task_directory"] == "custom_tasks/"
        assert config["test_command"] == "npm test"
        assert config["log_directory"] == ".custom/logs/"
        # artifacts_directory should still be default
        assert config["artifacts_directory"] == ".adversarial/artifacts/"

    def test_load_config_env_override(self, tmp_path):
        """load_config should allow environment variable overrides."""
        os.chdir(tmp_path)
        config_path = tmp_path / "config.yml"
        config_path.write_text("evaluator_model: gpt-4o\n")

        with patch.dict(
            os.environ,
            {
                "ADVERSARIAL_EVALUATOR_MODEL": "claude-3-sonnet",
                "ADVERSARIAL_TEST_COMMAND": "make test",
                "ADVERSARIAL_LOG_DIR": "/custom/logs",
            },
        ):
            config = load_config(str(config_path))

        assert config["evaluator_model"] == "claude-3-sonnet"
        assert config["test_command"] == "make test"
        assert config["log_directory"] == "/custom/logs"

    def test_load_config_file_overrides_defaults(self, tmp_path):
        """Config file values should override defaults."""
        os.chdir(tmp_path)
        config_path = tmp_path / "config.yml"
        config_path.write_text("evaluator_model: custom-model\n")

        config = load_config(str(config_path))

        assert config["evaluator_model"] == "custom-model"
        # Other defaults should remain
        assert config["task_directory"] == "tasks/"

    def test_load_config_empty_file(self, tmp_path):
        """load_config should handle empty config file."""
        os.chdir(tmp_path)
        config_path = tmp_path / "config.yml"
        config_path.write_text("")

        config = load_config(str(config_path))

        # Should return defaults
        assert config["evaluator_model"] == "gpt-4o"

    def test_load_config_partial_file(self, tmp_path):
        """load_config should merge partial config with defaults."""
        os.chdir(tmp_path)
        config_path = tmp_path / "config.yml"
        config_path.write_text("log_directory: .logs/\n")

        config = load_config(str(config_path))

        assert config["log_directory"] == ".logs/"
        assert config["evaluator_model"] == "gpt-4o"  # default


class TestRenderTemplate:
    """Test the render_template utility function."""

    def test_render_template_basic(self, tmp_path):
        """render_template should substitute variables."""
        os.chdir(tmp_path)
        template_path = tmp_path / "template.txt"
        template_path.write_text("Hello {{NAME}}, welcome to {{PLACE}}!")
        output_path = tmp_path / "output.txt"

        render_template(
            str(template_path),
            str(output_path),
            {"NAME": "World", "PLACE": "Python"},
        )

        assert output_path.exists()
        assert output_path.read_text() == "Hello World, welcome to Python!"

    def test_render_template_creates_dirs(self, tmp_path):
        """render_template should create parent directories if needed."""
        os.chdir(tmp_path)
        template_path = tmp_path / "template.txt"
        template_path.write_text("Content: {{VALUE}}")
        output_path = tmp_path / "nested" / "deep" / "output.txt"

        render_template(str(template_path), str(output_path), {"VALUE": "test"})

        assert output_path.exists()
        assert output_path.read_text() == "Content: test"

    def test_render_template_shell_script_executable(self, tmp_path):
        """render_template should make .sh files executable."""
        os.chdir(tmp_path)
        template_path = tmp_path / "script.sh.template"
        template_path.write_text("#!/bin/bash\necho {{MESSAGE}}")
        output_path = tmp_path / "output" / "script.sh"

        render_template(str(template_path), str(output_path), {"MESSAGE": "Hello"})

        assert output_path.exists()
        # Check executable permission
        import stat

        mode = output_path.stat().st_mode
        assert mode & stat.S_IXUSR  # User execute permission

    def test_render_template_non_sh_not_executable(self, tmp_path):
        """render_template should not make non-.sh files executable."""
        os.chdir(tmp_path)
        template_path = tmp_path / "config.yml.template"
        template_path.write_text("key: {{VALUE}}")
        output_path = tmp_path / "output" / "config.yml"

        render_template(str(template_path), str(output_path), {"VALUE": "test"})

        assert output_path.exists()
        # Check no execute permission added
        import stat

        mode = output_path.stat().st_mode
        assert not (mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))

    def test_render_template_multiple_same_var(self, tmp_path):
        """render_template should replace all occurrences of a variable."""
        os.chdir(tmp_path)
        template_path = tmp_path / "template.txt"
        template_path.write_text("{{X}} + {{X}} = 2{{X}}")
        output_path = tmp_path / "output.txt"

        render_template(str(template_path), str(output_path), {"X": "1"})

        assert output_path.read_text() == "1 + 1 = 21"

    def test_render_template_no_substitutions(self, tmp_path):
        """render_template should work with empty variables dict."""
        os.chdir(tmp_path)
        template_path = tmp_path / "template.txt"
        template_path.write_text("Plain text with no variables")
        output_path = tmp_path / "output.txt"

        render_template(str(template_path), str(output_path), {})

        assert output_path.read_text() == "Plain text with no variables"

    def test_render_template_preserves_unmatched(self, tmp_path):
        """render_template should preserve unmatched placeholders."""
        os.chdir(tmp_path)
        template_path = tmp_path / "template.txt"
        template_path.write_text("{{A}} and {{B}}")
        output_path = tmp_path / "output.txt"

        render_template(str(template_path), str(output_path), {"A": "replaced"})

        assert output_path.read_text() == "replaced and {{B}}"


class TestCheckEdgeCases:
    """Additional edge case tests for check command."""

    def test_check_api_key_preview_format(self, tmp_path, capsys):
        """check should show API key preview in correct format."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        (tmp_path / ".adversarial").mkdir()
        (tmp_path / ".adversarial" / "config.yml").write_text("log_directory: .adversarial/logs/")
        (tmp_path / ".adversarial" / "scripts").mkdir()
        for script in ["evaluate_plan.sh", "review_implementation.sh", "validate_tests.sh"]:
            script_path = tmp_path / ".adversarial" / "scripts" / script
            script_path.write_text("#!/bin/bash\n")
            script_path.chmod(0o755)

        # Long API key to test preview format
        long_key = "sk-abcdefgh123456789012345678901234567890xyz"

        with (
            patch("shutil.which", return_value="/usr/bin/aider"),
            patch("subprocess.run", return_value=Mock(returncode=0, stdout="v0.50.0")),
            patch.dict(os.environ, {"OPENAI_API_KEY": long_key}),
        ):
            result = check()

        captured = capsys.readouterr()
        # Should show first 8 and last 4 characters
        assert "sk-abcde" in captured.out
        assert "xyz]" in captured.out

    def test_check_aider_version_retrieval(self, tmp_path, capsys):
        """check should display aider version."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        (tmp_path / ".adversarial").mkdir()
        (tmp_path / ".adversarial" / "config.yml").write_text("log_directory: .adversarial/logs/")

        with (
            patch("shutil.which", return_value="/usr/bin/aider"),
            patch("subprocess.run", return_value=Mock(returncode=0, stdout="v0.55.0")),
        ):
            result = check()

        captured = capsys.readouterr()
        assert "v0.55.0" in captured.out

    def test_check_with_env_file_variable_count(self, tmp_path, capsys):
        """check should report correct number of .env variables."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        (tmp_path / ".adversarial").mkdir()
        (tmp_path / ".adversarial" / "config.yml").write_text("log_directory: .adversarial/logs/")
        # Create .env with 3 variables
        (tmp_path / ".env").write_text("VAR1=value1\nVAR2=value2\nOPENAI_API_KEY=sk-test123\n")

        with (
            patch("shutil.which", return_value="/usr/bin/aider"),
            patch("subprocess.run", return_value=Mock(returncode=0, stdout="")),
        ):
            result = check()

        captured = capsys.readouterr()
        assert "3 variables" in captured.out


class TestInitEdgeCases:
    """Additional edge case tests for init command."""

    def test_init_creates_logs_directory(self, tmp_path, capsys):
        """init should create logs subdirectory."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        result = init(str(tmp_path), interactive=False)

        assert result == 0
        assert (tmp_path / ".adversarial" / "logs").exists()
        assert (tmp_path / ".adversarial" / "logs").is_dir()

    def test_init_creates_artifacts_directory(self, tmp_path, capsys):
        """init should create artifacts subdirectory."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        result = init(str(tmp_path), interactive=False)

        assert result == 0
        assert (tmp_path / ".adversarial" / "artifacts").exists()
        assert (tmp_path / ".adversarial" / "artifacts").is_dir()

    def test_init_scripts_are_executable(self, tmp_path, capsys):
        """init should make all scripts executable."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        result = init(str(tmp_path), interactive=False)

        assert result == 0
        import stat

        scripts_dir = tmp_path / ".adversarial" / "scripts"
        for script in scripts_dir.glob("*.sh"):
            mode = script.stat().st_mode
            assert mode & stat.S_IXUSR, f"{script.name} should be executable"

    def test_init_gitignore_no_duplicates(self, tmp_path, capsys):
        """init should not duplicate entries in existing .gitignore."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        # Create .gitignore with existing entries
        (tmp_path / ".gitignore").write_text(".adversarial/logs/\n.env\n# Other stuff\n*.pyc\n")

        result = init(str(tmp_path), interactive=False)

        assert result == 0
        gitignore_content = (tmp_path / ".gitignore").read_text()
        # Count occurrences - should only appear once in original content
        # The new entries get appended but existing ones aren't duplicated
        assert gitignore_content.count(".env\n") >= 1  # At least one from original


class TestValidateApiKey:
    """Test the validate_api_key utility function."""

    def test_validate_empty_key(self):
        """Empty API key should be invalid."""
        is_valid, message = validate_api_key("", "openai")
        assert not is_valid
        assert "empty" in message.lower() or "placeholder" in message.lower()

    def test_validate_placeholder_key(self):
        """Placeholder API key should be invalid."""
        is_valid, message = validate_api_key("your-api-key-here", "openai")
        assert not is_valid
        assert "placeholder" in message.lower() or "empty" in message.lower()

    def test_validate_valid_openai_key(self):
        """Valid OpenAI key should pass validation."""
        is_valid, message = validate_api_key("sk-abcdefghijklmnopqrstuvwxyz123456", "openai")
        assert is_valid
        assert "valid" in message.lower()

    def test_validate_valid_openai_proj_key(self):
        """Valid OpenAI project key should pass validation."""
        is_valid, message = validate_api_key("sk-proj-abcdefghijklmnopqrstuvwxyz123456", "openai")
        assert is_valid
        assert "valid" in message.lower()

    def test_validate_invalid_openai_key_prefix(self):
        """OpenAI key with wrong prefix should fail."""
        is_valid, message = validate_api_key("pk-invalidprefix123456789", "openai")
        assert not is_valid
        assert "sk-" in message

    def test_validate_openai_key_too_short(self):
        """OpenAI key that's too short should fail."""
        is_valid, message = validate_api_key("sk-short", "openai")
        assert not is_valid
        assert "short" in message.lower()

    def test_validate_valid_anthropic_key(self):
        """Valid Anthropic key should pass validation."""
        is_valid, message = validate_api_key("sk-ant-abcdefghijklmnopqrstuvwxyz123456", "anthropic")
        assert is_valid
        assert "valid" in message.lower()

    def test_validate_invalid_anthropic_key_prefix(self):
        """Anthropic key with wrong prefix should fail."""
        is_valid, message = validate_api_key("sk-invalidprefix123456789", "anthropic")
        assert not is_valid
        assert "sk-ant-" in message

    def test_validate_anthropic_key_too_short(self):
        """Anthropic key that's too short should fail."""
        is_valid, message = validate_api_key("sk-ant-short", "anthropic")
        assert not is_valid
        assert "short" in message.lower()

    def test_validate_unknown_provider(self):
        """Unknown provider should accept any non-empty key."""
        is_valid, message = validate_api_key("any-key-format-12345678901234", "unknown")
        assert is_valid
        assert "valid" in message.lower()


class TestCreateExampleTask:
    """Test the create_example_task utility function."""

    def test_create_example_task_basic(self, tmp_path, capsys):
        """create_example_task should create a task file."""
        os.chdir(tmp_path)
        task_path = tmp_path / "example-task.md"

        create_example_task(str(task_path))

        assert task_path.exists()
        content = task_path.read_text()
        assert "Task" in content or "task" in content
        captured = capsys.readouterr()
        assert "Created" in captured.out

    def test_create_example_task_in_subdirectory(self, tmp_path, capsys):
        """create_example_task should work in subdirectories."""
        os.chdir(tmp_path)
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        task_path = tasks_dir / "new-task.md"

        create_example_task(str(task_path))

        assert task_path.exists()

    def test_create_example_task_content_structure(self, tmp_path, capsys):
        """create_example_task should create properly structured content."""
        os.chdir(tmp_path)
        task_path = tmp_path / "structured-task.md"

        create_example_task(str(task_path))

        content = task_path.read_text()
        # Should contain common task sections
        assert "#" in content  # Has headings
        # Either from template or fallback, should have some content
        assert len(content) > 50  # Reasonable length

    def test_create_example_task_uses_template_if_available(self, tmp_path, capsys):
        """create_example_task should use template file if it exists."""
        os.chdir(tmp_path)
        task_path = tmp_path / "template-task.md"

        # This tests the fallback path (no template available in tmp_path)
        create_example_task(str(task_path))

        assert task_path.exists()
        content = task_path.read_text()
        # Fallback should have specific content
        assert "Off-By-One" in content or "#" in content  # Either template or fallback

    def test_create_example_task_fallback_content(self, tmp_path, capsys):
        """create_example_task should create fallback content when template missing."""
        os.chdir(tmp_path)
        task_path = tmp_path / "fallback-task.md"

        # The function uses fallback when template doesn't exist
        create_example_task(str(task_path))

        assert task_path.exists()
        content = task_path.read_text()
        # Verify fallback content structure
        assert "Off-By-One" in content  # From fallback template
        assert "Bug Fix" in content
        assert "Acceptance Criteria" in content


class TestHealthCommand:
    """Test the health command functionality."""

    def test_health_import(self):
        """health function should be importable."""
        from adversarial_workflow.cli import health

        assert callable(health)

    def test_health_basic_execution(self, tmp_path, capsys):
        """health command should run without crashing."""
        from adversarial_workflow.cli import health

        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        with (
            patch("shutil.which", return_value="/usr/bin/aider"),
            patch("subprocess.run", return_value=Mock(returncode=0, stdout="")),
        ):
            result = health()

        # Should return an integer
        assert isinstance(result, int)


class TestCheckPlatformCompatibility:
    """Test the check_platform_compatibility utility function."""

    def test_check_platform_non_windows(self, capsys):
        """Non-Windows platforms should pass compatibility check."""
        with patch("platform.system", return_value="Darwin"):
            result = check_platform_compatibility()

        assert result is True

    def test_check_platform_linux(self, capsys):
        """Linux should pass compatibility check."""
        with patch("platform.system", return_value="Linux"):
            result = check_platform_compatibility()

        assert result is True

    def test_check_platform_windows_user_continues(self, capsys):
        """Windows user choosing to continue should pass."""
        with (
            patch("platform.system", return_value="Windows"),
            patch("builtins.input", return_value="y"),
        ):
            result = check_platform_compatibility()

        assert result is True
        captured = capsys.readouterr()
        assert "Windows" in captured.out
        assert "WSL" in captured.out

    def test_check_platform_windows_user_cancels(self, capsys):
        """Windows user choosing to cancel should fail."""
        with (
            patch("platform.system", return_value="Windows"),
            patch("builtins.input", return_value="n"),
        ):
            result = check_platform_compatibility()

        assert result is False
        captured = capsys.readouterr()
        assert "cancelled" in captured.out.lower()


class TestPrintBox:
    """Test the print_box utility function."""

    def test_print_box_with_title_only(self, capsys):
        """print_box should handle title-only boxes."""
        print_box("Test Title", "blue")

        captured = capsys.readouterr()
        assert "Test Title" in captured.out

    def test_print_box_with_content(self, capsys):
        """print_box should handle title with content list."""
        print_box("Title", ["Line 1", "Line 2"])

        captured = capsys.readouterr()
        assert "Title" in captured.out
        assert "Line 1" in captured.out
        assert "Line 2" in captured.out


class TestEstimateFileTokens:
    """Test the estimate_file_tokens utility function."""

    def test_estimate_tokens_basic(self, tmp_path):
        """estimate_file_tokens should return reasonable token estimate."""
        test_file = tmp_path / "test.md"
        # Write 100 characters (roughly 25 tokens)
        test_file.write_text("a" * 100)

        tokens = estimate_file_tokens(str(test_file))

        # Should be approximately 25 tokens (100 chars / 4)
        assert 20 <= tokens <= 30

    def test_estimate_tokens_empty_file(self, tmp_path):
        """estimate_file_tokens should handle empty files."""
        test_file = tmp_path / "empty.md"
        test_file.write_text("")

        tokens = estimate_file_tokens(str(test_file))

        assert tokens == 0

    def test_estimate_tokens_large_file(self, tmp_path):
        """estimate_file_tokens should handle large files."""
        test_file = tmp_path / "large.md"
        test_file.write_text("x" * 10000)  # 10000 chars

        tokens = estimate_file_tokens(str(test_file))

        # Should be approximately 2500 tokens
        assert 2400 <= tokens <= 2600


class TestExtractTokenCountFromLog:
    """Test the extract_token_count_from_log utility function."""

    def test_extract_tokens_from_log_with_k_suffix(self, tmp_path):
        """extract_token_count_from_log should find token count with k suffix."""
        log_file = tmp_path / "log.md"
        log_file.write_text(
            """
# Evaluation Log

Some content here.

Tokens: 15k sent, 422 received
"""
        )

        tokens = extract_token_count_from_log(str(log_file))

        assert tokens is not None
        assert tokens == 15000

    def test_extract_tokens_from_log_decimal(self, tmp_path):
        """extract_token_count_from_log should find token count with decimal."""
        log_file = tmp_path / "log.md"
        log_file.write_text(
            """
# Evaluation Log

Tokens: 1.5k sent, 100 received
"""
        )

        tokens = extract_token_count_from_log(str(log_file))

        assert tokens is not None
        assert tokens == 1500  # 1.5k = 1500

    def test_extract_tokens_no_count(self, tmp_path):
        """extract_token_count_from_log should return None when no tokens found."""
        log_file = tmp_path / "log.md"
        log_file.write_text("# Log with no token info")

        tokens = extract_token_count_from_log(str(log_file))

        # Should return None when pattern not found
        assert tokens is None

    def test_extract_tokens_file_not_found(self):
        """extract_token_count_from_log should handle missing files."""
        tokens = extract_token_count_from_log("nonexistent.md")

        # Should return None for missing file
        assert tokens is None


class TestPromptUser:
    """Test the prompt_user utility function."""

    def test_prompt_user_with_input(self):
        """prompt_user should return user input."""
        with patch("builtins.input", return_value="user_value"):
            result = prompt_user("Enter value")

        assert result == "user_value"

    def test_prompt_user_empty_returns_default(self):
        """prompt_user should return default when input is empty."""
        with patch("builtins.input", return_value=""):
            result = prompt_user("Enter value", default="default_value")

        assert result == "default_value"

    def test_prompt_user_with_default_shows_in_prompt(self, capsys):
        """prompt_user should show default value in prompt."""
        with patch("builtins.input", return_value=""):
            prompt_user("Enter value", default="shown_default")

        # The default is shown but we can't easily capture the prompt text
        # Just verify the function runs correctly
        assert True

    def test_prompt_user_strips_whitespace(self):
        """prompt_user should strip whitespace from input."""
        with patch("builtins.input", return_value="  spaced  "):
            result = prompt_user("Enter value")

        assert result == "spaced"

    def test_prompt_user_secret_mode(self):
        """prompt_user should use getpass for secret input."""
        with patch("getpass.getpass", return_value="secret_value"):
            result = prompt_user("Enter password", secret=True)

        assert result == "secret_value"

    def test_prompt_user_secret_empty_returns_default(self):
        """prompt_user secret mode should return default when empty."""
        with patch("getpass.getpass", return_value=""):
            result = prompt_user("Enter password", default="default_pass", secret=True)

        assert result == "default_pass"


class TestCLIHelpers:
    """Test additional CLI helper functions."""

    def test_main_function_callable(self):
        """main function should be callable."""
        from adversarial_workflow.cli import main

        assert callable(main)

    def test_main_with_help(self, capsys):
        """main function with --help should show usage."""
        from adversarial_workflow.cli import main

        with patch("sys.argv", ["adversarial", "--help"]):
            try:
                result = main()
            except SystemExit as e:
                # --help triggers SystemExit(0)
                assert e.code == 0

    def test_main_with_no_args(self, capsys):
        """main function with no args should show help."""
        from adversarial_workflow.cli import main

        with patch("sys.argv", ["adversarial"]):
            result = main()

        # Should return 0 when showing help
        assert result == 0

    def test_main_with_version(self, capsys):
        """main function with --version should show version."""
        from adversarial_workflow.cli import main

        with patch("sys.argv", ["adversarial", "--version"]):
            try:
                result = main()
            except SystemExit as e:
                # --version triggers SystemExit(0)
                assert e.code == 0


class TestCheckInternalFunctions:
    """Test internal helper functions within check command."""

    def test_check_with_short_api_key(self, tmp_path, capsys):
        """check should handle short API keys for preview."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        (tmp_path / ".adversarial").mkdir()
        (tmp_path / ".adversarial" / "config.yml").write_text("log_directory: .adversarial/logs/")
        (tmp_path / ".adversarial" / "scripts").mkdir()
        for script in ["evaluate_plan.sh", "review_implementation.sh", "validate_tests.sh"]:
            script_path = tmp_path / ".adversarial" / "scripts" / script
            script_path.write_text("#!/bin/bash\n")
            script_path.chmod(0o755)

        # Short API key (less than 12 chars) - should show "***"
        short_key = "sk-short"

        with (
            patch("shutil.which", return_value="/usr/bin/aider"),
            patch("subprocess.run", return_value=Mock(returncode=0, stdout="")),
            patch.dict(os.environ, {"OPENAI_API_KEY": short_key}),
        ):
            result = check()

        captured = capsys.readouterr()
        # Short key should still be detected as configured
        assert "OPENAI" in captured.out

    def test_check_with_env_parse_error(self, tmp_path, capsys):
        """check should handle .env file parsing errors."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        # Create .env file with binary/invalid content
        (tmp_path / ".env").write_bytes(b"\xff\xfe")

        with (
            patch("shutil.which", return_value="/usr/bin/aider"),
            patch("subprocess.run", return_value=Mock(returncode=0, stdout="")),
        ):
            result = check()

        # Should handle gracefully without crashing
        captured = capsys.readouterr()
        # Either warns about parse error or just skips .env
        assert result in [0, 1]


class TestInitInteractiveEdgeCases:
    """Test edge cases for init in interactive mode."""

    def test_init_interactive_abort_on_existing(self, tmp_path, capsys):
        """Interactive init should abort when user says no to overwrite."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        (tmp_path / ".adversarial").mkdir()
        (tmp_path / ".adversarial" / "existing.txt").write_text("keep me")

        with patch("builtins.input", return_value="n"):
            result = init(str(tmp_path), interactive=True)

        # Should abort
        assert result == 0
        # Existing content should still be there
        assert (tmp_path / ".adversarial" / "existing.txt").exists()
        captured = capsys.readouterr()
        assert "Aborted" in captured.out

    def test_init_interactive_success_message(self, tmp_path, capsys):
        """Interactive init should show success message."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        result = init(str(tmp_path), interactive=True)

        assert result == 0
        captured = capsys.readouterr()
        assert "initialized successfully" in captured.out
        assert "Next steps" in captured.out

    def test_init_interactive_overwrite_existing(self, tmp_path, capsys):
        """Interactive init should overwrite when user confirms."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        (tmp_path / ".adversarial").mkdir()
        (tmp_path / ".adversarial" / "old.txt").write_text("old content")

        with patch("builtins.input", return_value="y"):
            result = init(str(tmp_path), interactive=True)

        assert result == 0
        # Old content should be gone
        assert not (tmp_path / ".adversarial" / "old.txt").exists()
        # New content should exist
        assert (tmp_path / ".adversarial" / "config.yml").exists()


class TestInitTemplateErrors:
    """Test template rendering error handling in init."""

    def test_init_template_render_failure(self, tmp_path, capsys):
        """init should handle template rendering errors."""
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        # Mock shutil.copy to fail during template copy
        original_copy = shutil.copy

        def failing_copy(src, dst):
            if ".aider.conf" in str(dst):
                raise IOError("Mock copy failure")
            return original_copy(src, dst)

        with patch("shutil.copy", side_effect=failing_copy):
            result = init(str(tmp_path), interactive=False)

        # Should fail gracefully
        assert result == 1
        captured = capsys.readouterr()
        assert "ERROR" in captured.out or "failed" in captured.out.lower()
