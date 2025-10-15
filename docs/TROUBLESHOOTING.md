# Troubleshooting Guide

This document provides solutions to common issues when setting up and using the adversarial workflow.

## Table of Contents

- [Installation & Setup Issues](#installation--setup-issues)
- [Configuration Problems](#configuration-problems)
- [API & Authentication Errors](#api--authentication-errors)
- [Script Execution Issues](#script-execution-issues)
- [Workflow-Specific Problems](#workflow-specific-problems)
- [Performance & Cost Issues](#performance--cost-issues)
- [Getting Help](#getting-help)

---

## Installation & Setup Issues

### Issue: `pip install adversarial-workflow` fails

**Symptoms**:
```bash
$ pip install adversarial-workflow
ERROR: Could not find a version that satisfies the requirement adversarial-workflow
```

**Causes & Solutions**:

1. **Package not yet published to PyPI**
   - Check if package is in development
   - Install from source:
     ```bash
     git clone https://github.com/movito/adversarial-workflow.git
     cd adversarial-workflow
     pip install -e .
     ```

2. **Python version too old**
   - Requires Python 3.8+
   - Check version: `python --version`
   - Upgrade: `pyenv install 3.11` or download from python.org

3. **Virtual environment issues**
   - Create clean venv:
     ```bash
     python -m venv .venv
     source .venv/bin/activate  # Linux/Mac
     .venv\Scripts\activate     # Windows
     pip install adversarial-workflow
     ```

### Issue: `adversarial: command not found`

**Symptoms**:
```bash
$ adversarial init
bash: adversarial: command not found
```

**Causes & Solutions**:

1. **Not in PATH** (common with `--user` installs)
   ```bash
   # Find installation location
   python -m pip show adversarial-workflow
   
   # Add to PATH (Linux/Mac)
   export PATH="$HOME/.local/bin:$PATH"
   
   # Or use full path
   python -m adversarial_workflow.cli init
   ```

2. **Virtual environment not activated**
   ```bash
   source .venv/bin/activate
   adversarial init  # Should work now
   ```

3. **Installation failed silently**
   ```bash
   pip install --force-reinstall adversarial-workflow
   pip show adversarial-workflow  # Verify installation
   ```

### Issue: `adversarial init` fails - "Not a git repository"

**Symptoms**:
```bash
$ adversarial init
❌ ERROR: Not a git repository. Run 'git init' first.
```

**Solution**:
```bash
# Initialize git repo first
git init
git add .
git commit -m "Initial commit"

# Then initialize adversarial workflow
adversarial init
```

**Why**: Adversarial workflow requires git for code review (git diff).

### Issue: Permission denied when running scripts

**Symptoms**:
```bash
$ .adversarial/scripts/evaluate_plan.sh task.md
bash: .adversarial/scripts/evaluate_plan.sh: Permission denied
```

**Solution**:
```bash
# Make scripts executable
chmod +x .adversarial/scripts/*.sh

# Or run with bash
bash .adversarial/scripts/evaluate_plan.sh task.md
```

**Prevention**: `adversarial init` should set permissions automatically. If not:
```bash
find .adversarial/scripts -name "*.sh" -exec chmod +x {} \;
```

---

## Configuration Problems

### Issue: Config file not found

**Symptoms**:
```bash
$ adversarial evaluate task.md
Error: Configuration file not found: .adversarial/config.yml
```

**Causes & Solutions**:

1. **Not initialized**
   ```bash
   adversarial init
   ```

2. **Wrong directory**
   ```bash
   # Make sure you're in project root
   pwd  # Check current directory
   ls -la .adversarial/  # Should exist
   cd /path/to/project  # Go to correct location
   ```

3. **Config deleted**
   ```bash
   # Recreate config
   adversarial init --force
   ```

### Issue: YAML parsing errors

**Symptoms**:
```bash
Error parsing config.yml: mapping values are not allowed here
```

**Cause**: Invalid YAML syntax

**Solution**:
```bash
# Check YAML syntax
cat .adversarial/config.yml

# Common issues:
# ❌ Wrong:
evaluator_model:gpt-4o  # Missing space after colon

# ✅ Correct:
evaluator_model: gpt-4o  # Space after colon

# ❌ Wrong:
test_command: pytest tests/  # Unquoted path with spaces
  --verbose

# ✅ Correct:
test_command: "pytest tests/ --verbose"  # Quoted
```

### Issue: Config changes not taking effect

**Symptoms**: Changed config but commands still use old values

**Causes & Solutions**:

1. **Environment variable override**
   ```bash
   # Check environment variables
   env | grep ADVERSARIAL
   
   # Unset if needed
   unset ADVERSARIAL_EVALUATOR_MODEL
   ```

2. **Script cached old config**
   ```bash
   # Restart terminal or reload environment
   source ~/.bashrc  # Linux
   source ~/.zshrc   # Mac with zsh
   ```

3. **Multiple config files**
   ```bash
   # Find all config files
   find . -name "config.yml"
   
   # Make sure editing the right one
   cat .adversarial/config.yml  # Should be in .adversarial/
   ```

**Precedence**: Environment variables > YAML config > defaults

---

## API & Authentication Errors

### Issue: "OpenAI API key not found"

**Symptoms**:
```bash
$ adversarial evaluate task.md
Error: OpenAI API key not found. Set OPENAI_API_KEY environment variable.
```

**Solutions**:

1. **Set in .env file** (recommended)
   ```bash
   # Copy template
   cp .adversarial/.env.example .env
   
   # Edit .env
   echo "OPENAI_API_KEY=sk-your-key-here" > .env
   
   # Verify
   cat .env
   ```

2. **Set as environment variable**
   ```bash
   # Temporary (current session)
   export OPENAI_API_KEY="sk-your-key-here"
   
   # Permanent (Linux/Mac)
   echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Set in shell profile**
   ```bash
   # Mac (zsh)
   echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.zshrc
   
   # Linux (bash)
   echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.bashrc
   ```

**Security note**: Never commit API keys to git!
```bash
# Ensure .env is in .gitignore
echo ".env" >> .gitignore
git add .gitignore
git commit -m "chore: Ignore .env files"
```

### Issue: "Invalid API key"

**Symptoms**:
```bash
Error: Invalid API key provided: sk-****
```

**Solutions**:

1. **Check key format**
   - OpenAI keys start with `sk-`
   - Check for extra spaces or newlines:
     ```bash
     echo "$OPENAI_API_KEY" | wc -c  # Should be ~51 chars
     echo "$OPENAI_API_KEY" | od -c  # Check for whitespace
     ```

2. **Regenerate key**
   - Go to https://platform.openai.com/api-keys
   - Create new key
   - Replace old key

3. **Check account status**
   - Verify account not suspended
   - Check billing at https://platform.openai.com/account/billing

### Issue: "Rate limit exceeded"

**Symptoms**:
```bash
Error: Rate limit reached for requests
```

**Solutions**:

1. **Wait and retry** (temporary limit)
   ```bash
   # Wait 60 seconds
   sleep 60
   adversarial evaluate task.md
   ```

2. **Upgrade plan** (if on free tier)
   - Free tier: 3 requests/min
   - Paid tier: 60 requests/min
   - https://platform.openai.com/account/billing

3. **Optimize token usage** (see TOKEN_OPTIMIZATION.md)
   - Use `--read` instead of `--files`
   - Single-shot invocations
   - Smaller context

### Issue: "Insufficient quota"

**Symptoms**:
```bash
Error: You exceeded your current quota, please check your plan and billing details
```

**Solutions**:

1. **Add payment method**
   - https://platform.openai.com/account/billing
   - Add credit card
   - Set usage limits

2. **Check usage**
   - View current usage at https://platform.openai.com/usage
   - Set spending limits to avoid surprises

3. **Estimate costs** (before running)
   - Plan evaluation: ~$0.05-0.15
   - Code review: ~$0.10-0.30
   - Test validation: ~$0.05-0.15
   - Typical task: ~$0.25-1.00

---

## Script Execution Issues

### Issue: "aider: command not found"

**Symptoms**:
```bash
$ .adversarial/scripts/evaluate_plan.sh task.md
.../evaluate_plan.sh: line 53: aider: command not found
```

**Solution**:
```bash
# Install aider-chat
pip install aider-chat

# Verify installation
aider --version

# If still not found, use full path in config
which aider  # Note the path
# Update .adversarial/config.yml if needed
```

### Issue: Scripts fail with "no such file or directory"

**Symptoms**:
```bash
$ .adversarial/scripts/evaluate_plan.sh task.md
Error: Task file not found: task.md
```

**Solutions**:

1. **Use correct path** (relative to current directory)
   ```bash
   # If in project root
   .adversarial/scripts/evaluate_plan.sh tasks/TASK-001.md
   
   # If in different directory
   .adversarial/scripts/evaluate_plan.sh ../tasks/TASK-001.md
   
   # Or use absolute path
   .adversarial/scripts/evaluate_plan.sh /full/path/to/task.md
   ```

2. **Check file exists**
   ```bash
   ls -la tasks/TASK-001.md
   ```

3. **Check task_directory in config**
   ```bash
   # Config should match your project structure
   cat .adversarial/config.yml
   # task_directory: tasks/  # Must match actual location
   ```

### Issue: "No changes detected in git diff"

**Symptoms**:
```bash
$ adversarial review
⚠️ WARNING: No changes detected in git diff!
⚠️ This might indicate PHANTOM WORK
```

**Causes & Solutions**:

1. **No implementation yet**
   - Go back to Phase 2 (implementation)
   - Make actual code changes
   - Then run review

2. **Changes not staged**
   ```bash
   git status  # Check what changed
   git add .   # Stage changes
   adversarial review
   ```

3. **Changes already committed**
   ```bash
   # Review the last commit instead
   git diff HEAD~1 > .adversarial/artifacts/last-commit.diff
   
   # Manually review using aider
   aider --read .adversarial/artifacts/last-commit.diff \
         --message "Review this implementation"
   ```

### Issue: Script hangs or runs forever

**Symptoms**: Script starts but never completes

**Causes & Solutions**:

1. **Interactive aider prompt**
   ```bash
   # Make sure scripts use --yes flag
   grep -n "\-\-yes" .adversarial/scripts/evaluate_plan.sh
   
   # Should see --yes in aider command
   ```

2. **Large context causing timeout**
   - Check file sizes being read
   - Reduce context (use --read for large files)
   - Increase timeout in script

3. **API timeout**
   ```bash
   # Check network connectivity
   curl https://api.openai.com/v1/models
   
   # Try manual aider call
   aider --model gpt-4o --yes --message "test"
   ```

**Kill hung process**:
```bash
# Find process
ps aux | grep aider

# Kill it
kill -9 <PID>

# Or use Ctrl+C in terminal
```

---

## Workflow-Specific Problems

### Issue: Reviewer always says "NEEDS_REVISION"

**Symptoms**: Plan gets rejected repeatedly, unclear what to fix

**Solutions**:

1. **Read feedback carefully**
   ```bash
   # Review specific concerns
   cat .adversarial/logs/TASK-001-PLAN-EVALUATION.md | grep "CRITICAL\|MEDIUM"
   ```

2. **Make plan more specific**
   - Add file:line numbers
   - Include SEARCH/REPLACE blocks
   - Specify exact changes
   - Define acceptance criteria measurably

3. **Provide context**
   - Explain WHY you're making changes
   - Reference investigation findings
   - Show grep results for scope

**Example improvement**:
```markdown
# ❌ Too vague:
Fix the validation logic

# ✅ Specific:
Add 3 validation checks to validate_clip() (data_models.py:45):
1. Line 47: Check name non-empty - if not clip.name: errors.append("Name required")
2. Line 52: Validate timecode format - if not is_valid_smpte(clip.start_timecode): ...
3. Line 58: Ensure start < end - if start_frames >= end_frames: ...

Acceptance: 6 xfailed tests in test_validation.py pass, exit code 0
```

### Issue: Code review detects phantom work (but code is real!)

**Symptoms**: Reviewer says "TODOs only" but you wrote real code

**Causes & Solutions**:

1. **Git diff showing wrong changes**
   ```bash
   # Verify what's actually in diff
   git diff | head -50
   
   # Make sure changes are staged
   git add -A
   git diff --cached  # Check staged changes
   ```

2. **Code looks like TODOs to evaluator**
   ```python
   # ❌ This looks like phantom work:
   def validate(clip):
       # Validate name
       # Validate timecode
       # Check start < end
       return True
   
   # ✅ This is clearly real code:
   def validate(clip):
       if not clip.name:
           return ValidationResult(valid=False, errors=["Name required"])
       if not is_valid_timecode(clip.start_timecode):
           return ValidationResult(valid=False, errors=["Invalid start"])
       # ... more actual logic ...
   ```

3. **Provide better git diff**
   ```bash
   # Include more context lines
   git diff -U10 > .adversarial/artifacts/implementation.diff
   ```

### Issue: Tests pass locally but validation fails

**Symptoms**: `pytest` succeeds but `adversarial validate` says FAIL

**Causes & Solutions**:

1. **Different test command**
   ```bash
   # Check config
   grep test_command .adversarial/config.yml
   
   # Should match what you run manually
   # If you run: pytest tests/test_validation.py -v
   # Config should have: test_command: pytest tests/test_validation.py -v
   ```

2. **Environment differences**
   ```bash
   # Make sure .env is loaded
   cat .env  # Contains OPENAI_API_KEY, etc.
   
   # Check virtual environment
   which python  # Should be in .venv
   ```

3. **Cached test results**
   ```bash
   # Clear pytest cache
   rm -rf .pytest_cache __pycache__
   pytest --cache-clear
   ```

### Issue: Workflow takes too long

**Symptoms**: Each phase takes 20+ minutes, whole task is 3+ hours

**Solutions**:

1. **Optimize token usage** (see TOKEN_OPTIMIZATION.md)
   - Use `--read` instead of `--files`
   - Smaller context (don't send entire codebase)
   - Single-shot prompts (no conversation)

2. **Skip Phase 0 for simple tasks**
   - Only investigate complex/unclear issues
   - Simple bugs: go straight to planning

3. **Streamline for trivial changes**
   ```bash
   # For < 10 line changes:
   1. Quick plan (5 min)
   2. Quick evaluation (5 min)
   3. Implement (10 min)
   4. Quick review (5 min)
   5. Quick validation (5 min)
   # Total: ~30 min instead of 2 hours
   ```

4. **Parallelize** (if multiple tasks)
   - Run evaluations in parallel
   - Use different terminal windows
   - Don't block on one task

---

## Performance & Cost Issues

### Issue: Single task costs $5+ in API calls

**Symptoms**: Token usage shows 500K+ tokens sent

**Causes & Solutions**:

1. **Using `--files` instead of `--read`**
   ```bash
   # ❌ EXPENSIVE:
   aider --files src/**/*.py  # Adds ALL files to context
   
   # ✅ CHEAP:
   aider --read task.md --read diff.txt  # Reference only
   ```

2. **Conversational usage** (not single-shot)
   ```bash
   # ❌ EXPENSIVE: Multiple messages
   aider --files src/validation.py
   # Then 10 messages back and forth
   
   # ✅ CHEAP: One complete message
   aider --files src/validation.py \
         --read plan.md \
         --message "[Complete detailed instructions]" \
         --yes
   ```

3. **Large files in context**
   ```bash
   # Check file sizes
   wc -l tasks/TASK-001.md
   
   # If > 1000 lines, extract relevant section
   sed -n '100,200p' tasks/TASK-001.md > task-excerpt.md
   aider --read task-excerpt.md
   ```

**Target costs**:
- Plan evaluation: $0.05-0.15
- Code review: $0.10-0.30
- Test validation: $0.05-0.15
- **Total per task: $0.25-1.00**

If exceeding these, optimize your aider usage.

### Issue: API calls timing out

**Symptoms**:
```bash
Error: Request timed out after 60 seconds
```

**Solutions**:

1. **Reduce context size**
   - Fewer files with `--read`
   - Shorter prompts
   - Extract relevant sections only

2. **Use faster model** (if quality acceptable)
   ```yaml
   # .adversarial/config.yml
   evaluator_model: gpt-4o-mini  # Faster, cheaper (but less capable)
   ```

3. **Retry with backoff**
   ```bash
   # Add retry logic to scripts
   for i in {1..3}; do
     adversarial evaluate task.md && break
     sleep 5
   done
   ```

### Issue: Aider crashes with "Out of memory"

**Symptoms**: System freezes, aider process killed

**Causes**: Too many large files in context

**Solutions**:

1. **Use `--read` instead of `--files`**
2. **Limit file scope**
   ```bash
   # Instead of:
   aider --files src/**/*.py
   
   # Do:
   aider --files src/validation.py  # Just one file
   ```

3. **Increase swap space** (Linux)
   ```bash
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

---

## Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide** ✓
2. **Review error messages carefully**
   - Copy full error message
   - Note what you were doing
   - Check recent changes

3. **Try basic debugging**
   ```bash
   # Check versions
   python --version
   pip show adversarial-workflow
   aider --version
   
   # Check configuration
   cat .adversarial/config.yml
   env | grep ADVERSARIAL
   
   # Check git status
   git status
   git diff
   ```

4. **Search existing issues**
   - GitHub issues: https://github.com/movito/adversarial-workflow/issues
   - Common problems likely documented

### How to Ask for Help

**Good bug report**:

```markdown
## Issue: Review fails with YAML parsing error

**Environment**:
- OS: Ubuntu 22.04
- Python: 3.11.5
- adversarial-workflow: 1.0.0
- aider-chat: 0.30.0

**Steps to reproduce**:
1. Run `adversarial init`
2. Edit .adversarial/config.yml to add custom test command
3. Run `adversarial evaluate tasks/TASK-001.md`

**Error message**:
```
Error parsing config.yml: mapping values are not allowed here
  in ".adversarial/config.yml", line 13, column 20
```

**Config file** (relevant section):
```yaml
test_command: pytest tests/ --verbose  # Line 13
```

**Expected**: Should parse YAML correctly
**Actual**: Parsing fails

**What I tried**:
- Quoted the value: `test_command: "pytest tests/ --verbose"` (didn't help)
- Removed the value (works, but need custom command)
```

### Where to Get Help

1. **GitHub Issues** (preferred)
   - https://github.com/movito/adversarial-workflow/issues
   - Search first, then create new issue
   - Include all details from template above

2. **Documentation**
   - README.md - Quick start and overview
   - INTERACTION_PATTERNS.md - Workflow concepts
   - TOKEN_OPTIMIZATION.md - Cost optimization
   - WORKFLOW_PHASES.md - Detailed phase guide
   - EXAMPLES.md - Integration examples

3. **Community**
   - GitHub Discussions (if enabled)
   - Project maintainers: @movito

### Self-Service Resources

**Enable debug logging**:
```bash
# Add to your scripts
set -x  # Print each command
# ... rest of script ...
set +x  # Turn off debug

# Or run with bash -x
bash -x .adversarial/scripts/evaluate_plan.sh task.md
```

**Test individual components**:
```bash
# Test aider directly
aider --model gpt-4o --yes --message "test message"

# Test YAML parsing
python -c "import yaml; print(yaml.safe_load(open('.adversarial/config.yml')))"

# Test git diff
git diff > test.diff
wc -l test.diff  # Should have content
```

**Check logs**:
```bash
# Review evaluation logs
ls -lh .adversarial/logs/
cat .adversarial/logs/TASK-*-PLAN-EVALUATION.md

# Check artifacts
ls -lh .adversarial/artifacts/
```

---

## Common Error Messages & Solutions

### "YAML Error: could not determine a constructor"

**Cause**: Invalid YAML syntax (often indentation)

**Solution**:
```yaml
# ❌ Wrong indentation:
workflow_settings:
enabled: true

# ✅ Correct:
workflow_settings:
  enabled: true
```

### "ModuleNotFoundError: No module named 'aider'"

**Cause**: Aider not installed

**Solution**:
```bash
pip install aider-chat
```

### "git: command not found"

**Cause**: Git not installed

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install git

# Mac
brew install git

# Verify
git --version
```

### "UnicodeDecodeError: 'utf-8' codec can't decode"

**Cause**: Binary file or wrong encoding

**Solution**:
```bash
# Check file encoding
file task.md  # Should say "UTF-8 Unicode text"

# Convert if needed
iconv -f ISO-8859-1 -t UTF-8 task.md > task-utf8.md
```

### "OpenAI Error 429: Too Many Requests"

**Cause**: Rate limit exceeded

**Solution**: Wait and retry, or upgrade plan (see API section above)

### "Git diff too large (> 1MB)"

**Cause**: Trying to review massive changes

**Solution**:
- Break into smaller commits
- Review module by module
- Use `git diff -- path/to/specific/file.py`

---

## Preventive Measures

**To avoid common issues**:

1. **Keep virtual environments clean**
   ```bash
   # Create project-specific venv
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Use version control properly**
   ```bash
   # Commit often
   git add -A
   git commit -m "WIP: description"
   
   # Create feature branches
   git checkout -b feature/task-001
   ```

3. **Document your config**
   ```yaml
   # .adversarial/config.yml
   # Custom test command for our project
   test_command: "pytest tests/ -v --tb=short"
   ```

4. **Track token usage**
   - Note costs in task logs
   - Monitor monthly spending
   - Optimize when costs increase

5. **Test in isolation**
   ```bash
   # Before running workflow, verify tests work
   pytest tests/
   
   # Then run workflow
   adversarial evaluate task.md
   ```

---

## Still Stuck?

If you've tried everything in this guide and still have issues:

1. **Create minimal reproduction**
   - Fresh project
   - Minimal config
   - Simplest task that fails
   - Document exact steps

2. **Gather diagnostic info**
   ```bash
   # Create diagnostic report
   echo "=== System Info ===" > diagnostic.txt
   uname -a >> diagnostic.txt
   python --version >> diagnostic.txt
   pip list >> diagnostic.txt
   echo "=== Config ===" >> diagnostic.txt
   cat .adversarial/config.yml >> diagnostic.txt
   echo "=== Last Error ===" >> diagnostic.txt
   # Paste error message here
   ```

3. **File GitHub issue** with all details
   - Include diagnostic report
   - Minimal reproduction steps
   - What you expected vs. what happened

**We're here to help!** The adversarial workflow is a community project, and your feedback makes it better for everyone.
