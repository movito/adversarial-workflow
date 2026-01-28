"""
YAML parsing and discovery for custom evaluators.

This module handles discovering evaluator definitions from
.adversarial/evaluators/*.yml files and parsing them into
EvaluatorConfig objects.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import yaml

from .config import EvaluatorConfig

logger = logging.getLogger(__name__)


class EvaluatorParseError(Exception):
    """Raised when evaluator YAML is invalid."""


def parse_evaluator_yaml(yml_file: Path) -> EvaluatorConfig:
    """Parse a YAML file into an EvaluatorConfig.

    Args:
        yml_file: Path to the YAML file

    Returns:
        EvaluatorConfig instance

    Raises:
        EvaluatorParseError: If YAML is invalid or missing required fields
        yaml.YAMLError: If YAML syntax is invalid
    """
    # Read file with explicit UTF-8 encoding
    try:
        content = yml_file.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        raise EvaluatorParseError(f"File encoding error (not UTF-8): {yml_file}") from e

    # Parse YAML
    data = yaml.safe_load(content)

    # Check for empty YAML
    if data is None or (isinstance(data, str) and not data.strip()):
        raise EvaluatorParseError(f"Empty or invalid YAML file: {yml_file}")

    # Ensure parsed data is a dict (YAML can parse scalars, lists, etc.)
    if not isinstance(data, dict):
        raise EvaluatorParseError(
            f"YAML must be a mapping, got {type(data).__name__}: {yml_file}"
        )

    # Validate required fields exist
    required = [
        "name",
        "description",
        "model",
        "api_key_env",
        "prompt",
        "output_suffix",
    ]
    missing = [f for f in required if f not in data]
    if missing:
        raise EvaluatorParseError(f"Missing required fields: {', '.join(missing)}")

    # Validate required fields are strings (YAML can parse 'yes' as bool, '123' as int)
    for field in required:
        value = data[field]
        if not isinstance(value, str):
            raise EvaluatorParseError(
                f"Field '{field}' must be a string, got {type(value).__name__}: {value!r}"
            )

    # Validate name format (valid CLI command name)
    name = data["name"]
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", name):
        raise EvaluatorParseError(
            f"Invalid evaluator name '{name}': must start with letter, "
            "contain only letters, numbers, hyphens, underscores"
        )

    # Normalize aliases (handle None, string, or list)
    aliases = data.get("aliases")
    if aliases is None:
        data["aliases"] = []
    elif isinstance(aliases, str):
        data["aliases"] = [aliases]
    elif not isinstance(aliases, list):
        raise EvaluatorParseError(
            f"aliases must be string or list, got {type(aliases).__name__}"
        )

    # Validate alias names - must be strings with valid format
    for alias in data.get("aliases", []):
        if not isinstance(alias, str):
            raise EvaluatorParseError(
                f"Alias must be a string, got {type(alias).__name__}: {alias!r}"
            )
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", alias):
            raise EvaluatorParseError(
                f"Invalid alias '{alias}': must start with letter, "
                "contain only letters, numbers, hyphens, underscores"
            )

    # Validate prompt is non-empty
    prompt = data.get("prompt", "")
    if not prompt or not prompt.strip():
        raise EvaluatorParseError("prompt cannot be empty")

    # Validate optional string fields if present (YAML can parse '2' as int, 'yes' as bool)
    optional_string_fields = ["log_prefix", "fallback_model", "version"]
    for field in optional_string_fields:
        if field in data and data[field] is not None:
            value = data[field]
            if not isinstance(value, str):
                raise EvaluatorParseError(
                    f"Field '{field}' must be a string, got {type(value).__name__}: {value!r}"
                )

    # Validate timeout if present
    if "timeout" in data:
        timeout = data["timeout"]
        # Handle null/empty values
        if timeout is None or timeout == "":
            raise EvaluatorParseError("Field 'timeout' cannot be null or empty")
        # Check for bool before int (bool is subclass of int in Python)
        # YAML parses 'yes'/'true' as True, 'no'/'false' as False
        if isinstance(timeout, bool):
            raise EvaluatorParseError(
                f"Field 'timeout' must be an integer, got bool: {timeout!r}"
            )
        if not isinstance(timeout, int):
            raise EvaluatorParseError(
                f"Field 'timeout' must be an integer, got {type(timeout).__name__}: {timeout!r}"
            )
        # timeout=0 is invalid (does not disable timeout - use a large value instead)
        if timeout <= 0:
            raise EvaluatorParseError(
                f"Field 'timeout' must be positive (> 0), got {timeout}"
            )
        if timeout > 600:
            logger.warning(
                "Timeout %ds exceeds maximum (600s), clamping to 600s in %s",
                timeout,
                yml_file.name,
            )
            data["timeout"] = 600

    # Filter to known fields only (log unknown fields)
    known_fields = {
        "name",
        "description",
        "model",
        "api_key_env",
        "prompt",
        "output_suffix",
        "log_prefix",
        "fallback_model",
        "aliases",
        "version",
        "timeout",
    }
    unknown = set(data.keys()) - known_fields
    if unknown:
        logger.warning(
            "Unknown fields in %s: %s", yml_file.name, ", ".join(sorted(unknown))
        )

    # Build filtered data dict
    filtered_data = {k: v for k, v in data.items() if k in known_fields}

    # Create config with metadata
    config = EvaluatorConfig(
        **filtered_data,
        source="local",
        config_file=str(yml_file),
    )

    return config


def discover_local_evaluators(
    base_path: Path | None = None,
) -> dict[str, EvaluatorConfig]:
    """Discover evaluators from .adversarial/evaluators/*.yml

    Args:
        base_path: Project root (default: current directory)

    Returns:
        Dict mapping evaluator name (and aliases) to EvaluatorConfig
    """
    if base_path is None:
        base_path = Path.cwd()

    evaluators: dict[str, EvaluatorConfig] = {}
    local_dir = base_path / ".adversarial" / "evaluators"

    if not local_dir.exists():
        return evaluators

    # Get yml files with error handling for permission/access issues
    try:
        yml_files = sorted(local_dir.glob("*.yml"))
    except OSError as e:
        logger.warning("Could not read evaluators directory: %s", e)
        return evaluators

    for yml_file in yml_files:
        try:
            config = parse_evaluator_yaml(yml_file)

            # Check for name conflicts
            if config.name in evaluators:
                logger.warning(
                    "Evaluator '%s' in %s conflicts with existing; skipping",
                    config.name,
                    yml_file.name,
                )
                continue

            # Register primary name
            evaluators[config.name] = config

            # Register aliases (point to same config object)
            for alias in config.aliases:
                if alias in evaluators:
                    logger.warning(
                        "Alias '%s' conflicts with existing evaluator; skipping alias",
                        alias,
                    )
                    continue
                evaluators[alias] = config

        except EvaluatorParseError as e:
            logger.warning("Skipping %s: %s", yml_file.name, e)
        except yaml.YAMLError as e:
            logger.warning("Skipping %s: YAML syntax error: %s", yml_file.name, e)
        except OSError as e:
            logger.warning("Could not load %s: %s", yml_file.name, e)

    return evaluators
