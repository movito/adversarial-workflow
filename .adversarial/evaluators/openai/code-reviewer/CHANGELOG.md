# Changelog - code-reviewer

All notable changes to this evaluator will be documented in this file.

## [1.0.0] - 2026-02-27

### Added
- Initial release
- 4-phase adversarial review protocol (attack surface, execution tracing, test cross-reference, interaction analysis)
- Boundary value enumeration for all input sources
- Test gap identification with coverage table
- PASS/CONCERNS/FAIL verdict system
- Finding categories: CORRECTNESS, ROBUSTNESS, TESTING, INTERACTION

### Origin
- Battle-tested on dispatch-kit (7 PRs: DSP-0014 through DSP-0040)
- Catches issues that BugBot and CodeRabbit miss (semantic correctness, resource exhaustion, type assumption violations)
- Complements security-focused reviewers by focusing on logic correctness
