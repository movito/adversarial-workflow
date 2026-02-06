"""
YAML parsing and discovery for custom evaluators.

This module handles discovering evaluator definitions from
.adversarial/evaluators/*.yml files and parsing them into
EvaluatorConfig objects.

Supports dual-field model specification (ADV-0015):
- Legacy: model + api_key_env fields (backwards compatible)
- New: model_requirement field (resolved via ModelResolver)
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import yaml

from .config import EvaluatorConfig, ModelRequirement

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
        raise EvaluatorParseError(f"YAML must be a mapping, got {type(data).__name__}: {yml_file}")

    # Validate required fields exist
    # model and api_key_env are only required if model_requirement is not present
    always_required = [
        "name",
        "description",
        "prompt",
        "output_suffix",
    ]
    has_model_requirement = "model_requirement" in data
    if not has_model_requirement:
        # Legacy format: model and api_key_env are required
        always_required.extend(["model", "api_key_env"])

    missing = [f for f in always_required if f not in data]
    if missing:
        raise EvaluatorParseError(f"Missing required fields: {', '.join(missing)}")

    # Validate required fields are strings (YAML can parse 'yes' as bool, '123' as int)
    for field in always_required:
        value = data[field]
        if not isinstance(value, str):
            raise EvaluatorParseError(
                f"Field '{field}' must be a string, got {type(value).__name__}: {value!r}"
            )

    # Validate model and api_key_env are strings if present (even when optional)
    for field in ["model", "api_key_env"]:
        if field in data and data[field] is not None:
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
        raise EvaluatorParseError(f"aliases must be string or list, got {type(aliases).__name__}")

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
            raise EvaluatorParseError(f"Field 'timeout' must be an integer, got bool: {timeout!r}")
        if not isinstance(timeout, int):
            raise EvaluatorParseError(
                f"Field 'timeout' must be an integer, got {type(timeout).__name__}: {timeout!r}"
            )
        # timeout=0 is invalid (does not disable timeout - use a large value instead)
        if timeout <= 0:
            raise EvaluatorParseError(f"Field 'timeout' must be positive (> 0), got {timeout}")
        if timeout > 600:
            logger.warning(
                "Timeout %ds exceeds maximum (600s), clamping to 600s in %s",
                timeout,
                yml_file.name,
            )
            data["timeout"] = 600

    # Parse model_requirement if present (ADV-0015)
    model_requirement = None
    if "model_requirement" in data:
        req_data = data["model_requirement"]

        # Validate model_requirement is a mapping
        if not isinstance(req_data, dict):
            raise EvaluatorParseError(
                f"model_requirement must be a mapping, got {type(req_data).__name__}"
            )

        # Validate required fields in model_requirement
        if "family" not in req_data:
            raise EvaluatorParseError("model_requirement.family is required")
        if "tier" not in req_data:
            raise EvaluatorParseError("model_requirement.tier is required")

        # Validate family and tier are strings
        family = req_data["family"]
        tier = req_data["tier"]
        if not isinstance(family, str):
            raise EvaluatorParseError(
                f"model_requirement.family must be a string, got {type(family).__name__}"
            )
        if not isinstance(tier, str):
            raise EvaluatorParseError(
                f"model_requirement.tier must be a string, got {type(tier).__name__}"
            )

        # Validate optional min_version is string if present
        min_version = req_data.get("min_version", "")
        # Reject booleans explicitly (YAML parses 'yes'/'no'/'true'/'false' as bool)
        if isinstance(min_version, bool):
            raise EvaluatorParseError(
                f"model_requirement.min_version must be a string, got bool: {min_version!r}"
            )
        # Convert integers to strings (YAML parses '0' as int 0)
        if isinstance(min_version, int):
            min_version = str(min_version)
        elif min_version and not isinstance(min_version, str):
            raise EvaluatorParseError(
                f"model_requirement.min_version must be a string, got {type(min_version).__name__}"
            )

        # Validate optional min_context is integer if present
        min_context = req_data.get("min_context", 0)
        # Reject booleans explicitly (YAML parses 'yes'/'no'/'true'/'false' as bool)
        if isinstance(min_context, bool):
            raise EvaluatorParseError("model_requirement.min_context must be an integer, got bool")
        if min_context and not isinstance(min_context, int):
            raise EvaluatorParseError(
                f"model_requirement.min_context must be an integer, got {type(min_context).__name__}"
            )

        model_requirement = ModelRequirement(
            family=family,
            tier=tier,
            min_version=min_version,
            min_context=min_context,
        )

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
        "model_requirement",  # ADV-0015
    }
    unknown = set(data.keys()) - known_fields
    # Ignore underscore-prefixed metadata fields (e.g., _meta from library install)
    unknown = {f for f in unknown if not f.startswith("_")}
    if unknown:
        logger.warning("Unknown fields in %s: %s", yml_file.name, ", ".join(sorted(unknown)))

    # Build filtered data dict (exclude model_requirement as it's handled separately)
    scalar_fields = known_fields - {"model_requirement"}
    filtered_data = {k: v for k, v in data.items() if k in scalar_fields}

    # Set defaults for optional model/api_key_env when model_requirement is present
    # Also handle explicit null values (YAML parses empty or null as None)
    if "model" not in filtered_data or filtered_data["model"] is None:
        filtered_data["model"] = ""
    if "api_key_env" not in filtered_data or filtered_data["api_key_env"] is None:
        filtered_data["api_key_env"] = ""

    # Create config with metadata and model_requirement
    config = EvaluatorConfig(
        **filtered_data,
        model_requirement=model_requirement,
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
