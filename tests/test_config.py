"""
Tests for configuration loading functionality.

Tests the load_config function which loads YAML configuration files
with defaults and environment variable overrides.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
import yaml

from adversarial_workflow.cli import load_config


class TestLoadConfig:
    """Test configuration loading with various scenarios."""

    def test_load_config_with_defaults(self):
        """Test load_config returns defaults when no config file exists."""
        with patch("os.path.exists", return_value=False):
            config = load_config("nonexistent.yml")

        # Should return default configuration
        expected_defaults = {
            "evaluator_model": "gpt-4o",
            "task_directory": "tasks/",
            "test_command": "pytest",
            "log_directory": ".adversarial/logs/",
            "artifacts_directory": ".adversarial/artifacts/",
        }
        assert config == expected_defaults

    def test_load_config_from_yaml_file(self, tmp_path):
        """Test loading configuration from YAML file."""
        # Create a test config file
        config_file = tmp_path / "test_config.yml"
        config_content = """
evaluator_model: gpt-3.5-turbo
task_directory: my_tasks/
test_command: npm test
custom_setting: test_value
"""
        config_file.write_text(config_content.strip())

        config = load_config(str(config_file))

        # Should merge defaults with file content
        assert config["evaluator_model"] == "gpt-3.5-turbo"
        assert config["task_directory"] == "my_tasks/"
        assert config["test_command"] == "npm test"
        assert config["custom_setting"] == "test_value"
        # Should still have defaults for unspecified values
        assert config["log_directory"] == ".adversarial/logs/"
        assert config["artifacts_directory"] == ".adversarial/artifacts/"

    def test_load_config_with_env_overrides(self):
        """Test that environment variables override config file values."""
        with patch("os.path.exists", return_value=False), patch.dict(
            os.environ,
            {
                "ADVERSARIAL_EVALUATOR_MODEL": "gpt-4-turbo",
                "ADVERSARIAL_TEST_COMMAND": "cargo test",
                "ADVERSARIAL_LOG_DIR": "custom_logs/",
            },
        ):
            config = load_config("nonexistent.yml")

        # Environment variables should override defaults
        assert config["evaluator_model"] == "gpt-4-turbo"
        assert config["test_command"] == "cargo test"
        assert config["log_directory"] == "custom_logs/"
        # Non-overridden values should remain default
        assert config["task_directory"] == "tasks/"

    def test_load_config_env_overrides_file(self, tmp_path):
        """Test that environment variables override file values."""
        # Create a test config file
        config_file = tmp_path / "test_config.yml"
        config_content = """
evaluator_model: gpt-3.5-turbo
test_command: pytest
"""
        config_file.write_text(config_content.strip())

        with patch.dict(
            os.environ,
            {
                "ADVERSARIAL_EVALUATOR_MODEL": "gpt-4",
                "ADVERSARIAL_TEST_COMMAND": "jest",
            },
        ):
            config = load_config(str(config_file))

        # Environment variables should override file values
        assert config["evaluator_model"] == "gpt-4"
        assert config["test_command"] == "jest"

    def test_load_config_empty_yaml_file(self, tmp_path):
        """Test loading empty YAML file returns defaults."""
        config_file = tmp_path / "empty_config.yml"
        config_file.write_text("")

        config = load_config(str(config_file))

        # Should return defaults for empty file
        expected_defaults = {
            "evaluator_model": "gpt-4o",
            "task_directory": "tasks/",
            "test_command": "pytest",
            "log_directory": ".adversarial/logs/",
            "artifacts_directory": ".adversarial/artifacts/",
        }
        assert config == expected_defaults

    def test_load_config_invalid_yaml(self, tmp_path):
        """Test loading invalid YAML file handles error gracefully."""
        config_file = tmp_path / "invalid_config.yml"
        config_file.write_text("invalid: yaml: content: [unclosed")

        # Should raise an exception or return defaults
        with pytest.raises((Exception, yaml.YAMLError)):
            load_config(str(config_file))

    def test_load_config_partial_env_overrides(self):
        """Test that only set environment variables override config."""
        with patch("os.path.exists", return_value=False), patch.dict(
            os.environ,
            {
                "ADVERSARIAL_EVALUATOR_MODEL": "gpt-4",
                # Only set one env var, others should remain default
            },
            clear=True,
        ):
            config = load_config("nonexistent.yml")

        # Only the set environment variable should be overridden
        assert config["evaluator_model"] == "gpt-4"
        assert config["test_command"] == "pytest"  # default
        assert config["log_directory"] == ".adversarial/logs/"  # default

    def test_load_config_with_sample_config(self, sample_config):
        """Test load_config with sample configuration from fixture."""
        # This tests integration with our fixtures
        assert "project_name" in sample_config
        assert "openai_api_key" in sample_config
        assert sample_config["aider_model"] == "gpt-4o"

    def test_load_config_default_path(self):
        """Test load_config with default path parameter."""
        with patch("os.path.exists", return_value=False):
            config = load_config()  # No path specified, should use default

        # Should still return defaults
        assert config["evaluator_model"] == "gpt-4o"

    @patch("builtins.open", mock_open(read_data="evaluator_model: custom-model"))
    @patch("os.path.exists", return_value=True)
    def test_load_config_file_read_error(self, mock_exists):
        """Test load_config handles file read errors."""
        with patch("builtins.open", side_effect=IOError("Permission denied")):
            with pytest.raises(IOError):
                load_config("config.yml")


class TestConfigIntegration:
    """Integration tests for configuration loading with project structure."""

    def test_load_config_in_project_directory(self, tmp_project):
        """Test loading config from project directory setup."""
        # tmp_project fixture creates .adversarial/config.yaml
        config_path = tmp_project / ".adversarial" / "config.yaml"

        config = load_config(str(config_path))

        # Should load the config created by fixture
        assert "project_name" in config
        assert config["project_name"] == "test_project"

    def test_config_priority_order(self, tmp_project):
        """Test that configuration priority order works correctly."""
        # Create config file
        config_file = tmp_project / ".adversarial" / "config.yml"
        config_content = """
evaluator_model: file-model
test_command: file-test
"""
        config_file.write_text(config_content.strip())

        # Override with environment
        with patch.dict(os.environ, {"ADVERSARIAL_EVALUATOR_MODEL": "env-model"}):
            config = load_config(str(config_file))

        # Environment should win over file
        assert config["evaluator_model"] == "env-model"
        # File should win over defaults
        assert config["test_command"] == "file-test"
        # Defaults should be used for unspecified values
        assert config["task_directory"] == "tasks/"
