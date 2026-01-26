"""Tests for evaluator YAML parsing and discovery."""

import pytest

from adversarial_workflow.evaluators import (
    EvaluatorParseError,
    discover_local_evaluators,
    parse_evaluator_yaml,
)


class TestParseEvaluatorYaml:
    """Tests for parse_evaluator_yaml function."""

    def test_parse_valid_yaml(self, tmp_path):
        """Parse a valid evaluator YAML with all required fields."""
        yml = tmp_path / "test.yml"
        yml.write_text(
            """
name: test
description: Test evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Evaluate this document
output_suffix: TEST-EVAL
"""
        )
        config = parse_evaluator_yaml(yml)

        assert config.name == "test"
        assert config.description == "Test evaluator"
        assert config.model == "gpt-4o"
        assert config.api_key_env == "OPENAI_API_KEY"
        assert config.prompt == "Evaluate this document"
        assert config.output_suffix == "TEST-EVAL"
        assert config.source == "local"
        assert config.config_file == str(yml)

    def test_parse_with_optional_fields(self, tmp_path):
        """Parse YAML with all optional fields specified."""
        yml = tmp_path / "athena.yml"
        yml.write_text(
            """
name: athena
description: Knowledge evaluation
model: gemini-2.5-pro
api_key_env: GEMINI_API_KEY
prompt: You are Athena
output_suffix: KNOWLEDGE-EVAL
log_prefix: ATHENA
fallback_model: gpt-4o
version: 2.0.0
aliases:
  - knowledge
  - research
"""
        )
        config = parse_evaluator_yaml(yml)

        assert config.name == "athena"
        assert config.log_prefix == "ATHENA"
        assert config.fallback_model == "gpt-4o"
        assert config.version == "2.0.0"
        assert config.aliases == ["knowledge", "research"]

    def test_parse_missing_required_field(self, tmp_path):
        """Error on missing required field."""
        yml = tmp_path / "invalid.yml"
        yml.write_text("name: test\ndescription: Test\n")

        with pytest.raises(EvaluatorParseError, match="Missing required fields"):
            parse_evaluator_yaml(yml)

    def test_parse_invalid_name_starts_with_number(self, tmp_path):
        """Error on name starting with number."""
        yml = tmp_path / "bad-name.yml"
        yml.write_text(
            """
name: 123-invalid
description: Bad name
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test
output_suffix: TEST
"""
        )

        with pytest.raises(EvaluatorParseError, match="Invalid evaluator name"):
            parse_evaluator_yaml(yml)

    def test_parse_invalid_name_special_chars(self, tmp_path):
        """Error on name with invalid special characters."""
        yml = tmp_path / "bad-name.yml"
        yml.write_text(
            """
name: test@invalid
description: Bad name
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test
output_suffix: TEST
"""
        )

        with pytest.raises(EvaluatorParseError, match="Invalid evaluator name"):
            parse_evaluator_yaml(yml)

    def test_parse_invalid_alias(self, tmp_path):
        """Error on invalid alias name."""
        yml = tmp_path / "bad-alias.yml"
        yml.write_text(
            """
name: valid
description: Valid name but bad alias
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test
output_suffix: TEST
aliases:
  - 123-bad
"""
        )

        with pytest.raises(EvaluatorParseError, match="Invalid alias"):
            parse_evaluator_yaml(yml)

    def test_parse_empty_prompt(self, tmp_path):
        """Error on empty prompt."""
        yml = tmp_path / "empty-prompt.yml"
        yml.write_text(
            """
name: test
description: Test
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: ""
output_suffix: TEST
"""
        )

        with pytest.raises(EvaluatorParseError, match="prompt cannot be empty"):
            parse_evaluator_yaml(yml)

    def test_parse_whitespace_prompt(self, tmp_path):
        """Error on whitespace-only prompt."""
        yml = tmp_path / "whitespace-prompt.yml"
        yml.write_text(
            """
name: test
description: Test
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: "   "
output_suffix: TEST
"""
        )

        with pytest.raises(EvaluatorParseError, match="prompt cannot be empty"):
            parse_evaluator_yaml(yml)

    def test_parse_encoding_error(self, tmp_path):
        """Error on non-UTF-8 file."""
        yml = tmp_path / "bad-encoding.yml"
        yml.write_bytes(b"\xff\xfe" + "name: test".encode("utf-16-le"))

        with pytest.raises(EvaluatorParseError, match="encoding error"):
            parse_evaluator_yaml(yml)

    def test_parse_empty_yaml(self, tmp_path):
        """Error on empty YAML file."""
        yml = tmp_path / "empty.yml"
        yml.write_text("")

        with pytest.raises(EvaluatorParseError, match="Empty or invalid"):
            parse_evaluator_yaml(yml)

    def test_parse_whitespace_only_yaml(self, tmp_path):
        """Error on whitespace-only YAML file."""
        yml = tmp_path / "whitespace.yml"
        yml.write_text("   \n   \n")

        with pytest.raises(EvaluatorParseError, match="Empty or invalid"):
            parse_evaluator_yaml(yml)

    def test_parse_aliases_as_string(self, tmp_path):
        """Single alias as string converts to list."""
        yml = tmp_path / "test.yml"
        yml.write_text(
            """
name: test
description: Test
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: TEST
aliases: alt_name
"""
        )
        config = parse_evaluator_yaml(yml)

        assert config.aliases == ["alt_name"]

    def test_parse_aliases_as_list(self, tmp_path):
        """Multiple aliases as list."""
        yml = tmp_path / "test.yml"
        yml.write_text(
            """
name: test
description: Test
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: TEST
aliases:
  - alt1
  - alt2
"""
        )
        config = parse_evaluator_yaml(yml)

        assert config.aliases == ["alt1", "alt2"]

    def test_parse_aliases_none(self, tmp_path):
        """Missing aliases defaults to empty list."""
        yml = tmp_path / "test.yml"
        yml.write_text(
            """
name: test
description: Test
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: TEST
"""
        )
        config = parse_evaluator_yaml(yml)

        assert config.aliases == []

    def test_parse_unknown_fields_logged(self, tmp_path, caplog):
        """Unknown fields are logged as warnings but don't cause failure."""
        yml = tmp_path / "test.yml"
        yml.write_text(
            """
name: test
description: Test
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: TEST
unknown_field: some value
another_unknown: 123
"""
        )

        import logging

        with caplog.at_level(logging.WARNING):
            config = parse_evaluator_yaml(yml)

        assert config.name == "test"
        assert "Unknown fields" in caplog.text
        assert "unknown_field" in caplog.text

    def test_parse_non_string_required_field(self, tmp_path):
        """Error when required field is not a string (YAML parses 'yes' as bool)."""
        yml = tmp_path / "bad-type.yml"
        yml.write_text(
            """
name: test
description: Test
model: gpt-4o
api_key_env: yes
prompt: Test prompt
output_suffix: TEST
"""
        )

        with pytest.raises(EvaluatorParseError, match="must be a string"):
            parse_evaluator_yaml(yml)

    def test_parse_integer_required_field(self, tmp_path):
        """Error when required field is an integer."""
        yml = tmp_path / "int-field.yml"
        yml.write_text(
            """
name: test
description: 123
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: TEST
"""
        )

        with pytest.raises(EvaluatorParseError, match="must be a string"):
            parse_evaluator_yaml(yml)

    def test_parse_non_string_alias(self, tmp_path):
        """Error when alias is not a string (e.g., integer)."""
        yml = tmp_path / "int-alias.yml"
        yml.write_text(
            """
name: test
description: Test
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: TEST
aliases:
  - 123
"""
        )

        with pytest.raises(EvaluatorParseError, match="Alias must be a string"):
            parse_evaluator_yaml(yml)

    def test_parse_boolean_alias(self, tmp_path):
        """Error when alias is a boolean (YAML parses 'yes' as True)."""
        yml = tmp_path / "bool-alias.yml"
        yml.write_text(
            """
name: test
description: Test
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: TEST
aliases:
  - yes
"""
        )

        with pytest.raises(EvaluatorParseError, match="Alias must be a string"):
            parse_evaluator_yaml(yml)

    def test_parse_yaml_list_not_mapping(self, tmp_path):
        """Error when YAML is a list instead of mapping."""
        yml = tmp_path / "list.yml"
        yml.write_text(
            """
- item1
- item2
"""
        )

        with pytest.raises(EvaluatorParseError, match="must be a mapping"):
            parse_evaluator_yaml(yml)

    def test_parse_yaml_scalar_not_mapping(self, tmp_path):
        """Error when YAML is a scalar instead of mapping."""
        yml = tmp_path / "scalar.yml"
        yml.write_text("just a string value")

        with pytest.raises(EvaluatorParseError, match="must be a mapping"):
            parse_evaluator_yaml(yml)

    def test_parse_optional_field_wrong_type(self, tmp_path):
        """Error when optional field has wrong type (version as int)."""
        yml = tmp_path / "bad-version.yml"
        yml.write_text(
            """
name: test
description: Test
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: TEST
version: 2
"""
        )

        with pytest.raises(EvaluatorParseError, match="'version' must be a string"):
            parse_evaluator_yaml(yml)

    def test_parse_fallback_model_wrong_type(self, tmp_path):
        """Error when fallback_model is boolean (YAML 'yes' -> True)."""
        yml = tmp_path / "bad-fallback.yml"
        yml.write_text(
            """
name: test
description: Test
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: TEST
fallback_model: yes
"""
        )

        with pytest.raises(
            EvaluatorParseError, match="'fallback_model' must be a string"
        ):
            parse_evaluator_yaml(yml)


class TestDiscoverLocalEvaluators:
    """Tests for discover_local_evaluators function."""

    def test_discover_no_directory(self, tmp_path):
        """Empty dict when no .adversarial/evaluators directory."""
        result = discover_local_evaluators(tmp_path)

        assert result == {}

    def test_discover_empty_directory(self, tmp_path):
        """Empty dict when evaluators directory is empty."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)

        result = discover_local_evaluators(tmp_path)

        assert result == {}

    def test_discover_single_evaluator(self, tmp_path):
        """Discover a single evaluator."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "test.yml").write_text(
            """
name: test
description: Test evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test prompt
output_suffix: TEST-EVAL
"""
        )

        result = discover_local_evaluators(tmp_path)

        assert "test" in result
        assert result["test"].name == "test"
        assert result["test"].source == "local"

    def test_discover_multiple_evaluators(self, tmp_path):
        """Discover multiple evaluators."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)

        (eval_dir / "alpha.yml").write_text(
            """
name: alpha
description: Alpha evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Alpha prompt
output_suffix: ALPHA-EVAL
"""
        )
        (eval_dir / "beta.yml").write_text(
            """
name: beta
description: Beta evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Beta prompt
output_suffix: BETA-EVAL
"""
        )

        result = discover_local_evaluators(tmp_path)

        assert len(result) == 2
        assert "alpha" in result
        assert "beta" in result

    def test_discover_evaluator_with_aliases(self, tmp_path):
        """Discover evaluator with aliases - aliases map to same config."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "athena.yml").write_text(
            """
name: athena
description: Knowledge eval
model: gemini-2.5-pro
api_key_env: GEMINI_API_KEY
prompt: You are Athena
output_suffix: KNOWLEDGE-EVAL
aliases:
  - knowledge
  - research
"""
        )

        result = discover_local_evaluators(tmp_path)

        assert "athena" in result
        assert "knowledge" in result
        assert "research" in result
        # All point to same config object
        assert result["athena"] is result["knowledge"]
        assert result["athena"] is result["research"]

    def test_discover_skips_invalid_yaml(self, tmp_path, caplog):
        """Invalid YAML files are skipped with warning."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "bad.yml").write_text("name: incomplete\n")
        (eval_dir / "good.yml").write_text(
            """
name: good
description: Good evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Good prompt
output_suffix: GOOD-EVAL
"""
        )

        import logging

        with caplog.at_level(logging.WARNING):
            result = discover_local_evaluators(tmp_path)

        assert "good" in result
        assert "incomplete" not in result
        assert "Skipping bad.yml" in caplog.text

    def test_discover_name_conflict_first_wins(self, tmp_path, caplog):
        """First evaluator wins on name conflict (sorted order)."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)

        # 'aaa.yml' comes before 'zzz.yml' in sorted order
        (eval_dir / "aaa.yml").write_text(
            """
name: duplicate
description: First one
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: First prompt
output_suffix: FIRST
"""
        )
        (eval_dir / "zzz.yml").write_text(
            """
name: duplicate
description: Second one
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Second prompt
output_suffix: SECOND
"""
        )

        import logging

        with caplog.at_level(logging.WARNING):
            result = discover_local_evaluators(tmp_path)

        assert result["duplicate"].description == "First one"
        assert "conflicts with existing" in caplog.text

    def test_discover_alias_conflict_skipped(self, tmp_path, caplog):
        """Alias conflicting with existing name is skipped."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)

        (eval_dir / "aaa.yml").write_text(
            """
name: first
description: First evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: First prompt
output_suffix: FIRST
"""
        )
        (eval_dir / "bbb.yml").write_text(
            """
name: second
description: Second evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Second prompt
output_suffix: SECOND
aliases:
  - first
"""
        )

        import logging

        with caplog.at_level(logging.WARNING):
            result = discover_local_evaluators(tmp_path)

        assert result["first"].name == "first"  # Original, not alias
        assert result["second"].name == "second"
        assert "Alias 'first' conflicts" in caplog.text

    def test_discover_uses_cwd_by_default(self, tmp_path, monkeypatch):
        """Uses current working directory when base_path is None."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "test.yml").write_text(
            """
name: test
description: Test
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Test
output_suffix: TEST
"""
        )

        monkeypatch.chdir(tmp_path)
        result = discover_local_evaluators()  # No base_path argument

        assert "test" in result

    def test_discover_ignores_non_yml_files(self, tmp_path):
        """Only .yml files are discovered, not .yaml or others."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)

        # This should be discovered
        (eval_dir / "good.yml").write_text(
            """
name: good
description: Good
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Good
output_suffix: GOOD
"""
        )

        # These should be ignored
        (eval_dir / "ignored.yaml").write_text(
            """
name: ignored
description: Ignored
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Ignored
output_suffix: IGNORED
"""
        )
        (eval_dir / "readme.md").write_text("# README")
        (eval_dir / "config.json").write_text("{}")

        result = discover_local_evaluators(tmp_path)

        assert "good" in result
        assert "ignored" not in result
        assert len(result) == 1

    def test_discover_skips_yaml_syntax_error(self, tmp_path, caplog):
        """YAML syntax errors are skipped with warning, valid files still load."""
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)

        # Malformed YAML (bad indentation)
        (eval_dir / "broken.yml").write_text(
            """
name: broken
  description: Bad indentation
model: gpt-4o
"""
        )

        # Valid YAML
        (eval_dir / "valid.yml").write_text(
            """
name: valid
description: Valid evaluator
model: gpt-4o
api_key_env: OPENAI_API_KEY
prompt: Valid prompt
output_suffix: VALID
"""
        )

        import logging

        with caplog.at_level(logging.WARNING):
            result = discover_local_evaluators(tmp_path)

        assert "valid" in result
        assert "broken" not in result
        assert "YAML syntax error" in caplog.text
