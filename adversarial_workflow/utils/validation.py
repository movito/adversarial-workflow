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

    with open(log_file_path, encoding="utf-8") as f:
        content = f.read()

    # Check minimum content size
    if len(content) < 500:
        return (
            False,
            None,
            f"Log file too small ({len(content)} bytes) - evaluation likely failed",
        )

    # Extract verdict — supports built-in and custom evaluator verdict names
    verdict = None
    # All recognized verdicts across built-in and custom evaluators
    all_verdicts = (
        "APPROVED|NEEDS_REVISION|REJECTED"  # built-in
        "|PROCEED|RETHINK"  # architecture-planner
        "|REVISION_SUGGESTED|RESTRUCTURE_NEEDED"  # architecture-reviewer
        "|COMPLIANT|MOSTLY_COMPLIANT|NON_COMPLIANT"  # spec-compliance
        "|PASS|CONCERNS|FAIL"  # code-reviewer
    )
    verdict_patterns = [
        rf"Verdict:\s*({all_verdicts})",
        rf"\*\*Verdict\*\*:\s*({all_verdicts})",
        rf"\*\*Verdict\*\*:\s*\*\*({all_verdicts})\*\*",  # **Verdict**: **FAIL**
        rf"[-*]\s*\*\*({all_verdicts})\*\*",  # - **FAIL**: ... (list item)
        rf"^\*\*({all_verdicts})\*\*",  # **FAIL** at line start
        rf"^({all_verdicts})\s*$",  # FAIL (bare line)
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
