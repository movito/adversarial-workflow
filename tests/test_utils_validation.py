"""Tests for validation utilities."""

import pytest

from adversarial_workflow.utils.validation import validate_evaluation_output


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
