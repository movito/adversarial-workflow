# ADV-0072: Fix Verdict Extraction for Bold Markdown Formats

**Status**: Done
**Priority**: Medium
**Type**: Bug fix
**Estimated Effort**: 1-2 hours
**Created**: 2026-04-15
**Origin**: ADV-0071 test evaluations — Gemini Flash outputs not parsed

## Summary

`validate_evaluation_output()` in `adversarial_workflow/utils/validation.py` fails to
extract verdicts from Gemini Flash evaluator outputs because the model wraps verdicts in
markdown bold syntax (`**FAIL**`, `**NON_COMPLIANT**`). The regex patterns only match
bare text verdicts, which o1 produces but Gemini Flash does not.

This causes the CLI to report `verdict: None` for all Gemini-based evaluators even when
the output clearly contains a valid verdict.

## Observed Formats

| Model | Evaluator | Output Format | Extracted? |
|-------|-----------|---------------|------------|
| o1 | code-reviewer | `FAIL` (bare line) | ✅ Yes |
| Gemini Flash | code-reviewer-fast | `- **FAIL**: Correctness bugs found.` | ❌ No |
| Gemini Flash | spec-compliance | `**NON_COMPLIANT**` (line start) | ❌ No |

## Root Cause

`validation.py` lines 48-52 define three regex patterns:

```python
verdict_patterns = [
    rf"Verdict:\s*({all_verdicts})",           # Verdict: FAIL
    rf"\*\*Verdict\*\*:\s*({all_verdicts})",   # **Verdict**: FAIL
    rf"^({all_verdicts})\s*$",                 # FAIL (bare line)
]
```

None match:
- `**FAIL**` — bold-wrapped verdict at line start
- `- **FAIL**: ...` — bold-wrapped verdict in a list item

## Proposed Fix

Add two patterns before the bare-line pattern:

```python
verdict_patterns = [
    rf"Verdict:\s*({all_verdicts})",
    rf"\*\*Verdict\*\*:\s*({all_verdicts})",
    rf"\*\*Verdict\*\*:\s*\*\*({all_verdicts})\*\*",  # **Verdict**: **FAIL**
    rf"[-*]\s*\*\*({all_verdicts})\*\*",               # - **FAIL**: ... (list item)
    rf"^\*\*({all_verdicts})\*\*",                      # **FAIL** at line start
    rf"^({all_verdicts})\s*$",
]
```

Verified with Python regex testing — all four observed formats match correctly.

## Acceptance Criteria

- [ ] Gemini Flash `code-reviewer-fast` verdicts extracted correctly
- [ ] Gemini Flash `spec-compliance` verdicts extracted correctly
- [ ] o1 `code-reviewer` verdicts still extracted correctly (no regression)
- [ ] All existing verdict patterns still work (bare, `Verdict:`, `**Verdict**:`)
- [ ] Tests cover each new pattern variant
- [ ] Property test: verdict in any recognized bold format is extracted

## Files to Modify

1. `adversarial_workflow/utils/validation.py` — add regex patterns
2. `tests/test_validation.py` (or equivalent) — add test cases for bold formats

## Test Matrix

Each verdict name × each format variant:

| Format | Example | Pattern |
|--------|---------|---------|
| Bare line | `FAIL` | existing |
| `Verdict:` prefix | `Verdict: FAIL` | existing |
| Bold key | `**Verdict**: FAIL` | existing |
| Bold key + bold value | `**Verdict**: **FAIL**` | new |
| Bold value on line | `**NON_COMPLIANT**` | new |
| List item bold | `- **FAIL**: description` | new |

## Notes

- Pre-existing bug, not a regression from ADV-0071
- Affects all Gemini-based evaluators (~$0.004/run), which are the most commonly used
- The evaluation content is correct — only the verdict extraction/display is broken
- No impact on human-readable output (the log file is fine), only on CLI status reporting

## Review

**PR**: #68
**Branch**: feature/ADV-0072-fix-verdict-extraction -> main

### Artifacts
- Review starter: `.kit/context/ADV-0072-REVIEW-STARTER.md`
- Evaluator review: `.kit/context/reviews/ADV-0072-evaluator-review.md`

### Files Changed
- `adversarial_workflow/utils/validation.py` (modified)
- `tests/test_utils_validation.py` (modified)
