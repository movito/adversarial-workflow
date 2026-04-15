# ADV-0072 Handoff: Fix Verdict Extraction for Bold Markdown Formats

**Task**: `.kit/tasks/2-todo/ADV-0072-fix-verdict-extraction-bold-markdown.md`
**Agent**: feature-developer-v5
**Created**: 2026-04-15

## Mission

Fix `validate_evaluation_output()` to extract verdicts from Gemini Flash outputs
that wrap verdicts in markdown bold syntax (`**FAIL**`, `**NON_COMPLIANT**`).

## The Bug

`adversarial_workflow/utils/validation.py` lines 48-52:

```python
verdict_patterns = [
    rf"Verdict:\s*({all_verdicts})",           # Verdict: FAIL
    rf"\*\*Verdict\*\*:\s*({all_verdicts})",   # **Verdict**: FAIL
    rf"^({all_verdicts})\s*$",                 # FAIL (bare line)
]
```

These patterns don't match:
- `**FAIL**` — bold-wrapped verdict at line start
- `- **FAIL**: description` — bold-wrapped verdict in a list item
- `**Verdict**: **FAIL**` — bold key AND bold value

## The Fix

Add three patterns to handle bold-wrapped verdicts:

```python
verdict_patterns = [
    rf"Verdict:\s*({all_verdicts})",
    rf"\*\*Verdict\*\*:\s*({all_verdicts})",
    rf"\*\*Verdict\*\*:\s*\*\*({all_verdicts})\*\*",  # **Verdict**: **FAIL**
    rf"[-*]\s*\*\*({all_verdicts})\*\*",               # - **FAIL**: ... (list item)
    rf"^\*\*({all_verdicts})\*\*",                      # **FAIL** at line start
    rf"^({all_verdicts})\s*$",                          # FAIL (bare line)
]
```

## Key Files

| File | What to do |
|------|-----------|
| `adversarial_workflow/utils/validation.py` (L48-52) | Add 3 new regex patterns |
| `tests/test_validation.py` | Add test cases for each bold format variant |

## Test Matrix

Each verdict name × each format variant:

| Format | Example | Status |
|--------|---------|--------|
| Bare line | `FAIL` | existing |
| `Verdict:` prefix | `Verdict: FAIL` | existing |
| Bold key | `**Verdict**: FAIL` | existing |
| Bold key + bold value | `**Verdict**: **FAIL**` | **new** |
| Bold value on line | `**NON_COMPLIANT**` | **new** |
| List item bold | `- **FAIL**: description` | **new** |

Write a parametrized test that covers all format × verdict combinations.

## Evaluation History

- **arch-review-fast** (Gemini 2.5 Flash): REVISION_SUGGESTED
  - 3 findings — all valid long-term concerns but don't block this bug fix:
    1. Coupling to evolving text formats → acknowledged, structured output not feasible for LLM evaluators
    2. Regex scalability → tactical decision, monitor growth
    3. None vs explicit error → out of scope for this fix, could be a follow-up
  - Evaluator acknowledged fix is "pragmatic and immediately resolves the bug"

## Scope Boundaries

- **In scope**: Add regex patterns + tests for bold markdown variants
- **Out of scope**: Refactoring to structured output, custom extractors, or error handling changes
- This is a targeted bug fix, not an architecture rework

## Branch Naming

```bash
git checkout -b feature/ADV-0072-fix-verdict-extraction
./scripts/core/project start ADV-0072
```

## Success Criteria

- [ ] Gemini Flash `code-reviewer-fast` verdicts extracted correctly
- [ ] Gemini Flash `spec-compliance` verdicts extracted correctly
- [ ] o1 `code-reviewer` verdicts still work (no regression)
- [ ] Tests cover each new pattern variant (parametrized)
- [ ] All existing tests pass
- [ ] CI passes on GitHub
