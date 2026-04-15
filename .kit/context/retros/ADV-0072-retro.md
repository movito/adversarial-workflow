## ADV-0072 — Fix Verdict Extraction for Bold Markdown Formats (PR #68)

**Date**: 2026-04-15
**Agent**: feature-developer-v5
**Scorecard**: 4 threads, 0 regressions, 3 bot rounds, 5 commits

### What Worked

1. **Incremental anchoring caught by CodeRabbit** — The first commit only tightened 2 of 6 patterns. CodeRabbit progressively flagged the remaining loose patterns across rounds 2 and 3, resulting in a more thorough fix than the original spec requested. The iterative bot-driven refinement produced better code.
2. **Parametrized test matrix** — The 13 verdicts x 7 formats matrix (91 combinations) gave high confidence that anchoring changes didn't break any existing format. Every commit could be validated instantly against 120 tests.
3. **False-positive rejection tests** — Writing explicit tests for `**FAIL**ure` and `**FAIL**ed` substring cases proved the regex anchoring actually works, and gave the evaluator concrete evidence to verify against.

### What Was Surprising

1. **CodeRabbit found a real gap the spec missed** — The original task spec only called for adding 2 new patterns. CodeRabbit correctly identified that ALL existing patterns (including `Verdict:` and `**Verdict**:`) were vulnerable to the same mid-line/substring false-positive issue. The fix scope tripled.
2. **Evaluator false-positive on test coverage** — The o1 code-reviewer claimed bullet-item trailing text wasn't tested, but `test_bold_verdict_with_trailing_text` and the parametrized `list_item_bold_dash` both cover this exact case. The evaluator didn't recognize the parametrized test structure.
3. **BugBot stayed silent throughout** — All 3 rounds had zero BugBot findings. The changes were pure regex + tests with no security/dependency implications, so this makes sense.

### What Should Change

1. **Spec should audit all sibling patterns, not just the new ones** — The ADV-0072 spec only proposed adding 2 patterns but didn't flag that existing patterns had the same anchoring gap. Future regex bug fixes should include an "audit all patterns in the group" step.
2. **Evaluator should cross-reference parametrized tests** — The code-reviewer evaluator missed that parametrized fixtures cover cases it flagged as untested. Consider adding a note to evaluator input templates about parametrized test structures.
3. **`gh-review-helper.sh thread-reply` failed silently** — The `thread-reply` subcommand errored with exit code 2 and no useful message. Fell back to `gh pr comment`. The script should surface the actual GraphQL error.

### Permission Prompts Hit

None.

### Process Actions Taken

- [ ] Update task spec template to include "audit sibling patterns" step for regex fixes
- [ ] Investigate `gh-review-helper.sh thread-reply` failure mode and fix error messaging
- [ ] Consider adding parametrized test note to evaluator input template
