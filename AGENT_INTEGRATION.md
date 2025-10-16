# Agent Integration Guide

**For AI Agents Integrating adversarial-workflow**

This guide provides a complete playbook for AI agents (like Claude Code, Cursor, or custom AI systems) to successfully integrate adversarial-workflow into projects. Based on real-world agent integration testing.

---

## Quick Reference

**Prerequisites:** Python 3.8+, Git, aider-chat, API keys (Anthropic/OpenAI)
**Installation:** `pip install adversarial-workflow`
**Verification:** `adversarial check`
**First Run:** `adversarial quickstart`

---

## Table of Contents

1. [Before You Start](#before-you-start)
2. [Installation Workflow](#installation-workflow)
3. [API Key Management](#api-key-management)
4. [Common Failure Modes](#common-failure-modes)
5. [Verification Checklist](#verification-checklist)
6. [Integration Patterns](#integration-patterns)
7. [Troubleshooting](#troubleshooting)

---

## Before You Start

### Read Documentation First

**ALWAYS** read package documentation before starting installation:
- Check README.md for prerequisites
- Look for INSTALL.md or QUICK_START.md
- Scan for dependency lists and system requirements

### Information Gathering Checklist

```
□ What dependencies does this package require?
□ Are there any hidden dependencies (like aider-chat)?
□ What API keys or credentials are needed?
□ What platform requirements exist? (Windows/macOS/Linux)
□ Are there any system-level dependencies? (bash, git, etc.)
□ What are the estimated costs? (API usage)
```

### Proactive Communication

Tell the user the COMPLETE picture before starting:

```
Agent: "I'm about to install adversarial-workflow. Here's what's needed:

DEPENDENCIES:
• Python 3.8+ ✅ (you have 3.11)
• Git repository ✅ (detected)
• aider-chat ❌ (needs installation)
• API keys ❌ (will need Anthropic or OpenAI)

PLATFORM:
• Requires: Unix-like system (macOS/Linux) or WSL
• Your system: macOS ✅

COSTS:
• ~$0.02-0.10 per workflow run
• Requires at least one API key (both recommended)

INSTALLATION PLAN:
1. Install aider-chat (prerequisite)
2. Install adversarial-workflow
3. Configure API keys (interactive)
4. Verify setup

Proceed? (Y/n)"
```

---

## Installation Workflow

### Phase 1: Prerequisites

**Install aider-chat FIRST:**

```bash
pip install aider-chat

# Verify installation
aider --version
```

If aider install fails, STOP and report to user. Don't continue with broken setup.

### Phase 2: Main Installation

```bash
pip install adversarial-workflow

# Verify installation
adversarial --version

# Alternative verification
python -m adversarial_workflow --version
```

### Phase 3: Initialization

```bash
cd project-directory/
adversarial init --interactive
```

If init fails with missing templates error:
- This is a PACKAGE BUG, not user error
- Report to user with exact error message
- Offer to create files manually as workaround

### Phase 4: Verification

```bash
adversarial check
```

Expected output:
```
✅ Git repository detected
✅ Aider installed (version X.Y.Z)
✅ ANTHROPIC_API_KEY configured
✅ OPENAI_API_KEY configured
✅ .adversarial/config.yml valid
✅ All scripts executable

✅ All checks passed! Your setup is ready.
```

---

## API Key Management

### Decision Tree for Agents

```
START: Need API keys for adversarial-workflow

├─ Q: Does user have keys ready?
│  ├─ YES → Collect interactively (see Pattern A)
│  └─ NO → Create .env.example, defer configuration (see Pattern B)
│
└─ Q: Should I test the keys?
   ├─ NO → Just validate format (recommended)
   └─ YES → Only if user explicitly requests

```

### Pattern A: Interactive Collection (User Has Keys)

```
Agent: "I'll collect your API keys now. These will be stored in .env
       (which is added to .gitignore automatically).

Please paste your Anthropic API key (starts with sk-ant-):
[User pastes key]

✅ Format validated (starts with sk-ant-, 108 characters)

Please paste your OpenAI API key (starts with sk-proj- or sk-):
[User pastes key]

✅ Format validated (starts with sk-proj-, 93 characters)

Creating .env file... ✅
Added .env to .gitignore... ✅

Your API keys are stored securely and won't be committed."
```

**Code Example:**

```python
def validate_api_key(key: str, provider: str) -> tuple[bool, str]:
    """Validate API key format (don't test actual API calls)"""
    if provider == "anthropic":
        if not key.startswith("sk-ant-"):
            return False, "Anthropic keys start with 'sk-ant-'"
        if len(key) < 20:
            return False, "Key seems too short"
        return True, "Format looks valid"

    elif provider == "openai":
        if not (key.startswith("sk-") or key.startswith("sk-proj-")):
            return False, "OpenAI keys start with 'sk-' or 'sk-proj-'"
        if len(key) < 20:
            return False, "Key seems too short"
        return True, "Format looks valid"

    return False, "Unknown provider"
```

### Pattern B: Deferred Configuration (User Doesn't Have Keys)

```
Agent: "I'll create a .env.example template. You can add your keys later.

To complete setup when you have keys:
1. Get API keys:
   • Anthropic: https://console.anthropic.com/settings/keys
   • OpenAI: https://platform.openai.com/api-keys

2. Create .env file:
   cp .env.example .env

3. Edit .env with your actual keys

4. Verify setup:
   adversarial check

Created: .env.example ✅"
```

### Security Rules for Agents

✅ **DO:**
- Validate key format before writing to file
- Add .env to .gitignore immediately
- Inform user about costs (~$0.02-0.10 per workflow)
- Use secret/password input (don't echo keys)

❌ **DON'T:**
- Log API keys in output
- Commit .env to git
- Test keys with actual API calls (costs money)
- Store keys in code or config files
- Show keys in error messages

---

## Common Failure Modes

### 1. Missing aider-chat

**Symptom:**
```
❌ ERROR: Aider not found
   Fix: Install: pip install aider-chat
```

**Agent Response:**
```
Agent: "adversarial check revealed missing aider-chat dependency.

This wasn't mentioned in your initial request, but it's required.

Should I:
[A] Install aider-chat now (recommended)
[B] Skip for now (you'll install manually)
[C] Abort installation"
```

### 2. Missing Template Files

**Symptom:**
```
❌ ERROR: Package installation incomplete

   MISSING TEMPLATES:
   • .aider.conf.yml.template
   • .env.example.template
```

**Agent Response:**
```
Agent: "❌ adversarial init failed with missing template error.

This is a PACKAGE BUG, not a configuration issue.

The package distribution is missing required files:
• .aider.conf.yml.template
• .env.example.template

OPTIONS:
1. Report bug: https://github.com/movito/adversarial-workflow/issues
2. Try reinstalling: pip install --upgrade --force-reinstall adversarial-workflow
3. Create files manually (I can help with this)

Which would you prefer?"
```

### 3. No Git Repository

**Symptom:**
```
❌ ERROR: Not a git repository
   Fix: Run: git init
```

**Agent Response:**
```
Agent: "adversarial-workflow requires a git repository to work.

It uses git to:
• Track code changes for review
• Detect phantom work
• Create audit trail

Should I initialize git now? (y/N):
[Wait for user confirmation]

If yes:
  git init
  git add .
  git commit -m "Initial commit"
  adversarial init
```

### 4. Platform Compatibility (Windows)

**Symptom:**
```
⚠️  WARNING: Native Windows is NOT Supported
```

**Agent Response:**
```
Agent: "Detected Windows platform. adversarial-workflow requires Unix shell.

RECOMMENDED: Install WSL (Windows Subsystem for Linux)
• 5-minute setup
• Full compatibility
• Guide: https://learn.microsoft.com/windows/wsl/install

ALTERNATIVE: Git Bash (not officially supported)
• May have issues
• Use at your own risk

BEST OPTION: I recommend stopping here and setting up WSL first.

Continue anyway? (not recommended) (y/N):"
```

---

## Verification Checklist

### Immediately After Installation

Run these checks and report results:

```bash
# Check 1: Package installed
adversarial --version
# Expected: adversarial-workflow X.Y.Z

# Check 2: Python module works
python -m adversarial_workflow --version
# Expected: adversarial-workflow X.Y.Z

# Check 3: Aider available
aider --version
# Expected: aider X.Y.Z

# Check 4: Setup validation
adversarial check
# Expected: All checks passed

# Check 5: Directory structure
ls -la .adversarial/
# Expected: config.yml, scripts/, logs/

# Check 6: Templates accessible
ls -la .adversarial/scripts/
# Expected: evaluate_plan.sh, review_implementation.sh, validate_tests.sh

# Check 7: Dotfiles created
ls -la .aider.conf.yml .env.example
# Expected: Both files exist
```

### Report Format

```
Agent: "✅ Installation Complete

VERIFICATION RESULTS:
✅ adversarial-workflow v0.2.2 installed
✅ python -m adversarial_workflow works
✅ aider v0.XX.X available
✅ Git repository detected
✅ Configuration files created
✅ All 3 workflow scripts present
✅ .aider.conf.yml created
✅ .env.example created

⚠️  REMAINING STEPS:
1. Configure API keys in .env
2. Run: adversarial check (to verify keys)
3. Try: adversarial quickstart (guided first workflow)

Ready to configure API keys now? (Y/n)"
```

---

## Integration Patterns

### Pattern 1: Full Automation (User Has Everything Ready)

```
1. Check prerequisites
2. Install aider-chat
3. Install adversarial-workflow
4. Run adversarial init --interactive
5. Collect API keys interactively
6. Run adversarial check
7. Offer adversarial quickstart
```

### Pattern 2: Partial Automation (Missing Prerequisites)

```
1. Check prerequisites → aider missing
2. Inform user about missing dependency
3. Ask if should install now
4. Install aider-chat
5. Install adversarial-workflow
6. Run adversarial init
7. Create .env.example (defer API key config)
8. List remaining manual steps
```

### Pattern 3: Manual Configuration (User Prefers Control)

```
1. Check prerequisites → list what's needed
2. Ask user to confirm they have everything
3. Install adversarial-workflow only
4. Run adversarial init (non-interactive)
5. Provide instructions for manual .env setup
6. Wait for user to configure
7. When ready, run adversarial check
```

### Pattern 4: Recovery from Failure

```
1. Installation fails → capture error
2. Analyze error:
   - Missing dependency? Install it
   - Package bug? Offer workaround
   - Platform issue? Suggest WSL
3. Attempt fix
4. Retry installation
5. If still fails → report to user with details
6. Offer manual alternative
```

---

## Troubleshooting

### "Command not found: adversarial"

**Diagnosis:**
- Not installed in current environment
- Installed in different Python environment
- PATH issue (especially in WSL)

**Solution:**
```bash
# Check if installed
pip list | grep adversarial

# Find installation location
which adversarial

# If in WSL, update PATH
export PATH="$HOME/.local/bin:$PATH"

# Or use python -m instead
python -m adversarial_workflow --version
```

### "adversarial init" fails with cryptic error

**Diagnosis:**
- Missing template files (package bug)
- Permission denied (directory not writable)
- Not a git repository

**Solution:**
```bash
# Check package integrity
python -c "from pathlib import Path; import adversarial_workflow; print(Path(adversarial_workflow.__file__).parent / 'templates')"

# Check git
git status

# Check permissions
ls -ld .
```

### "No module named adversarial_workflow.__main__"

**Diagnosis:**
- Older version (< 0.2.2) doesn't have __main__.py
- Incorrect Python environment

**Solution:**
```bash
# Check version
pip show adversarial-workflow

# If < 0.2.2, upgrade
pip install --upgrade adversarial-workflow

# Use CLI instead
adversarial --version
```

---

## Best Practices for Agents

### 1. Progressive Disclosure

Don't overwhelm the user. Reveal information progressively:

```
Step 1: "Installing adversarial-workflow..."
Step 2: "Need to install prerequisite: aider-chat"
Step 3: "Ready to configure API keys?"
```

Not all at once:
```
❌ "Need to install X, Y, Z, configure A, B, C, and also..."
```

### 2. Fail Fast, Fail Loud

If something is wrong, STOP immediately and inform user:

```
Agent: "❌ STOPPED: aider-chat installation failed

ERROR: [actual error message]

I cannot continue without aider-chat. Options:
1. Troubleshoot the error together
2. Try alternative installation method
3. Defer adversarial-workflow installation

What would you like to do?"
```

### 3. Leave Breadcrumbs

Document what you did for future reference:

Create `INTEGRATION_NOTES.md`:
```markdown
# adversarial-workflow Integration

**Date:** 2025-10-16
**Agent:** [Your name]
**Version:** 0.2.2

## What Worked
- ✅ Installed aider-chat v0.XX.X
- ✅ Installed adversarial-workflow v0.2.2
- ✅ Created .adversarial/ structure
- ✅ Configured API keys (both Anthropic + OpenAI)

## What Didn't Work
- ⚠️ Had to install aider manually (not documented in user request)

## Workarounds Applied
- None needed

## Next Steps for User
1. Run: adversarial quickstart
2. Review: docs/USAGE.md
3. Try first workflow

## Files Created
- .adversarial/config.yml
- .adversarial/scripts/ (3 scripts)
- .aider.conf.yml
- .env (with actual keys)
- .env.example (template)
```

### 4. Bias Toward Asking

When in doubt, ASK the user:

```
✅ GOOD:
"The package needs aider-chat but it's not installed. Install now? (Y/n)"

❌ BAD:
[Silently installs aider without asking]
```

### 5. Test Incrementally

Verify each step before proceeding:

```python
# ✅ Good
install_aider()
verify_aider()  # Test it works
install_adversarial()
verify_adversarial()  # Test it works

# ❌ Bad
install_aider()
install_adversarial()
[Hope everything works]
```

---

## Integration Success Checklist

Before marking integration as complete, verify:

- [ ] adversarial-workflow installed and version correct
- [ ] aider-chat installed and accessible
- [ ] Git repository initialized
- [ ] .adversarial/ directory structure created
- [ ] All 3 workflow scripts present and executable
- [ ] .aider.conf.yml created
- [ ] .env.example created (or .env with actual keys)
- [ ] .env added to .gitignore
- [ ] `adversarial check` passes (or lists remaining steps)
- [ ] User knows next steps
- [ ] Integration documented

---

## Example Integration Session

Here's a complete successful integration:

```
User: "Install adversarial-workflow in this project"

Agent: "I'll install adversarial-workflow. Let me first check prerequisites...

✅ Python 3.11 detected
✅ Git repository detected
❌ aider-chat not found (required dependency)
❌ API keys needed (Anthropic or OpenAI)

Before installing adversarial-workflow, I need to:
1. Install aider-chat (prerequisite)
2. Set up API keys (~$0.02-0.10 per workflow)

Proceed? (Y/n)"

User: "Yes"

Agent: "Installing aider-chat...
✅ aider-chat v0.XX.X installed

Installing adversarial-workflow...
✅ adversarial-workflow v0.2.2 installed

Initializing in current project...
✅ Created .adversarial/ directory structure

Now I need your API keys. Do you have them ready?
(If not, I'll create a template and you can add them later)

Ready to add keys now? (Y/n)"

User: "Yes"

Agent: "Great! I'll collect them securely.

Paste your Anthropic API key (starts with sk-ant-):
[User pastes]
✅ Format validated

Paste your OpenAI API key (starts with sk-proj-):
[User pastes]
✅ Format validated

Creating .env file... ✅
Added .env to .gitignore... ✅

Running final verification...

✅ Installation complete!

VERIFICATION:
✅ adversarial-workflow v0.2.2
✅ aider v0.XX.X
✅ All configuration files created
✅ API keys configured
✅ All checks passed

NEXT STEPS:
Try your first workflow:
  adversarial quickstart

Or read the guide:
  https://github.com/movito/adversarial-workflow

Ready to run quickstart now? (Y/n)"
```

---

## Advanced: Handling Edge Cases

### Multiple Python Environments

```bash
# User might have multiple Python versions
# Always use explicit path to pip/python

# ❌ Ambiguous
pip install adversarial-workflow

# ✅ Explicit
python3.11 -m pip install adversarial-workflow
```

### Behind Corporate Proxy

```bash
# May need proxy configuration
pip install --proxy=http://proxy:port adversarial-workflow
```

### Virtual Environment Detection

```python
import sys

def is_venv():
    return sys.prefix != sys.base_prefix

if not is_venv():
    print("⚠️  Not in virtual environment")
    print("   Recommend: python -m venv venv && source venv/bin/activate")
```

---

## Resources

- **Package Repository**: https://github.com/movito/adversarial-workflow
- **Issue Tracker**: https://github.com/movito/adversarial-workflow/issues
- **Agent Experience Report**: `.agent-context/AGENT_EXPERIENCE_ADVERSARIAL_WORKFLOW.md` (this package)
- **aider Documentation**: https://aider.chat/docs/

---

## Feedback

If you're an AI agent that has integrated this package, please consider:
1. Filing issues for any problems encountered
2. Suggesting improvements to this guide
3. Sharing your integration approach

This guide is maintained based on real-world agent integration experiences.

---

**Last Updated:** 2025-10-16
**Guide Version:** 1.0
**Package Version:** 0.2.2
