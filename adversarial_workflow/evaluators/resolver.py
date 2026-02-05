"""
Model resolver for evaluator configurations (ADV-0015: Model Routing Layer - Phase 1).

This module provides the ModelResolver class that resolves model requirements
to actual model IDs using an embedded registry. It supports:
- model_requirement field (new structured format)
- model field (legacy string format)
- Fallback from model_requirement to model on resolution failure
"""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from adversarial_workflow.evaluators.config import EvaluatorConfig, ModelRequirement


class ResolutionError(Exception):
    """Raised when model resolution fails."""


class ModelResolver:
    """Resolves model requirements to actual model IDs.

    Uses an embedded registry (matching adversarial-evaluator-library/providers/registry.yml)
    to map family/tier pairs to concrete model identifiers.

    Resolution order:
    1. If model_requirement present: resolve via registry
    2. If resolution fails AND model present: warn + fallback to legacy
    3. If resolution fails AND no model: raise ResolutionError
    4. If no model_requirement AND model present: use legacy directly
    5. If neither: raise ResolutionError
    """

    # Default registry - matches adversarial-evaluator-library/providers/registry.yml
    # Updated 2026-02-03 per Library team handoff (ADR-0005)
    DEFAULT_REGISTRY: ClassVar[dict[str, dict[str, dict[str, list[str] | str]]]] = {
        "claude": {
            "opus": {
                "models": ["claude-4-opus-20260115", "claude-opus-4-5-20251101"],
                "prefix": "anthropic/",
            },
            "sonnet": {
                "models": ["claude-4-sonnet-20260115"],
                "prefix": "anthropic/",
            },
            "haiku": {
                "models": ["claude-4-haiku-20260115"],
                "prefix": "anthropic/",
            },
        },
        "gpt": {
            "flagship": {
                "models": ["gpt-4o", "gpt-4o-2024-08-06"],
                "prefix": "",
            },
            "standard": {
                "models": ["gpt-4-turbo", "gpt-4"],
                "prefix": "",
            },
            "mini": {
                "models": ["gpt-4o-mini"],
                "prefix": "",
            },
        },
        "o": {
            "flagship": {
                "models": ["o1", "o1-2024-12-17"],
                "prefix": "",
            },
            "mini": {
                "models": ["o3-mini"],
                "prefix": "",
            },
        },
        "gemini": {
            "pro": {
                "models": ["gemini-2.5-pro"],
                "prefix": "gemini/",
            },
            "flash": {
                "models": ["gemini-2.5-flash"],
                "prefix": "gemini/",
            },
        },
        "mistral": {
            "large": {
                "models": ["mistral-large-latest"],
                "prefix": "mistral/",
            },
            "small": {
                "models": ["mistral-small-latest"],
                "prefix": "mistral/",
            },
        },
        "codestral": {
            "latest": {
                "models": ["codestral-latest"],
                "prefix": "mistral/",
            },
        },
        "llama": {
            "large": {
                "models": ["llama-3.3-70b"],
                "prefix": "",  # varies by host
            },
            "medium": {
                "models": ["llama-3.1-8b"],
                "prefix": "",
            },
        },
    }

    # API key environment variable mapping by family
    API_KEY_MAP: ClassVar[dict[str, str]] = {
        "claude": "ANTHROPIC_API_KEY",
        "gpt": "OPENAI_API_KEY",
        "o": "OPENAI_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "mistral": "MISTRAL_API_KEY",
        "codestral": "MISTRAL_API_KEY",
        "llama": "TOGETHER_API_KEY",
    }

    def resolve(self, config: EvaluatorConfig) -> tuple[str, str]:
        """Resolve evaluator config to (model_id, api_key_env).

        Args:
            config: EvaluatorConfig with model and/or model_requirement

        Returns:
            (model_id, api_key_env) tuple

        Raises:
            ResolutionError: If resolution fails and no fallback available
        """
        if config.model_requirement:
            try:
                return self._resolve_requirement(config.model_requirement)
            except ResolutionError as e:
                if config.model:
                    # Fall back to legacy with warning
                    warnings.warn(
                        f"model_requirement resolution failed for {config.name}: {e}. "
                        f"Falling back to legacy model field: {config.model}",
                        UserWarning,
                        stacklevel=2,
                    )
                    return (config.model, config.api_key_env)
                raise

        # Legacy only
        if config.model:
            return (config.model, config.api_key_env)

        raise ResolutionError("No model or model_requirement specified")

    def _resolve_requirement(self, req: ModelRequirement) -> tuple[str, str]:
        """Resolve requirement to model ID using registry.

        Args:
            req: ModelRequirement with family and tier

        Returns:
            (model_id, api_key_env) tuple

        Raises:
            ResolutionError: If family or tier not found in registry
        """
        # TODO(Phase 2): ModelRequirement.min_version and ModelRequirement.min_context
        # are currently parsed but not used for filtering. Phase 1 only performs
        # family/tier matching. Phase 2 will implement filtering by min_version
        # and min_context requirements.
        family = self.DEFAULT_REGISTRY.get(req.family)
        if not family:
            raise ResolutionError(f"Unknown model family: {req.family}")

        tier_data = family.get(req.tier)
        if not tier_data:
            raise ResolutionError(f"Unknown tier '{req.tier}' for family '{req.family}'")

        # Return first (latest) model in tier
        models = tier_data.get("models", [])
        if not models:
            raise ResolutionError(f"No models defined for {req.family}/{req.tier}")
        # Registry type is list[str] | str for flexibility; actual values are always lists
        model_id = models[0]  # type: ignore[index]

        # Apply provider prefix for LiteLLM compatibility
        prefix = tier_data.get("prefix", "")
        if prefix:
            model_id = f"{prefix}{model_id}"

        # Determine API key env from family
        api_key_env = self._get_api_key_env(req.family)

        return (model_id, api_key_env)

    def _get_api_key_env(self, family: str) -> str:
        """Get default API key environment variable for family.

        Args:
            family: Model family name

        Returns:
            Environment variable name for API key
        """
        return self.API_KEY_MAP.get(family, f"{family.upper()}_API_KEY")
