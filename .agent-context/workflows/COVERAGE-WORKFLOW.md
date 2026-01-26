# Coverage Workflow

**Purpose**: Measure and analyze test coverage to identify untested code
**Agent**: Primarily test-runner, but feature-developer should also use
**Last Updated**: 2025-11-01

---

## When to Use

- ✅ When verifying new feature implementation
- ✅ During test quality improvement tasks
- ✅ Before major releases
- ✅ When investigating code quality issues

---

## Commands

```bash
# Terminal coverage report
pytest tests/ --cov=thematic_cuts --cov-report=term-missing

# HTML coverage report (detailed)
pytest tests/ --cov=thematic_cuts --cov-report=html
# Then open: htmlcov/index.html

# Branch coverage (includes conditional branches)
pytest tests/ --cov=thematic_cuts --cov-branch

# Specific module coverage
pytest tests/ --cov=thematic_cuts.module_name --cov-report=term-missing

# Fail if coverage below threshold
pytest tests/ --cov=thematic_cuts --cov-fail-under=53
```

---

## Workflow Steps

1. **Run coverage**: `pytest tests/ --cov=thematic_cuts --cov-report=term-missing`
2. **Review terminal output**: Check overall coverage percentage
3. **Identify gaps**: Look for modules/lines marked as 'missing' (not covered)
4. **Generate HTML**: `pytest --cov-report=html`, open `htmlcov/index.html`
5. **Analyze**: Review uncovered lines, determine if they need tests
6. **Report**: Document coverage metrics, highlight critical untested code
7. **Recommend**: Suggest test additions or document why coverage gap is acceptable

---

## Coverage Targets

| Category | Target | Rationale |
|----------|--------|-----------|
| **Project Baseline** | ≥53% | Current baseline, must not decrease |
| **New Features** | ≥80% | New code should be well-tested |
| **Critical Paths** | ≥90% | Core functionality (timecode, assembly) |

### Acceptable Gaps:

- CLI entry points (hard to test in unit tests)
- DaVinci API integration (requires DaVinci Resolve)
- Error handling for rare edge cases
- Defensive code that shouldn't execute in practice

---

## Interpreting Coverage Report

### Terminal Output:

```
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
your_project/core/timecode.py            245     12    95%   123, 456-478
your_project/davinci_api/timeline.py     189     98    48%   45-67, 89-145
your_project/parsers/claude_output.py    156      8    95%   234, 267-273
---------------------------------------------------------------------
TOTAL                                    4521   2123    53%
```

- **Stmts**: Total statements in file
- **Miss**: Statements not executed during tests
- **Cover**: Coverage percentage
- **Missing**: Line numbers not covered

### HTML Report Colors:

- 🟢 **Green**: Line fully covered
- 🟡 **Yellow**: Line partially covered (e.g., if-else with one branch untested)
- 🔴 **Red**: Line not covered at all

### Excluding from Coverage:

Use `# pragma: no cover` for unreachable code:

```python
if sys.platform == "win32":  # pragma: no cover
    # Windows-specific code we can't test on CI
    pass
```

---

## Coverage Analysis Example

```markdown
## Coverage Analysis: TASK-2025-017

**Overall Coverage**: 53% (baseline maintained ✅)

### Module Breakdown:

| Module | Coverage | Status | Notes |
|--------|----------|--------|-------|
| timecode_engine.py | 98% | ✅ Excellent | Critical path well-tested |
| semantic_parser.py | 92% | ✅ Good | New feature, good coverage |
| davinci_api/timeline_ops.py | 48% | ⚠️ Needs Work | Requires DaVinci Resolve |
| cli/wizard.py | 35% | ⚠️ Acceptable | CLI entry points hard to unit test |

### Critical Gaps:

1. **your_project/davinci_api/timeline_ops.py**
   - **Lines 45-67**: Clip placement logic
   - **Impact**: HIGH - core assembly functionality
   - **Recommendation**: Add integration tests or mocks

2. **your_project/validation.py**
   - **Lines 234, 267-273**: Error handling edge cases
   - **Impact**: MEDIUM - rare error conditions
   - **Recommendation**: Acceptable gap (defensive code)

### Recommendation:

✅ Coverage acceptable for merge. Critical paths (timecode, semantic parser) well-tested.
⚠️ Consider adding integration tests for timeline_ops.py in future iteration.
```

---

## Best Practices

### ✅ DO:
- Maintain or improve baseline coverage (≥53%)
- Focus on critical paths first (timecode, assembly, validation)
- Use HTML report for detailed line-by-line analysis
- Document acceptable coverage gaps with justification
- Include coverage metrics in test reports

### ❌ DON'T:
- Don't aim for 100% coverage blindly (diminishing returns)
- Don't test implementation details (test behavior, not internals)
- Don't let coverage drop below baseline without coordinator approval
- Don't add pointless tests just to hit coverage numbers

---

## Documentation

- **Quick Reference**: `.agent-context/PROCEDURAL-KNOWLEDGE-INDEX.md`
- **Full Guide**: This document
- **Test Analysis**: [TEST-SUITE-WORKFLOW.md](./TEST-SUITE-WORKFLOW.md)
- **Coverage Config**: `pyproject.toml` → `[tool.coverage.run]`

---

**Related Workflows**:
- [TESTING-WORKFLOW.md](./TESTING-WORKFLOW.md) - Basic testing commands
- [TEST-SUITE-WORKFLOW.md](./TEST-SUITE-WORKFLOW.md) - Full test analysis
