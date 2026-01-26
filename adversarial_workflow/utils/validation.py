"""Output validation utilities."""

from __future__ import annotations

import os
import re


def validate_evaluation_output(
    log_file_path: str,
) -> tuple[bool, str | None, str]:
    """
    Validate that evaluation log contains actual evaluation content.

    Args:
        log_file_path: Path to the evaluation log file

    Returns:
        (is_valid, verdict, message):
            - is_valid: True if valid evaluation, False if failed
            - verdict: "APPROVED", "NEEDS_REVISION", "REJECTED", or None
            - message: Descriptive message about validation result
    """
    if not os.path.exists(log_file_path):
        return False, None, f"Log file not found: {log_file_path}"

    with open(log_file_path) as f:
        content = f.read()

    # Check minimum content size
    if len(content) < 500:
        return (
            False,
            None,
            f"Log file too small ({len(content)} bytes) - evaluation likely failed",
        )

    # Check for evaluation markers (case-insensitive)
    content_lower = content.lower()
    evaluation_markers = [
        "verdict:",
        "approved",
        "needs_revision",
        "rejected",
        "evaluation summary",
        "strengths",
        "concerns",
    ]

    has_evaluation_content = any(
        marker in content_lower for marker in evaluation_markers
    )
    if not has_evaluation_content:
        return (
            False,
            None,
            "Log file missing evaluation content - no verdict or analysis found",
        )

    # Extract verdict
    verdict = None
    verdict_patterns = [
        r"Verdict:\s*(APPROVED|NEEDS_REVISION|REJECTED)",
        r"\*\*Verdict\*\*:\s*(APPROVED|NEEDS_REVISION|REJECTED)",
        r"^(APPROVED|NEEDS_REVISION|REJECTED)\s*$",
    ]

    for pattern in verdict_patterns:
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
        if match:
            verdict = match.group(1).upper()
            break

    if verdict:
        return True, verdict, f"Valid evaluation with verdict: {verdict}"
    else:
        # Has content but no clear verdict
        return True, None, "Evaluation complete (verdict not detected)"
