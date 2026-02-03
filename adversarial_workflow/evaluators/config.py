"""
EvaluatorConfig dataclass for evaluator definitions.

Supports dual-field model specification (ADV-0015):
- Legacy: model + api_key_env fields (backwards compatible)
- New: model_requirement field (structured capability requirements)
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ModelRequirement:
    """Model capability requirements (from library).

    This dataclass represents structured model requirements that can be
    resolved to actual model IDs via the ModelResolver. It separates
    WHAT capability is needed from HOW to access it.

    Attributes:
        family: Model family (e.g., "claude", "gpt", "gemini", "mistral", "llama")
        tier: Performance tier (e.g., "opus", "sonnet", "haiku", "flagship", "mini")
        min_version: Optional minimum model generation (e.g., "4" for Claude 4+)
        min_context: Optional minimum context window in tokens (e.g., 128000)
    """

    family: str
    tier: str
    min_version: str = ""
    min_context: int = 0


@dataclass
class EvaluatorConfig:
    """Configuration for an evaluator (built-in or custom).

    This dataclass represents the configuration for any evaluator,
    whether built-in (evaluate, proofread, review) or custom
    (defined in .adversarial/evaluators/*.yml).

    Supports dual-field model specification (ADV-0015):
    - Legacy: model + api_key_env fields (always backwards compatible)
    - New: model_requirement field (resolved via ModelResolver)

    When both are present, model_requirement takes precedence. If resolution
    fails, falls back to legacy model field with a warning.

    Attributes:
        name: Command name (e.g., "evaluate", "athena")
        description: Help text shown in CLI
        model: Model to use (e.g., "gpt-4o", "gemini-2.5-pro") - legacy field
        api_key_env: Environment variable name for API key - legacy field
        prompt: The evaluation prompt template
        output_suffix: Log file suffix (e.g., "PLAN-EVALUATION")
        log_prefix: CLI output prefix (e.g., "ATHENA")
        fallback_model: Fallback model if primary fails
        aliases: Alternative command names
        version: Evaluator version
        timeout: Timeout in seconds (default: 180, max: 600)
        model_requirement: Structured model requirement (resolved via ModelResolver)
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
    timeout: int = 180  # Timeout in seconds (default: 180, max: 600)

    # NEW: Structured model requirement (Phase 1 - ADV-0015)
    # When present, resolved via ModelResolver to actual model ID
    model_requirement: ModelRequirement | None = None

    # Metadata (set internally during discovery, not from YAML)
    source: str = "builtin"
    config_file: str | None = None
