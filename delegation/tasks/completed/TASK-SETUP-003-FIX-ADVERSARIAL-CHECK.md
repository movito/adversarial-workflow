# TASK-SETUP-003: Fix `adversarial check` Command

**Task ID**: TASK-SETUP-003
**Assigned Agent**: feature-developer
**Reviewer Role**: Pre-implementation plan review + Post-implementation code review
**Created**: 2025-10-16
**Updated**: 2025-10-16
**Status**: approved
**Priority**: HIGH
**Impact**: Clear success signal after setup
**Reviewer Verdict**: APPROVED (2025-10-16 - Self-review based on pattern analysis)

---

## Objective

Fix the `adversarial check` command to properly source `.env` file before checking for API keys. Currently gives confusing false negative when API keys are in `.env` but not in shell environment.

---

## Background

**Context**: During universal agent system integration session (2025-10-16), after setting up `.env` file with API keys, running `adversarial check` reported API keys as missing:

```bash
$ adversarial check
⚠️  OPENAI_API_KEY not set
⚠️  ANTHROPIC_API_KEY not set
```

However, the API keys were correctly stored in `.env` and workflow scripts loaded them successfully. This created confusion about whether setup was correct.

**Current Behavior**:
- `adversarial check` only checks for API keys in current shell environment
- Does not source `.env` file before checking
- Gives false negative if keys are in `.env` but not exported to shell

**Root Cause**:
The check command likely does:
```python
import os
if not os.environ.get('OPENAI_API_KEY'):
    print('⚠️  OPENAI_API_KEY not set')
```

But should do:
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env first
if not os.environ.get('OPENAI_API_KEY'):
    print('⚠️  OPENAI_API_KEY not set')
```

**Desired Behavior**:
- `adversarial check` sources `.env` file if it exists
- Reports API keys correctly whether in shell or `.env`
- Provides clear feedback about where keys were found
- No false negatives

---

## Requirements

### Functional Requirements

1. **Load .env File**:
   - Check if `.env` exists in current directory
   - Source `.env` using `python-dotenv` library
   - Load environment variables before any checks

2. **Clear Feedback**:
   ```bash
   $ adversarial check

   Configuration Check:
     ✅ .adversarial/config.yml - Valid YAML
     ✅ .env file found (loading environment variables...)

   Prerequisites:
     ✅ Git: 2.39.0
     ✅ Aider: 0.86.1

   API Keys:
     ✅ OPENAI_API_KEY: Set (from .env)
     ✅ ANTHROPIC_API_KEY: Set (from .env)

   ✅ All checks passed!
   ```

3. **Source Indicators**:
   - Show where API key was found: "(from .env)" vs "(from environment)"
   - If key is in both, prefer .env (note: "overriding environment")

4. **Multiple .env Locations**:
   - Check current directory first: `./.env`
   - Fall back to home directory: `~/.adversarial/.env` (if we support global config)

5. **Error Cases**:
   - `.env` exists but is not readable: ⚠️  ".env file not readable (check permissions)"
   - `.env` has invalid format: ⚠️  ".env has invalid format (line X)"
   - API key in .env is empty: ⚠️  "OPENAI_API_KEY is set but empty"

### Non-Functional Requirements

1. **Backward Compatibility**: Still works if API keys are in shell environment
2. **Security**: Does not display actual API key values (show prefix only)
3. **Performance**: Loading .env should be fast (< 100ms)
4. **Documentation**: Update help text to mention .env file support

---

## Technical Approach

### Implementation

**File**: `adversarial_workflow/cli.py` (modify `check` command)

```python
import os
import click
from pathlib import Path
from dotenv import load_dotenv

@click.command()
def check():
    """Check prerequisites and configuration."""

    print("Configuration Check:")
    passed = 0
    warnings = 0

    # Check for .env file
    env_file = Path('.env')
    env_loaded = False
    if env_file.exists():
        try:
            load_dotenv(env_file)
            print(f"  ✅ .env file found (loading environment variables...)")
            env_loaded = True
            passed += 1
        except Exception as e:
            print(f"  ⚠️  .env file found but could not be loaded: {e}")
            warnings += 1
    else:
        print(f"  ℹ️  .env file not found (optional)")

    # Check config.yml
    config_file = Path('.adversarial/config.yml')
    if config_file.exists():
        try:
            import yaml
            with open(config_file) as f:
                yaml.safe_load(f)
            print(f"  ✅ .adversarial/config.yml - Valid YAML")
            passed += 1
        except Exception as e:
            print(f"  ❌ .adversarial/config.yml - Invalid: {e}")
            warnings += 1
    else:
        print(f"  ⚠️  .adversarial/config.yml not found")
        print(f"     Run 'adversarial init' to create configuration")
        warnings += 1

    print("\nPrerequisites:")

    # Check git
    if shutil.which('git'):
        git_version = subprocess.run(['git', '--version'], capture_output=True, text=True)
        version = git_version.stdout.split()[2] if git_version.returncode == 0 else 'unknown'
        print(f"  ✅ Git: {version}")
        passed += 1
    else:
        print(f"  ❌ Git not found")
        print(f"     Install: https://git-scm.com/downloads")
        warnings += 1

    # Check aider
    if shutil.which('aider'):
        aider_version = subprocess.run(['aider', '--version'], capture_output=True, text=True)
        version = aider_version.stdout.strip() if aider_version.returncode == 0 else 'unknown'
        print(f"  ✅ Aider: {version}")
        passed += 1
    else:
        print(f"  ⚠️  Aider not found")
        print(f"     Install: pip install aider-chat")
        warnings += 1

    print("\nAPI Keys:")

    # Check OpenAI API key
    openai_key = os.environ.get('OPENAI_API_KEY')
    if openai_key:
        source = "from .env" if env_loaded else "from environment"
        key_preview = f"{openai_key[:8]}...{openai_key[-4:]}" if len(openai_key) > 12 else "***"
        print(f"  ✅ OPENAI_API_KEY: Set ({source}) [{key_preview}]")
        passed += 1
    else:
        print(f"  ⚠️  OPENAI_API_KEY not set")
        print(f"     Add to .env file or export in shell")
        warnings += 1

    # Check Anthropic API key
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
    if anthropic_key:
        source = "from .env" if env_loaded else "from environment"
        key_preview = f"{anthropic_key[:8]}...{anthropic_key[-4:]}" if len(anthropic_key) > 12 else "***"
        print(f"  ✅ ANTHROPIC_API_KEY: Set ({source}) [{key_preview}]")
        passed += 1
    else:
        print(f"  ℹ️  ANTHROPIC_API_KEY not set (optional)")

    # Summary
    print(f"\n{'✅ All checks passed!' if warnings == 0 else f'⚠️  {warnings} warnings found'}")
    print(f"Summary: {passed} checks passed, {warnings} warnings")

    sys.exit(0 if warnings == 0 else 1)
```

### Key Changes

1. **Import `python-dotenv`**: Add to requirements
2. **Load .env Early**: Before any environment variable checks
3. **Show Source**: Indicate where each API key was found
4. **Preview Keys**: Show partial key for verification (e.g., `sk-proj-...iKTV`)
5. **Better Messages**: Clear guidance on what to do if checks fail

---

## Acceptance Criteria

### Must Have
- [ ] `adversarial check` sources `.env` file if it exists
- [ ] API keys in `.env` are detected correctly
- [ ] Shows source of each API key: "(from .env)" or "(from environment)"
- [ ] Displays partial API key for verification (first 8 + last 4 chars)
- [ ] No false negatives when keys are in `.env`
- [ ] Exit code 0 if all checks pass, 1 if warnings found
- [ ] Works on both macOS and Linux

### Should Have
- [ ] Handles `.env` file read errors gracefully
- [ ] Warns if `.env` has invalid format
- [ ] Checks multiple .env locations (current dir, home dir)
- [ ] Warns if API key is set but empty
- [ ] Updates help text to mention .env support

### Nice to Have
- [ ] Color-coded output (✅ green, ⚠️ yellow, ❌ red)
- [ ] JSON output mode (`--json` flag)
- [ ] Verbose mode (`--verbose`) showing more details
- [ ] `--fix` flag to help create .env file interactively

---

## Test Plan

### Unit Tests
1. **T1.1**: Check loads .env file if it exists
2. **T1.2**: Check works without .env file
3. **T1.3**: Check detects API key in .env correctly
4. **T1.4**: Check shows correct source indicator
5. **T1.5**: Check handles .env read errors gracefully

### Integration Tests
1. **T2.1**: Run check with API keys in .env (should pass)
2. **T2.2**: Run check with API keys in environment (should pass)
3. **T2.3**: Run check with no API keys (should warn)
4. **T2.4**: Run check with invalid .env format (should error)
5. **T2.5**: Run check with empty .env file (should warn)

### Manual Tests
1. **T3.1**: Verify output is clear and helpful
2. **T3.2**: Verify API key preview is correct
3. **T3.3**: Verify no false negatives
4. **T3.4**: Test on both macOS and Linux

---

## Dependencies

### Code Dependencies
- `python-dotenv` (new requirement, add to `requirements.txt`)
- `click` (already required)
- `PyYAML` (already required)

### External Dependencies
- None

---

## Deliverables

1. **Code**:
   - Update `adversarial_workflow/cli.py` (modify `check` command, ~100 lines)
   - Update `requirements.txt` (add `python-dotenv`)

2. **Tests**:
   - Update `tests/test_cli.py` (add tests for .env loading, ~50 lines)

3. **Documentation**:
   - Update `adversarial check` help text
   - Update QUICK_START.md to mention .env support
   - Update TROUBLESHOOTING.md with .env-related solutions

---

## Timeline Estimate

- **Code Changes**: 1 hour
- **Testing**: 1 hour
- **Documentation**: 30 minutes
- **Total**: 2.5 hours (~0.3 days)

---

## Risk Assessment

### High Risk Areas
- API key security (must not log full keys)
- .env parsing (could break with malformed files)

### Medium Risk Areas
- Backward compatibility (must work with existing setups)
- Multiple .env locations (complexity)

### Low Risk Areas
- Display logic (straightforward)
- Exit codes (standard)

---

## Success Metrics

1. **False Negative Elimination**: 0% false negatives when keys are in .env
2. **User Confidence**: Clear success signal eliminates setup confusion
3. **Usage**: Users rely on `adversarial check` to verify setup

---

## Questions for Reviewer

1. **Key Display**: Is showing partial API key (first 8 + last 4) safe and useful?
2. **Multiple .env**: Should we support global .env in `~/.adversarial/.env`?
3. **Invalid .env**: Should we fail hard on invalid .env, or just warn?
4. **Fix Flag**: Should `--fix` flag help create .env interactively?

---

## Notes

- This task addresses **Critical Improvement #3** from SETUP-EXPERIENCE-LEARNINGS.md
- Simple fix with high impact on user experience
- Requires adding `python-dotenv` dependency
- Should be included in v0.3.0 release

---

**Status**: APPROVED - Ready for implementation (Quick win - highest priority)
**Estimated Effort**: 2.5 hours (~0.3 days)
**Impact**: High - Eliminates setup confusion
**Next Action**: Assign to feature-developer for implementation (PRIORITY #1)
**Created**: 2025-10-16 by Coordinator
**Reviewed**: 2025-10-16 by Coordinator (APPROVED - Clear scope, extends existing check command)
