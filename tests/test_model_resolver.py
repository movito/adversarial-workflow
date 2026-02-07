"""Tests for model resolution (ADV-0015: Model Routing Layer - Phase 1).

This module tests:
1. ModelRequirement dataclass
2. ModelResolver resolution logic
3. Fallback behavior
4. Error handling
"""

import pytest

from adversarial_workflow.evaluators.config import EvaluatorConfig, ModelRequirement
from adversarial_workflow.evaluators.resolver import ModelResolver, ResolutionError


class TestModelRequirement:
    """Tests for ModelRequirement dataclass."""

    def test_model_requirement_required_fields(self):
        """ModelRequirement stores family and tier."""
        req = ModelRequirement(family="claude", tier="opus")
        assert req.family == "claude"
        assert req.tier == "opus"

    def test_model_requirement_default_values(self):
        """ModelRequirement has sensible defaults for optional fields."""
        req = ModelRequirement(family="claude", tier="opus")
        assert req.min_version == ""
        assert req.min_context == 0

    def test_model_requirement_with_all_fields(self):
        """ModelRequirement accepts all optional fields."""
        req = ModelRequirement(
            family="claude",
            tier="opus",
            min_version="4",
            min_context=128000,
        )
        assert req.family == "claude"
        assert req.tier == "opus"
        assert req.min_version == "4"
        assert req.min_context == 128000


class TestEvaluatorConfigWithModelRequirement:
    """Tests for EvaluatorConfig with model_requirement field."""

    def test_evaluator_config_without_model_requirement(self):
        """EvaluatorConfig works without model_requirement (backwards compat)."""
        config = EvaluatorConfig(
            name="test",
            description="Test evaluator",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            prompt="Test prompt",
            output_suffix="TEST",
        )
        assert config.model_requirement is None
        assert config.model == "gpt-4o"

    def test_evaluator_config_with_model_requirement(self):
        """EvaluatorConfig accepts optional model_requirement."""
        req = ModelRequirement(family="claude", tier="opus")
        config = EvaluatorConfig(
            name="test",
            description="Test evaluator",
            model="",
            api_key_env="",
            prompt="Test prompt",
            output_suffix="TEST",
            model_requirement=req,
        )
        assert config.model_requirement is not None
        assert config.model_requirement.family == "claude"
        assert config.model_requirement.tier == "opus"

    def test_evaluator_config_with_both_fields(self):
        """EvaluatorConfig can have both model and model_requirement (dual-field)."""
        req = ModelRequirement(family="claude", tier="opus")
        config = EvaluatorConfig(
            name="test",
            description="Test evaluator",
            model="claude-4-opus-20260115",
            api_key_env="ANTHROPIC_API_KEY",
            prompt="Test prompt",
            output_suffix="TEST",
            model_requirement=req,
        )
        assert config.model == "claude-4-opus-20260115"
        assert config.model_requirement is not None


class TestModelResolverRegistryResolution:
    """Tests for ModelResolver registry-based resolution."""

    def test_resolve_claude_opus(self):
        """Resolver maps claude/opus to correct model ID."""
        config = EvaluatorConfig(
            name="test",
            description="Test",
            model="",
            api_key_env="",
            prompt="Test",
            output_suffix="TEST",
            model_requirement=ModelRequirement(family="claude", tier="opus"),
        )
        resolver = ModelResolver()
        model_id, api_key_env = resolver.resolve(config)
        assert "claude" in model_id.lower()
        assert "opus" in model_id.lower()
        assert api_key_env == "ANTHROPIC_API_KEY"

    def test_resolve_claude_sonnet(self):
        """Resolver maps claude/sonnet to correct model ID."""
        config = EvaluatorConfig(
            name="test",
            description="Test",
            model="",
            api_key_env="",
            prompt="Test",
            output_suffix="TEST",
            model_requirement=ModelRequirement(family="claude", tier="sonnet"),
        )
        resolver = ModelResolver()
        model_id, api_key_env = resolver.resolve(config)
        assert "claude" in model_id.lower()
        assert "sonnet" in model_id.lower()
        assert api_key_env == "ANTHROPIC_API_KEY"

    def test_resolve_claude_haiku(self):
        """Resolver maps claude/haiku to correct model ID."""
        config = EvaluatorConfig(
            name="test",
            description="Test",
            model="",
            api_key_env="",
            prompt="Test",
            output_suffix="TEST",
            model_requirement=ModelRequirement(family="claude", tier="haiku"),
        )
        resolver = ModelResolver()
        model_id, api_key_env = resolver.resolve(config)
        assert "claude" in model_id.lower()
        assert "haiku" in model_id.lower()
        assert api_key_env == "ANTHROPIC_API_KEY"

    def test_resolve_gpt_flagship(self):
        """Resolver maps gpt/flagship to gpt-4o."""
        config = EvaluatorConfig(
            name="test",
            description="Test",
            model="",
            api_key_env="",
            prompt="Test",
            output_suffix="TEST",
            model_requirement=ModelRequirement(family="gpt", tier="flagship"),
        )
        resolver = ModelResolver()
        model_id, api_key_env = resolver.resolve(config)
        assert "gpt-4o" in model_id
        assert api_key_env == "OPENAI_API_KEY"

    def test_resolve_gpt_mini(self):
        """Resolver maps gpt/mini to gpt-4o-mini."""
        config = EvaluatorConfig(
            name="test",
            description="Test",
            model="",
            api_key_env="",
            prompt="Test",
            output_suffix="TEST",
            model_requirement=ModelRequirement(family="gpt", tier="mini"),
        )
        resolver = ModelResolver()
        model_id, api_key_env = resolver.resolve(config)
        assert "gpt-4o-mini" in model_id
        assert api_key_env == "OPENAI_API_KEY"

    def test_resolve_o_flagship(self):
        """Resolver maps o/flagship to o1."""
        config = EvaluatorConfig(
            name="test",
            description="Test",
            model="",
            api_key_env="",
            prompt="Test",
            output_suffix="TEST",
            model_requirement=ModelRequirement(family="o", tier="flagship"),
        )
        resolver = ModelResolver()
        model_id, api_key_env = resolver.resolve(config)
        assert model_id == "o1"
        assert api_key_env == "OPENAI_API_KEY"

    def test_resolve_gemini_pro(self):
        """Resolver maps gemini/pro to gemini-2.5-pro."""
        config = EvaluatorConfig(
            name="test",
            description="Test",
            model="",
            api_key_env="",
            prompt="Test",
            output_suffix="TEST",
            model_requirement=ModelRequirement(family="gemini", tier="pro"),
        )
        resolver = ModelResolver()
        model_id, api_key_env = resolver.resolve(config)
        assert "gemini" in model_id
        assert "pro" in model_id
        assert api_key_env == "GEMINI_API_KEY"

    def test_resolve_gemini_flash(self):
        """Resolver maps gemini/flash to gemini-2.5-flash."""
        config = EvaluatorConfig(
            name="test",
            description="Test",
            model="",
            api_key_env="",
            prompt="Test",
            output_suffix="TEST",
            model_requirement=ModelRequirement(family="gemini", tier="flash"),
        )
        resolver = ModelResolver()
        model_id, api_key_env = resolver.resolve(config)
        assert "gemini" in model_id
        assert "flash" in model_id
        assert api_key_env == "GEMINI_API_KEY"

    def test_resolve_mistral_large(self):
        """Resolver maps mistral/large to mistral-large-latest."""
        config = EvaluatorConfig(
            name="test",
            description="Test",
            model="",
            api_key_env="",
            prompt="Test",
            output_suffix="TEST",
            model_requirement=ModelRequirement(family="mistral", tier="large"),
        )
        resolver = ModelResolver()
        model_id, api_key_env = resolver.resolve(config)
        assert "mistral" in model_id
        assert "large" in model_id
        assert api_key_env == "MISTRAL_API_KEY"

    def test_resolve_codestral(self):
        """Resolver maps codestral/latest to codestral-latest."""
        config = EvaluatorConfig(
            name="test",
            description="Test",
            model="",
            api_key_env="",
            prompt="Test",
            output_suffix="TEST",
            model_requirement=ModelRequirement(family="codestral", tier="latest"),
        )
        resolver = ModelResolver()
        model_id, api_key_env = resolver.resolve(config)
        assert "codestral" in model_id
        assert api_key_env == "MISTRAL_API_KEY"

    def test_resolve_llama_large(self):
        """Resolver maps llama/large to llama model."""
        config = EvaluatorConfig(
            name="test",
            description="Test",
            model="",
            api_key_env="",
            prompt="Test",
            output_suffix="TEST",
            model_requirement=ModelRequirement(family="llama", tier="large"),
        )
        resolver = ModelResolver()
        model_id, api_key_env = resolver.resolve(config)
        assert "llama" in model_id
        assert api_key_env == "TOGETHER_API_KEY"


class TestModelResolverLegacyFallback:
    """Tests for ModelResolver legacy model field support."""

    def test_resolve_legacy_model_field(self):
        """Resolver uses legacy model field when model_requirement absent."""
        config = EvaluatorConfig(
            name="test",
            description="Test",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            prompt="Test",
            output_suffix="TEST",
        )
        resolver = ModelResolver()
        model_id, api_key_env = resolver.resolve(config)
        assert model_id == "gpt-4o"
        assert api_key_env == "OPENAI_API_KEY"

    def test_model_used_directly_with_unknown_family(self):
        """Resolver uses model directly when model present (ignores unknown requirement)."""
        config = EvaluatorConfig(
            name="test",
            description="Test",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            prompt="Test",
            output_suffix="TEST",
            model_requirement=ModelRequirement(family="unknown", tier="unknown"),
        )
        resolver = ModelResolver()
        # No warning - model field takes priority, requirement ignored
        model_id, api_key_env = resolver.resolve(config)
        assert model_id == "gpt-4o"
        assert api_key_env == "OPENAI_API_KEY"

    def test_model_used_directly_with_unknown_tier(self):
        """Resolver uses model directly when model present (ignores unknown tier)."""
        config = EvaluatorConfig(
            name="test",
            description="Test",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            prompt="Test",
            output_suffix="TEST",
            model_requirement=ModelRequirement(family="claude", tier="unknown"),
        )
        resolver = ModelResolver()
        # No warning - model field takes priority, requirement ignored
        model_id, api_key_env = resolver.resolve(config)
        assert model_id == "gpt-4o"
        assert api_key_env == "OPENAI_API_KEY"

    def test_model_field_takes_priority_over_requirement(self):
        """Explicit model field takes priority over model_requirement (ADV-0032)."""
        config = EvaluatorConfig(
            name="priority-test",
            description="Test model priority",
            model="claude-opus-4-6",  # Explicit - should win
            api_key_env="ANTHROPIC_API_KEY",
            prompt="Test",
            output_suffix="TEST",
            model_requirement=ModelRequirement(
                family="claude",
                tier="opus",
            ),  # Would resolve to old ID - should be ignored
        )
        resolver = ModelResolver()
        model_id, api_key_env = resolver.resolve(config)

        # Explicit model wins
        assert model_id == "claude-opus-4-6"
        assert api_key_env == "ANTHROPIC_API_KEY"
        # No prefix added (registry not used)
        assert "anthropic/" not in model_id


class TestModelResolverErrorHandling:
    """Tests for ModelResolver error handling."""

    def test_resolve_error_when_no_model_or_requirement(self):
        """Resolver raises when neither model nor model_requirement present."""
        config = EvaluatorConfig(
            name="test",
            description="Test",
            model="",
            api_key_env="",
            prompt="Test",
            output_suffix="TEST",
        )
        resolver = ModelResolver()
        with pytest.raises(ResolutionError, match="No model or model_requirement"):
            resolver.resolve(config)

    def test_resolve_error_on_unknown_family_no_fallback(self):
        """Resolver raises when family unknown and no fallback available."""
        config = EvaluatorConfig(
            name="test",
            description="Test",
            model="",  # no fallback
            api_key_env="",
            prompt="Test",
            output_suffix="TEST",
            model_requirement=ModelRequirement(family="unknown", tier="unknown"),
        )
        resolver = ModelResolver()
        with pytest.raises(ResolutionError, match="Unknown model family"):
            resolver.resolve(config)

    def test_resolve_error_on_unknown_tier_no_fallback(self):
        """Resolver raises when tier unknown and no fallback available."""
        config = EvaluatorConfig(
            name="test",
            description="Test",
            model="",  # no fallback
            api_key_env="",
            prompt="Test",
            output_suffix="TEST",
            model_requirement=ModelRequirement(family="claude", tier="unknown"),
        )
        resolver = ModelResolver()
        with pytest.raises(ResolutionError, match="Unknown tier"):
            resolver.resolve(config)

    def test_error_message_includes_family_name(self):
        """Error message includes the unknown family name."""
        config = EvaluatorConfig(
            name="test",
            description="Test",
            model="",
            api_key_env="",
            prompt="Test",
            output_suffix="TEST",
            model_requirement=ModelRequirement(family="nonexistent", tier="tier"),
        )
        resolver = ModelResolver()
        with pytest.raises(ResolutionError, match="nonexistent"):
            resolver.resolve(config)

    def test_error_message_includes_tier_name(self):
        """Error message includes the unknown tier name."""
        config = EvaluatorConfig(
            name="test",
            description="Test",
            model="",
            api_key_env="",
            prompt="Test",
            output_suffix="TEST",
            model_requirement=ModelRequirement(family="claude", tier="nonexistent"),
        )
        resolver = ModelResolver()
        with pytest.raises(ResolutionError, match="nonexistent"):
            resolver.resolve(config)
