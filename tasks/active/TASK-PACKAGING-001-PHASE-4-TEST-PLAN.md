# TASK-PACKAGING-001: Phase 4 - Local Testing Plan

**Task ID**: TASK-PACKAGING-001-PHASE-4
**Assigned Agent**: test-runner (execution), coordinator (planning)
**Evaluator Role**: Pre-test plan review + Post-test results review
**Created**: 2025-10-15
**Updated**: 2025-10-15 (Expanded to macOS + Linux testing)
**Status**: updated-for-unix-platforms

---

## Objective

Verify that the adversarial-workflow package works correctly on **Unix-like systems (macOS and Linux)**. Ensure all CLI commands function, templates render properly, and the workflow executes end-to-end without errors. Validate cross-platform compatibility between macOS and Linux environments.

---

## Background

Phases 1-3 are complete:
- **Phase 1**: Package structure (6 files, 828 lines)
- **Phase 2**: Script templates (7 files, 693 lines)
- **Phase 3**: Documentation (5 files, 4,792 lines)

**Total deliverable**: 18 files, 6,313 lines of code and documentation

**Branch**: `feature/v1.2.0-adversarial-workflow-package`

This phase verifies the package actually works before proceeding to multi-environment testing.

---

## Test Environment

### Primary Environment (macOS)
**System**: macOS 24.6.0 (Darwin)
**Python**: System Python (check version)
**Git**: Repository available
**Location**: `/Users/broadcaster_three/Github/thematic-cuts/`
**Test Directory**: Create temporary test project in `/tmp/adversarial-test-project/`

### Secondary Environment (Linux)
**System**: Ubuntu 22.04 LTS (via GitHub Actions or Docker)
**Python**: 3.8, 3.9, 3.10, 3.11, 3.12 (matrix testing)
**Git**: Repository available
**Test Directory**: `/tmp/adversarial-test-project/`
**Setup Method**: GitHub Actions (free tier) or local Docker container

### Platform Scope
- ✅ **macOS**: Full test suite execution
- ✅ **Linux**: Full test suite execution + bash version differences
- ❌ **Windows**: Explicitly excluded (requires WSL/Git Bash - document as limitation)

---

## Test Categories

### Category 1: Package Installation
**Objective**: Verify package can be installed in development mode

**Test Cases**:

1. **T1.1: Development Installation**
   - Command: `pip install -e adversarial-workflow/`
   - Expected: Installation succeeds, no errors
   - Verification: `pip list | grep adversarial-workflow` shows package
   - Success Criteria: Package appears in pip list with correct version

2. **T1.2: Import Verification**
   - Command: `python -c "import adversarial_workflow; print(adversarial_workflow.__version__)"`
   - Expected: Imports successfully, prints version number
   - Success Criteria: No import errors

3. **T1.3: CLI Entry Point**
   - Command: `which adversarial`
   - Expected: Shows path to adversarial command
   - Success Criteria: Command is in PATH

4. **T1.4: Help Command**
   - Command: `adversarial --help`
   - Expected: Shows usage information with 5 commands
   - Success Criteria: Lists init, check, evaluate, review, validate commands

---

### Category 2: CLI Command Testing
**Objective**: Verify each CLI command executes without errors

**Test Cases**:

5. **T2.1: adversarial init - Error Handling (No Git)**
   - Setup: Create directory without git: `mkdir /tmp/no-git-test`
   - Command: `cd /tmp/no-git-test && adversarial init`
   - Expected: ERROR message "Not a git repository"
   - Success Criteria: Exits with clear error, suggests `git init`

6. **T2.2: adversarial init - Fresh Project**
   - Setup: Create git repo: `mkdir /tmp/adversarial-test-project && cd /tmp/adversarial-test-project && git init`
   - Command: `adversarial init`
   - Expected: Creates `.adversarial/` directory with templates
   - Verification: Check for files:
     - `.adversarial/config.yml`
     - `.adversarial/scripts/evaluate_plan.sh`
     - `.adversarial/scripts/review_implementation.sh`
     - `.adversarial/scripts/validate_tests.sh`
     - `.aider.conf.yml`
     - `.env.example`
   - Success Criteria: All 6 files created, scripts are executable

7. **T2.3: adversarial init - Already Initialized**
   - Setup: Run init twice
   - Command: `adversarial init` (second time)
   - Expected: WARNING "Already initialized", asks for confirmation
   - Success Criteria: Doesn't overwrite without permission

8. **T2.4: adversarial check - Missing Dependencies**
   - Setup: Use test project with no aider
   - Command: `adversarial check`
   - Expected: Reports missing aider, missing API keys
   - Success Criteria: Clear diagnostic output with fix suggestions

9. **T2.5: adversarial check - Fully Configured**
   - Setup: Install aider, set API key in .env
   - Command: `adversarial check`
   - Expected: "✓ All checks passed!"
   - Success Criteria: No errors or warnings

10. **T2.6: adversarial evaluate - Missing Task File**
    - Command: `adversarial evaluate nonexistent.md`
    - Expected: ERROR "Task file not found"
    - Success Criteria: Shows usage example

11. **T2.7: adversarial evaluate - Invalid Task File**
    - Setup: Create empty file: `echo "" > empty-task.md`
    - Command: `adversarial evaluate empty-task.md`
    - Expected: Attempts evaluation (may warn about empty content)
    - Success Criteria: No crash, handles gracefully

12. **T2.8: adversarial review - No Git Changes**
    - Setup: Clean git state
    - Command: `adversarial review`
    - Expected: "No git changes detected" (phantom work detection)
    - Success Criteria: Exits without calling aider

13. **T2.9: adversarial validate - Invalid Test Command**
    - Setup: Configure invalid test command in config.yml
    - Command: `adversarial validate "nonexistent-command"`
    - Expected: ERROR "Command not found"
    - Success Criteria: Captures error, doesn't hang

---

### Category 3: Template Rendering
**Objective**: Verify templates render correctly with user configuration

**Test Cases**:

14. **T3.1: Config Template Rendering**
    - File: `.adversarial/config.yml`
    - Check: Contains default values for:
      - `evaluator_model: gpt-4o`
      - `task_directory: tasks/`
      - `log_directory: .adversarial/logs/`
      - `artifacts_directory: .adversarial/artifacts/`
      - `test_command: pytest`
    - Success Criteria: Valid YAML, sensible defaults

15. **T3.2: Script Template Variable Substitution**
    - File: `.adversarial/scripts/evaluate_plan.sh`
    - Check: Contains config loading logic:
      ```bash
      EVALUATOR_MODEL=$(grep 'evaluator_model:' .adversarial/config.yml | awk '{print $2}')
      ```
    - Success Criteria: No remaining `{{VARIABLE}}` placeholders

16. **T3.3: Aider Config Template**
    - File: `.aider.conf.yml`
    - Check: Contains valid aider settings
    - Success Criteria: Valid YAML, correct aider flags

17. **T3.4: Env Template**
    - File: `.env.example`
    - Check: Contains OPENAI_API_KEY placeholder with instructions
    - Success Criteria: Clear comments explaining setup

---

### Category 4: Script Execution
**Objective**: Verify workflow scripts execute without syntax errors

**Test Cases**:

18. **T4.1: Evaluate Script - Config Loading**
    - Script: `.adversarial/scripts/evaluate_plan.sh`
    - Test: `bash -n evaluate_plan.sh` (syntax check)
    - Expected: No syntax errors
    - Success Criteria: Script is syntactically valid

19. **T4.2: Evaluate Script - Execution (Dry Run)**
    - Setup: Create minimal task file
    - Command: `bash .adversarial/scripts/evaluate_plan.sh test-task.md --dry-run` (if supported)
    - Expected: Loads config, shows what it would do
    - Success Criteria: No crashes, config values loaded correctly

20. **T4.3: Review Script - Config Loading**
    - Script: `.adversarial/scripts/review_implementation.sh`
    - Test: `bash -n review_implementation.sh`
    - Expected: No syntax errors
    - Success Criteria: Script is syntactically valid

21. **T4.4: Validate Script - Config Loading**
    - Script: `.adversarial/scripts/validate_tests.sh`
    - Test: `bash -n validate_tests.sh`
    - Expected: No syntax errors
    - Success Criteria: Script is syntactically valid

---

### Category 5: Configuration System
**Objective**: Verify configuration files are read and parsed correctly

**Test Cases**:

22. **T5.1: Config YAML Parsing**
    - File: `.adversarial/config.yml`
    - Test: `python -c "import yaml; yaml.safe_load(open('.adversarial/config.yml'))"`
    - Expected: Parses without error
    - Success Criteria: Valid YAML

23. **T5.2: Config Value Override**
    - Setup: Modify `evaluator_model: gpt-4-turbo` in config.yml
    - Test: Run script, check it uses gpt-4-turbo
    - Expected: Script picks up custom value
    - Success Criteria: Configuration is honored

24. **T5.3: Environment Variable Override**
    - Setup: `export ADVERSARIAL_EVALUATOR_MODEL=claude-sonnet-4-5`
    - Test: Check if env var overrides config
    - Expected: Depends on implementation (document behavior)
    - Success Criteria: Behavior is consistent and documented

25. **T5.4: Invalid YAML Handling**
    - Setup: Break YAML syntax: `echo "invalid: [unclosed" >> .adversarial/config.yml`
    - Command: `adversarial check`
    - Expected: ERROR "Invalid config.yml"
    - Success Criteria: Clear error message, suggests fix

---

### Category 6: Error Handling
**Objective**: Verify graceful failure and helpful error messages

**Test Cases**:

26. **T6.1: Missing API Key**
    - Setup: No .env file
    - Command: Attempt to run evaluate script
    - Expected: WARNING "OPENAI_API_KEY not set"
    - Success Criteria: Doesn't crash, shows fix instructions

27. **T6.2: Aider Not Installed**
    - Setup: Rename aider binary temporarily
    - Command: `adversarial check`
    - Expected: ERROR "Aider not found in PATH"
    - Success Criteria: Shows installation command

28. **T6.3: Permission Denied**
    - Setup: Make script non-executable: `chmod -x .adversarial/scripts/evaluate_plan.sh`
    - Command: Attempt to run script
    - Expected: ERROR "Permission denied"
    - Success Criteria: Suggests `chmod +x`

29. **T6.4: Disk Space Check** (if implemented)
    - Setup: N/A (requires special setup)
    - Expected: Warns if low disk space
    - Success Criteria: Optional - document if implemented

---

### Category 7: Integration Test - End-to-End Workflow
**Objective**: Run a complete workflow from init to validation

**Test Cases**:

30. **T7.1: Complete Workflow - Happy Path**
    - **Setup**: Fresh git repository with simple Python project
      ```bash
      mkdir /tmp/test-project && cd /tmp/test-project
      git init
      echo "def hello(): return 'world'" > main.py
      echo "def test_hello(): assert hello() == 'world'" > test_main.py
      git add . && git commit -m "Initial commit"
      ```

    - **Step 1: Initialize**
      - Command: `adversarial init`
      - Expected: Creates .adversarial/ directory
      - Verify: All templates present

    - **Step 2: Configure**
      - Edit `.adversarial/config.yml`:
        - Set `test_command: python -m pytest test_main.py -v`
        - Set `task_directory: ./`
      - Copy `.env.example` to `.env`
      - Add OPENAI_API_KEY (if available)

    - **Step 3: Create Task**
      - Create `task-test-feature.md`:
        ```markdown
        # Task: Add Exclamation Feature

        ## Objective
        Modify hello() to return 'world!'

        ## Implementation
        Change return statement to add exclamation

        ## Tests
        Update test to expect 'world!'
        ```

    - **Step 4: Plan Evaluation** (if aider + API key available)
      - Command: `.adversarial/scripts/evaluate_plan.sh task-test-feature.md`
      - Expected: Evaluator reviews plan, saves to logs/
      - Success Criteria: Creates log file, returns status code

    - **Step 5: Implementation**
      - Make change: `def hello(): return 'world!'`
      - Update test: `assert hello() == 'world!'`
      - Git add changes

    - **Step 6: Code Review** (if aider + API key available)
      - Command: `.adversarial/scripts/review_implementation.sh`
      - Expected: Evaluator reviews git diff
      - Success Criteria: Creates review file, checks for phantom work

    - **Step 7: Test Validation**
      - Command: `.adversarial/scripts/validate_tests.sh`
      - Expected: Runs pytest, captures output
      - Success Criteria: Tests pass, validation succeeds

    - **Overall Success Criteria**:
      - All steps complete without crashes
      - Logs created in correct locations
      - Workflow feels smooth and intuitive

31. **T7.2: Workflow - Phantom Work Detection**
    - **Setup**: Same as T7.1 but skip implementation (Step 5)
    - **Test**: Run review script with no git changes
    - **Expected**: Detects phantom work, aborts review
    - **Success Criteria**: "No changes detected" message, exits early

32. **T7.3: Workflow - Test Failure Handling**
    - **Setup**: Same as T7.1 but introduce failing test
    - **Test**: Run validate script with failing test
    - **Expected**: Captures failure, reports in validation log
    - **Success Criteria**: Non-zero exit code, clear failure message

---

### Category 8: Cross-Platform Compatibility (NEW)
**Objective**: Verify package works identically on macOS and Linux

**Test Cases**:

36. **T8.1: Bash Version Compatibility**
    - **macOS Test**: Check Bash version: `bash --version`
    - **Linux Test**: Check Bash version: `bash --version`
    - Expected: Scripts work on both bash 3.2+ (macOS) and bash 4.x+ (Linux)
    - Success Criteria: No syntax errors, scripts execute identically

37. **T8.2: Path Handling - Case Sensitivity**
    - **macOS Test**: Create file `Test.txt`, try to access `test.txt`
    - **Linux Test**: Create file `Test.txt`, try to access `test.txt`
    - Expected: macOS succeeds (case-insensitive), Linux fails (case-sensitive)
    - Success Criteria: Package handles both correctly (uses exact case)

38. **T8.3: Package Installation - Linux**
    - Setup: Ubuntu 22.04 via GitHub Actions or Docker
    - Command: `pip install -e adversarial-workflow/`
    - Expected: Installation succeeds on Linux
    - Success Criteria: All dependencies install, entry points work

39. **T8.4: CLI Commands - Linux**
    - Command: `adversarial --help` on Linux
    - Expected: Shows same output as macOS
    - Success Criteria: All 5 commands available and functional

40. **T8.5: Script Execution - Linux**
    - Script: `.adversarial/scripts/evaluate_plan.sh` on Linux
    - Test: `bash -n evaluate_plan.sh`
    - Expected: No syntax errors on Linux bash
    - Success Criteria: Script is syntactically valid on Linux

41. **T8.6: Environment Variables - Linux**
    - Setup: `.env` file with OPENAI_API_KEY on Linux
    - Test: Scripts can read environment variables
    - Expected: Same behavior as macOS
    - Success Criteria: API key loaded correctly

42. **T8.7: GitHub Actions Setup**
    - File: Create `.github/workflows/test-adversarial-workflow.yml`
    - Content: Matrix testing on Ubuntu 22.04 with Python 3.8-3.12
    - Command: Test workflow runs successfully
    - Expected: All tests pass on GitHub Actions runners
    - Success Criteria: CI pipeline validates Linux compatibility

43. **T8.8: End-to-End Workflow - Linux**
    - Test: Run complete T7.1 workflow on Linux (Ubuntu)
    - Expected: Same results as macOS
    - Success Criteria: All steps complete, logs match macOS output

---

### Category 9: Documentation Verification
**Objective**: Verify documentation examples are accurate and work

**Test Cases**:

44. **T9.1: README Quick Start**
    - Follow steps in `adversarial-workflow/README.md` exactly
    - Expected: Commands work as documented
    - Success Criteria: No discrepancies between docs and reality

45. **T9.2: README Platform Requirements**
    - File: `adversarial-workflow/README.md`
    - Check: Contains clear platform requirements section
    - Expected: Documents macOS/Linux support, Windows WSL requirement
    - Success Criteria: Users know what platforms are supported

46. **T9.3: EXAMPLES.md Python/pytest Example**
    - File: `adversarial-workflow/docs/EXAMPLES.md`
    - Test: Follow Python/pytest example
    - Expected: Configuration works as shown
    - Success Criteria: Example is accurate

47. **T9.4: TROUBLESHOOTING.md Solutions**
    - File: `adversarial-workflow/docs/TROUBLESHOOTING.md`
    - Test: Verify fix commands are correct (e.g., chmod commands)
    - Expected: Solutions work
    - Success Criteria: No incorrect commands

---

## Success Criteria

### Must Pass (Blocking Issues)
- [ ] All Category 1 tests pass (Package installation works on macOS)
- [ ] All Category 2 tests pass (CLI commands function on macOS)
- [ ] Category 8 tests pass (Cross-platform compatibility verified)
  - [ ] T8.3: Package installs on Linux
  - [ ] T8.4: CLI works on Linux
  - [ ] T8.7: GitHub Actions setup complete
- [ ] T7.1 passes (End-to-end workflow completes on macOS)
- [ ] T8.8 passes (End-to-end workflow completes on Linux)
- [ ] No crashes or unhandled exceptions
- [ ] Error messages are clear and actionable

### Should Pass (Non-Blocking Issues)
- [ ] All Category 3 tests pass (Templates render correctly)
- [ ] All Category 4 tests pass (Scripts execute)
- [ ] All Category 5 tests pass (Config system works)
- [ ] All Category 6 tests pass (Error handling is good)
- [ ] Category 8 platform-specific tests pass (Bash versions, case sensitivity)

### Nice to Have
- [ ] Category 7 advanced tests pass (Phantom work detection, failure handling)
- [ ] Category 9 tests pass (Documentation examples work)
- [ ] GitHub Actions CI runs successfully on every push

---

## Test Execution Plan

### Phase 4.1: Setup (macOS)
1. Ensure clean environment
2. Install package in development mode
3. Create test directory structure
4. Document system info (Python version, OS, etc.)

### Phase 4.2: macOS Testing
1. Run Category 1 tests (Installation)
2. Run Category 2 tests (CLI commands)
3. Run Categories 3-6 tests (Templates, Scripts, Config, Errors)
4. Run Category 7 tests (Integration)
5. Run Category 9 tests (Documentation)

### Phase 4.3: Linux Environment Setup
1. Set up Ubuntu 22.04 (GitHub Actions or Docker)
2. Install package in development mode on Linux
3. Create test directory structure
4. Document Linux system info (Python version, Bash version)

### Phase 4.4: Linux Testing
1. Run Category 1 tests on Linux (Installation)
2. Run Category 2 tests on Linux (CLI commands)
3. Run Category 8 tests (Cross-platform compatibility)
4. Run Category 7 tests on Linux (Integration E2E)
5. Create GitHub Actions workflow (T8.7)

### Phase 4.5: Results Documentation
1. Create test results matrix (macOS + Linux)
2. Document all failures with:
   - Test case ID
   - Platform (macOS/Linux)
   - Expected behavior
   - Actual behavior
   - Error messages
   - Screenshots if relevant
3. Categorize issues by severity:
   - CRITICAL: Blocks package use
   - HIGH: Major functionality broken
   - MEDIUM: Minor issues, workarounds exist
   - LOW: Cosmetic or documentation issues
4. Document platform-specific differences discovered

### Phase 4.6: Issue Analysis
1. Group failures by root cause
2. Identify patterns
3. Suggest fixes for each issue

---

## Deliverables

1. **Test Execution Report** (`PHASE-4-TEST-RESULTS.md`)
   - All test results (pass/fail)
   - System information
   - Execution times
   - Screenshots of key tests

2. **Issues List** (`PHASE-4-ISSUES.md`)
   - All discovered issues
   - Severity classification
   - Suggested fixes

3. **Updated Package** (if fixes needed)
   - Code changes to address issues
   - Updated documentation if inaccurate

---

## Risk Assessment

### Low Risk Areas
- Documentation (Phase 3 complete, high quality)
- Template content (Phase 2 tested)
- Package structure (Phase 1 standard layout)

### Medium Risk Areas
- CLI implementation (not yet tested)
- Config parsing (bash + Python interaction)
- Template rendering (variable substitution)

### High Risk Areas
- End-to-end workflow (complex, many moving parts)
- Error handling (edge cases may be missed)
- Cross-platform compatibility (only tested on macOS)

---

## Dependencies

### Required for Testing
- Python 3.8+ (system Python)
- pip (package installer)
- git (version control)
- bash (shell scripts)

### Optional for Full Testing
- aider-chat (for workflow scripts)
- OPENAI_API_KEY (for evaluator)
- pytest (for example tests)

### Not Required (Future Phases)
- Multiple OS environments (Phase 5)
- Multiple Python versions (Phase 5)
- CI/CD systems (Phase 6)

---

## Timeline Estimate

### Original (macOS-only): 4-7 hours
- **macOS Test Execution**: 2-3 hours
- **Issue Documentation**: 30-60 minutes
- **Fix Implementation**: 1-2 hours (depends on issues found)
- **Re-testing**: 1 hour

### Updated (macOS + Linux): 6-10 hours
- **macOS Test Execution**: 2-3 hours
- **Linux Environment Setup**: 30-60 minutes (GitHub Actions or Docker)
- **Linux Test Execution**: 1.5-2 hours
- **Cross-platform Comparison**: 30 minutes
- **Issue Documentation**: 45-90 minutes (both platforms)
- **Fix Implementation**: 1-2 hours (depends on issues found)
- **Re-testing**: 1-1.5 hours (both platforms)
- **Total**: 6-10 hours

**Evaluator Assessment**: +2-3 hours for Linux (Confirmed)

---

## Questions for Evaluator

1. **Test Coverage**: Are there critical scenarios missing from this test plan?
2. **Test Order**: Should any tests be run in a different order?
3. **Success Criteria**: Are the "must pass" vs "should pass" distinctions appropriate?
4. **Risk Assessment**: Do you agree with the risk classifications?
5. **Edge Cases**: What additional edge cases should be tested?
6. **Documentation**: Are test cases clearly described?
7. **Automation**: Should any of these tests be automated for Phase 5?

---

## Notes

- This plan focuses on **Unix-like systems (macOS + Linux)** testing
- ~~Multi-environment testing (Linux, Windows) is Phase 5~~ **UPDATED**: Linux testing moved to Phase 4
- Windows testing is **explicitly excluded** (requires WSL/Git Bash - different testing category)
- Phase 5 scope: Advanced multi-distribution Linux testing (Alpine, CentOS, etc.) if needed
- CI/CD integration testing is Phase 6
- Performance testing is deferred to Phase 6
- Security review is deferred to Phase 6

### Rationale for macOS + Linux Scope

**Evaluator Assessment** (2025-10-15):
- +2-3 hours effort (6-10 hours total vs. 4-7 hours macOS-only)
- 80-90% issue coverage (vs. 60-70% macOS-only)
- Discovers critical differences: Bash versions, case sensitivity, package managers
- GitHub Actions provides free Linux testing infrastructure
- Package is Bash-based by design (Unix-like natural fit)
- Windows native support would require architectural changes (Bash → Python rewrite)

**Decision**: Proceed with macOS + Linux as optimal balance of thoroughness and efficiency.

---

**Status**: Updated for Unix platforms (macOS + Linux)
**Test Cases**: 47 tests across 9 categories
**Estimated Duration**: 6-10 hours
**Next Action**: Run `scripts/evaluate_plan.sh` on updated plan
**Created**: 2025-10-15 by Coordinator
**Updated**: 2025-10-15 by Coordinator (Expanded to macOS + Linux)
