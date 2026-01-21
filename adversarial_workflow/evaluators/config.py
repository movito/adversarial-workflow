"""
EvaluatorConfig dataclass for evaluator definitions.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EvaluatorConfig:
    """Configuration for an evaluator (built-in or custom).

    This dataclass represents the configuration for any evaluator,
    whether built-in (evaluate, proofread, review) or custom
    (defined in .adversarial/evaluators/*.yml).

    Attributes:
        name: Command name (e.g., "evaluate", "athena")
        description: Help text shown in CLI
        model: Model to use (e.g., "gpt-4o", "gemini-2.5-pro")
        api_key_env: Environment variable name for API key
        prompt: The evaluation prompt template
        output_suffix: Log file suffix (e.g., "PLAN-EVALUATION")
        log_prefix: CLI output prefix (e.g., "ATHENA")
        fallback_model: Fallback model if primary fails
        aliases: Alternative command names
        version: Evaluator version
        source: "builtin" or "local" (set internally)
        config_file: Path to YAML file if local (set internally)
    """

    # Required fields
    name: str
    description: str
    model: str
    api_key_env: str
    prompt: str
    output_suffix: str

    # Optional fields with defaults
    log_prefix: str = ""
    fallback_model: str | None = None
    aliases: list[str] = field(default_factory=list)
    version: str = "1.0.0"

    # Metadata (set internally during discovery, not from YAML)
    source: str = "builtin"
    config_file: str | None = None
