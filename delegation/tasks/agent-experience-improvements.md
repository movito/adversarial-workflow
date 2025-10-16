# Task: Agent Experience Improvements (High Priority)

**Type**: Enhancement
**Priority**: HIGH
**Version**: v0.2.2

## Context

Agent integration testing revealed critical UX issues for AI agents trying to use adversarial-workflow. This task addresses the highest-priority improvements identified in `.agent-context/AGENT_EXPERIENCE_ADVERSARIAL_WORKFLOW.md`.

## Objectives

Improve agent experience by addressing the most critical blockers and pain points:

### 1. Document aider-chat prerequisite (HIGH)
**Problem**: Agents didn't know aider was required until `adversarial check` failed
**Solution**: Add prominent Prerequisites section to README before Quick Start

### 2. Add `__main__.py` for python -m execution (MEDIUM)
**Problem**: `python -m adversarial_workflow` doesn't work (no `__main__.py`)
**Solution**: Create simple `__main__.py` that calls `cli.main()`

### 3. Add pre-flight template validation (MEDIUM)
**Problem**: `adversarial init` fails with cryptic error if templates missing
**Solution**: Validate all required templates exist before attempting to copy them

## Implementation Plan

### Phase 1: README Prerequisites (Completed)
- [x] Add Prerequisites section before Quick Start
- [x] List all required dependencies explicitly:
  - Python 3.8+
  - Git repository
  - **aider-chat** (with installation command)
  - API keys (Anthropic/OpenAI)
- [x] Add platform requirements (macOS/Linux/WSL)
- [x] Link to detailed platform support section

### Phase 2: __main__.py Module (Completed)
- [x] Create `adversarial_workflow/__main__.py`
- [x] Import `main` from `cli`
- [x] Call `main()` when executed as module

### Phase 3: Pre-flight Validation (Completed)
- [x] Add template validation to `init()` function
- [x] Check all 6 required templates exist before proceeding
- [x] Provide clear error message with:
  - WHY: Explains this is a package bug, not user error
  - MISSING TEMPLATES: Lists what's missing
  - FIX: Suggests reporting issue or reinstalling
  - WORKAROUND: Manual creation instructions

## Testing Strategy

1. **Fresh Installation Test**:
   - Install in clean venv
   - Verify `adversarial --version` works
   - Verify `python -m adversarial_workflow --version` works
   - Verify templates are accessible

2. **Pre-flight Validation Test**:
   - Mock missing template scenario
   - Verify clear error message
   - Verify helpful workaround suggestions

3. **README Verification**:
   - Prerequisites appear before Quick Start
   - All dependencies listed
   - Installation commands correct

## Acceptance Criteria

- [x] README has prominent Prerequisites section with aider-chat
- [x] `python -m adversarial_workflow` works (via __main__.py)
- [x] `init()` validates templates before attempting copy
- [x] Clear error messages guide agents to solutions
- [x] No regressions in existing functionality

## Future Work (v0.2.3+)

Lower priority improvements:
- AGENT_INTEGRATION.md guide
- QUICK_START.md step-by-step guide
- `--dry-run` mode for init
- `repair` command for fixing common issues

## Success Metrics

- Agents can successfully install without confusion
- Missing template errors are caught early with clear guidance
- Documentation explicitly lists all prerequisites upfront
- `python -m adversarial_workflow` provides alternative execution method
