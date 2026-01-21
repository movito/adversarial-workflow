"""Tests for EvaluatorConfig dataclass."""

import pytest

from adversarial_workflow.evaluators import EvaluatorConfig


class TestEvaluatorConfig:
    """Tests for EvaluatorConfig dataclass."""

    def test_required_fields_only(self):
        """Create config with only required fields."""
        config = EvaluatorConfig(
            name="test",
            description="Test evaluator",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            prompt="Evaluate this document",
            output_suffix="TEST-EVAL",
        )

        assert config.name == "test"
        assert config.description == "Test evaluator"
        assert config.model == "gpt-4o"
        assert config.api_key_env == "OPENAI_API_KEY"
        assert config.prompt == "Evaluate this document"
        assert config.output_suffix == "TEST-EVAL"

    def test_default_values(self):
        """Verify default values for optional fields."""
        config = EvaluatorConfig(
            name="test",
            description="Test",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            prompt="Test",
            output_suffix="TEST",
        )

        assert config.log_prefix == ""
        assert config.fallback_model is None
        assert config.aliases == []
        assert config.version == "1.0.0"
        assert config.source == "builtin"
        assert config.config_file is None

    def test_with_all_optional_fields(self):
        """Create config with all optional fields specified."""
        config = EvaluatorConfig(
            name="athena",
            description="Knowledge evaluation using Gemini 2.5 Pro",
            model="gemini-2.5-pro",
            api_key_env="GEMINI_API_KEY",
            prompt="You are Athena, a knowledge evaluation specialist...",
            output_suffix="KNOWLEDGE-EVAL",
            log_prefix="ATHENA",
            fallback_model="gpt-4o",
            aliases=["knowledge", "research"],
            version="1.0.0",
            source="local",
            config_file="/path/to/athena.yml",
        )

        assert config.name == "athena"
        assert config.log_prefix == "ATHENA"
        assert config.fallback_model == "gpt-4o"
        assert config.aliases == ["knowledge", "research"]
        assert config.source == "local"
        assert config.config_file == "/path/to/athena.yml"

    def test_aliases_not_shared_between_instances(self):
        """Verify aliases list is not shared between instances."""
        config1 = EvaluatorConfig(
            name="test1",
            description="Test 1",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            prompt="Test",
            output_suffix="TEST",
        )
        config2 = EvaluatorConfig(
            name="test2",
            description="Test 2",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            prompt="Test",
            output_suffix="TEST",
        )

        config1.aliases.append("alias1")

        assert config1.aliases == ["alias1"]
        assert config2.aliases == []  # Should NOT be affected

    def test_equality(self):
        """Two configs with same values are equal."""
        config1 = EvaluatorConfig(
            name="test",
            description="Test",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            prompt="Test",
            output_suffix="TEST",
        )
        config2 = EvaluatorConfig(
            name="test",
            description="Test",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            prompt="Test",
            output_suffix="TEST",
        )

        assert config1 == config2

    def test_inequality(self):
        """Two configs with different values are not equal."""
        config1 = EvaluatorConfig(
            name="test1",
            description="Test",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            prompt="Test",
            output_suffix="TEST",
        )
        config2 = EvaluatorConfig(
            name="test2",
            description="Test",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            prompt="Test",
            output_suffix="TEST",
        )

        assert config1 != config2
