"""Configuration loading utilities."""

from __future__ import annotations

import os
from typing import Any

import yaml


def load_config(config_path: str = ".adversarial/config.yml") -> dict[str, Any]:
    """Load configuration from YAML file with environment variable overrides."""
    # Default configuration
    config: dict[str, Any] = {
        "evaluator_model": "gpt-4o",
        "task_directory": "tasks/",
        "test_command": "pytest",
        "log_directory": ".adversarial/logs/",
        "artifacts_directory": ".adversarial/artifacts/",
    }

    # Load from file if exists
    if os.path.exists(config_path):
        with open(config_path) as f:
            file_config = yaml.safe_load(f) or {}
            if not isinstance(file_config, dict):
                raise ValueError(f"Config file must be a mapping, got {type(file_config).__name__}")
            config.update(file_config)

    # Override with environment variables
    env_overrides = {
        "ADVERSARIAL_EVALUATOR_MODEL": "evaluator_model",
        "ADVERSARIAL_TEST_COMMAND": "test_command",
        "ADVERSARIAL_LOG_DIR": "log_directory",
    }

    for env_var, config_key in env_overrides.items():
        value = os.getenv(env_var)
        if value:
            config[config_key] = value

    return config
