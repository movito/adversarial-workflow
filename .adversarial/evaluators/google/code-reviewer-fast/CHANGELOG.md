# Changelog - code-reviewer-fast

All notable changes to this evaluator will be documented in this file.

## [1.0.0] - 2026-02-27

### Added

- Initial release
- Condensed adversarial review protocol (edge cases, tracing, test gaps, interactions)
- Optimized for Gemini Flash speed and cost (~$0.003-0.01/run)
- PASS/CONCERNS/FAIL verdict system
- Finding categories: CORRECTNESS, ROBUSTNESS, TESTING

### Origin

- Fast variant of openai/code-reviewer
- Battle-tested on dispatch-kit as iteration evaluator
- Used for re-checking after fixes and pre-push sanity checks
