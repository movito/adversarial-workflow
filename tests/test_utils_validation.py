"""Tests for validation utilities."""

import pytest

from adversarial_workflow.utils.validation import validate_evaluation_output

# Padding to exceed the 500-byte minimum content threshold
_PAD = "Evaluation details. " * 30  # ~600 bytes


# All recognized verdicts for parametrized tests
_ALL_VERDICTS = [
    "APPROVED",
    "NEEDS_REVISION",
    "REJECTED",
    "PROCEED",
    "RETHINK",
    "REVISION_SUGGESTED",
    "RESTRUCTURE_NEEDED",
    "COMPLIANT",
    "MOSTLY_COMPLIANT",
    "NON_COMPLIANT",
    "PASS",
    "CONCERNS",
    "FAIL",
]

# Format templates: each produces a line containing the verdict
_VERDICT_FORMATS = {
    "bare_line": "{verdict}",
    "verdict_prefix": "Verdict: {verdict}",
    "bold_key": "**Verdict**: {verdict}",
    "bold_key_bold_value": "**Verdict**: **{verdict}**",
    "bold_value_line_start": "**{verdict}**",
    "list_item_bold_dash": "- **{verdict}**: Some description here",
    "list_item_bold_star": "* **{verdict}**: Some description here",
}


class TestValidateEvaluationOutput:
    """Test validate_evaluation_output function."""

    def test_file_not_found(self):
        """Returns invalid when file doesn't exist."""
        is_valid, verdict, message = validate_evaluation_output("/nonexistent.md")
        assert is_valid is False
        assert verdict is None
        assert "not found" in message.lower()

    def test_file_too_small(self, tmp_path):
        """Returns invalid when file is too small."""
        log_file = tmp_path / "small.md"
        log_file.write_text("tiny")

        is_valid, verdict, message = validate_evaluation_output(str(log_file))
        assert is_valid is False
        assert verdict is None
        assert "too small" in message.lower()

    def test_no_markers_still_valid(self, tmp_path):
        """Content without markers is still valid (library evaluators use varied formats)."""
        log_file = tmp_path / "no_markers.md"
        log_file.write_text("x" * 600)  # Big enough but no standard markers

        is_valid, verdict, message = validate_evaluation_output(str(log_file))
        # Should be valid - library evaluators may not use standard markers
        assert is_valid is True
        assert verdict is None
        assert "verdict not detected" in message.lower()

    def test_approved_verdict(self, tmp_path):
        """Extracts APPROVED verdict correctly."""
        log_file = tmp_path / "approved.md"
        log_file.write_text(
            """
# Evaluation Summary

**Verdict**: APPROVED

## Strengths
- Good implementation
"""
            + "x" * 500
        )

        is_valid, verdict, _message = validate_evaluation_output(str(log_file))
        assert is_valid is True
        assert verdict == "APPROVED"

    def test_needs_revision_verdict(self, tmp_path):
        """Extracts NEEDS_REVISION verdict correctly."""
        log_file = tmp_path / "needs_rev.md"
        log_file.write_text(
            """
# Evaluation Summary

Verdict: NEEDS_REVISION

## Concerns
- Missing tests
"""
            + "x" * 500
        )

        is_valid, verdict, _message = validate_evaluation_output(str(log_file))
        assert is_valid is True
        assert verdict == "NEEDS_REVISION"

    def test_rejected_verdict(self, tmp_path):
        """Extracts REJECTED verdict correctly."""
        log_file = tmp_path / "rejected.md"
        log_file.write_text(
            """
# Evaluation Summary

Verdict: REJECTED

## Critical Issues
- Security vulnerability
"""
            + "x" * 500
        )

        is_valid, verdict, _message = validate_evaluation_output(str(log_file))
        assert is_valid is True
        assert verdict == "REJECTED"

    def test_verdict_case_insensitive(self, tmp_path):
        """Verdict extraction is case insensitive."""
        log_file = tmp_path / "lower.md"
        log_file.write_text(
            """
# Evaluation Summary

Verdict: approved

## Details
Some evaluation content here
"""
            + "x" * 500
        )

        is_valid, verdict, _message = validate_evaluation_output(str(log_file))
        assert is_valid is True
        assert verdict == "APPROVED"

    def test_content_with_markers_but_no_verdict(self, tmp_path):
        """Valid when has markers but no clear verdict."""
        log_file = tmp_path / "no_verdict.md"
        log_file.write_text(
            """
# Evaluation Summary

## Strengths
- Good structure

## Concerns
- Needs more tests
"""
            + "x" * 500
        )

        is_valid, verdict, message = validate_evaluation_output(str(log_file))
        assert is_valid is True
        assert verdict is None
        assert "verdict not detected" in message.lower()


class TestVerdictFormatExtraction:
    """Parametrized tests for all verdict format x verdict name combinations."""

    @pytest.mark.parametrize("verdict", _ALL_VERDICTS)
    @pytest.mark.parametrize(
        "fmt_name,fmt_template",
        list(_VERDICT_FORMATS.items()),
        ids=list(_VERDICT_FORMATS.keys()),
    )
    def test_verdict_format_combinations(self, tmp_path, verdict, fmt_name, fmt_template):
        """Every recognized verdict is extracted from every supported format."""
        verdict_line = fmt_template.format(verdict=verdict)
        content = f"# Evaluation\n\n{_PAD}\n\n{verdict_line}\n"

        log_file = tmp_path / f"{fmt_name}_{verdict}.md"
        log_file.write_text(content)

        is_valid, extracted, _msg = validate_evaluation_output(str(log_file))
        assert is_valid is True, f"Expected valid for {fmt_name} / {verdict}"
        assert extracted == verdict, f"Expected {verdict} from format '{fmt_name}', got {extracted}"

    @pytest.mark.parametrize("verdict", _ALL_VERDICTS)
    def test_bold_value_case_insensitive(self, tmp_path, verdict):
        """Bold-wrapped verdicts are extracted case-insensitively."""
        content = f"# Eval\n\n{_PAD}\n\n**{verdict.lower()}**\n"
        log_file = tmp_path / f"bold_lower_{verdict}.md"
        log_file.write_text(content)

        is_valid, extracted, _msg = validate_evaluation_output(str(log_file))
        assert is_valid is True
        assert extracted == verdict

    def test_bold_verdict_with_trailing_text(self, tmp_path):
        """Bold verdict in list item with trailing description is extracted."""
        content = f"# Eval\n\n{_PAD}\n\n- **FAIL**: Correctness bugs found.\n"
        log_file = tmp_path / "list_trailing.md"
        log_file.write_text(content)

        is_valid, verdict, _msg = validate_evaluation_output(str(log_file))
        assert is_valid is True
        assert verdict == "FAIL"

    def test_bold_non_compliant_line_start(self, tmp_path):
        """Gemini Flash spec-compliance format: **NON_COMPLIANT** at line start."""
        content = f"# Spec Compliance\n\n{_PAD}\n\n**NON_COMPLIANT**\n"
        log_file = tmp_path / "gemini_spec.md"
        log_file.write_text(content)

        is_valid, verdict, _msg = validate_evaluation_output(str(log_file))
        assert is_valid is True
        assert verdict == "NON_COMPLIANT"

    def test_bold_key_bold_value(self, tmp_path):
        """Bold key AND bold value: **Verdict**: **FAIL**."""
        content = f"# Review\n\n{_PAD}\n\n**Verdict**: **FAIL**\n"
        log_file = tmp_path / "bold_both.md"
        log_file.write_text(content)

        is_valid, verdict, _msg = validate_evaluation_output(str(log_file))
        assert is_valid is True
        assert verdict == "FAIL"
