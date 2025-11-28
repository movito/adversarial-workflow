# TASK-PACKAGING-001: Onboarding Enhancement

**Task ID**: TASK-PACKAGING-001-ONBOARDING
**Status**: READY_FOR_IMPLEMENTATION
**Priority**: HIGH (User experience critical)
**Created**: 2025-10-15
**Dependencies**: v0.1.0 complete

---

## Overview

Enhance the adversarial-workflow package onboarding to be delightful and educational. Focus on API key setup guidance, interactive wizards, and quick success paths.

---

## User Requirements

1. ✅ Explain the dual-model system (Implementation + Evaluation)
2. ✅ Explain Anthropic API (Claude 3.5 Sonnet for implementation)
3. ✅ Explain OpenAI API (GPT-4o for evaluation)
4. ✅ Provide links to get API keys
5. ✅ Offer to create .env file (default: yes)
6. ✅ Show alternative manual setup instructions

---

## API Key Education

### What Users Need to Understand

**The Two-Agent System:**
```
┌─────────────────────────────────────────────────────┐
│ Adversarial Workflow (Phantom Work Prevention)     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Agent 1: IMPLEMENTATION (aider)                   │
│  ├─ Writes code based on your task                │
│  ├─ Recommended: Claude 3.5 Sonnet (Anthropic)     │
│  └─ Alternative: GPT-4o (OpenAI)                   │
│                                                     │
│  Agent 2: EVALUATOR (aider)                        │
│  ├─ Reviews code for quality/correctness           │
│  ├─ Recommended: GPT-4o (OpenAI)                   │
│  └─ Alternative: Claude 3.5 Sonnet (Anthropic)     │
│                                                     │
│  Why two models? Adversarial = different            │
│  perspectives catch more issues!                    │
└─────────────────────────────────────────────────────┘
```

**Setup Options:**

1. **RECOMMENDED** (Best Quality, Different Perspectives):
   - Implementation: Claude 3.5 Sonnet (Anthropic API)
   - Evaluation: GPT-4o (OpenAI API)
   - Cost: ~$0.02-0.10 per workflow
   - **Requires: Both API keys**

2. **OpenAI Only** (Simpler Setup):
   - Implementation: GPT-4o (OpenAI API)
   - Evaluation: GPT-4o (OpenAI API)
   - Cost: ~$0.05-0.15 per workflow
   - **Requires: OpenAI API key only**

3. **Anthropic Only** (Alternative):
   - Implementation: Claude 3.5 Sonnet (Anthropic API)
   - Evaluation: Claude 3.5 Sonnet (Anthropic API)
   - Cost: ~$0.02-0.10 per workflow
   - **Requires: Anthropic API key only**

---

## Interactive Onboarding Flow

### Command: `adversarial init --interactive`

```
🚀 Welcome to Adversarial Workflow!

This tool helps you write better code using AI-powered code review.
It uses TWO AI models (implementation + evaluation) to catch issues.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1 of 4: Choose Your Setup

Which API keys do you have?

  1. Both Anthropic + OpenAI (RECOMMENDED - best quality)
  2. OpenAI only (simpler setup)
  3. Anthropic only (alternative)
  4. I'll configure later

Your choice [1]: _

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[If choice 1 - Both APIs]

Step 2 of 4: Anthropic API Key

Claude 3.5 Sonnet will write your code (implementation agent).

Need an API key?
  1. Go to: https://console.anthropic.com/settings/keys
  2. Click "Create Key"
  3. Copy the key (starts with "sk-ant-")

Paste your Anthropic API key (or press Enter to skip): _

✅ API key validated! ($5.00 credit remaining)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 3 of 4: OpenAI API Key

GPT-4o will review your code (evaluator agent).

Need an API key?
  1. Go to: https://platform.openai.com/api-keys
  2. Click "+ Create new secret key"
  3. Copy the key (starts with "sk-proj-" or "sk-")

Paste your OpenAI API key (or press Enter to skip): _

✅ API key validated! ($10.00 credit remaining)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 4 of 4: Configuration

Project name: [my-project] _
Test framework: [pytest] / npm test / other: _
Task directory: [tasks/] _

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Setup Complete!

Created:
  ✓ .env (with your API keys - added to .gitignore)
  ✓ .adversarial/config.yml
  ✓ .adversarial/scripts/ (3 workflow scripts)
  ✓ .aider.conf.yml (aider configuration)

Your configuration:
  Implementation: Claude 3.5 Sonnet (Anthropic)
  Evaluator: GPT-4o (OpenAI)
  Cost per workflow: ~$0.02-0.10

Next steps:
  1. Run: adversarial quickstart
     (creates example task and runs first workflow)

  2. Or create your own:
     - Create: tasks/my-first-task.md
     - Run: adversarial evaluate tasks/my-first-task.md

  3. Read the guide: https://github.com/movito/adversarial-workflow

Need help? Run: adversarial doctor
```

---

## Command: `adversarial quickstart`

```
🚀 Quick Start: Your First Adversarial Workflow

Let me guide you through your first workflow in 3 steps.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[If .env not found]

⚠️  API keys not configured yet.

Let's set them up now (takes 2 minutes):

Which API keys do you have?
  1. Both Anthropic + OpenAI (RECOMMENDED)
  2. OpenAI only
  3. Anthropic only

Your choice [1]: _

[... interactive API key setup ...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: Creating Example Task

I'll create a sample bug fix task for you to try.

✅ Created: tasks/example-bug-fix.md

Let's look at it:

┌─────────────────────────────────────────────────────┐
│ # Task: Fix off-by-one error in list processing    │
│                                                     │
│ ## Problem                                          │
│ The `process_items()` function misses the last     │
│ item in the list.                                   │
│                                                     │
│ ## Expected Behavior                                │
│ Should process all items including the last one.    │
│                                                     │
│ ## Implementation Plan                              │
│ 1. Fix the range in the for loop                   │
│ 2. Add test for edge case                          │
└─────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 2: Evaluating the Plan

Running Phase 1: Plan Evaluation
This asks GPT-4o to review the task plan...

⏳ Calling OpenAI API... (this takes ~10 seconds)

✅ Evaluator Response:

┌─────────────────────────────────────────────────────┐
│ APPROVED                                            │
│                                                     │
│ The task is well-defined with clear acceptance     │
│ criteria. The implementation plan is sound.         │
│                                                     │
│ Suggestions:                                        │
│ - Consider adding a test for empty list            │
│ - Document the fix in a comment                    │
└─────────────────────────────────────────────────────┘

Cost: $0.02

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 3: Next Steps

You've completed your first adversarial workflow evaluation! 🎉

What you learned:
  ✓ How to create a task file
  ✓ How to run plan evaluation
  ✓ How the evaluator provides feedback

Try the full workflow:
  1. Implement the fix (or let Claude do it)
  2. Run: adversarial review (Phase 3: Code Review)
  3. Run: adversarial validate (Phase 4: Test Validation)

Learn more:
  - Read: docs/USAGE.md
  - Examples: adversarial examples
  - Help: adversarial --help
```

---

## Enhanced `adversarial check` Output

```
🔍 Checking adversarial workflow setup...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Git Repository
  ✅ Git repository detected
  ✅ Clean working directory

Dependencies
  ✅ Aider installed (version 0.86.1)
  ✅ Python 3.12.12

API Keys
  ✅ ANTHROPIC_API_KEY configured ($5.00 remaining)
  ✅ OPENAI_API_KEY configured ($10.00 remaining)

Configuration
  ✅ .adversarial/config.yml valid
  ✅ Implementation: claude-3-5-sonnet-20241022
  ✅ Evaluator: gpt-4o

Scripts
  ✅ evaluate_plan.sh (executable)
  ✅ review_implementation.sh (executable)
  ✅ validate_tests.sh (executable)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ All checks passed! Your setup is ready.

Estimated cost per workflow: $0.02-0.10

Try it: adversarial quickstart
```

**With Issues:**

```
🔍 Checking adversarial workflow setup...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Git Repository
  ✅ Git repository detected

Dependencies
  ✅ Aider installed (version 0.86.1)

API Keys
  ❌ ANTHROPIC_API_KEY not set
  ⚠️  OPENAI_API_KEY not set

Configuration
  ✅ .adversarial/config.yml valid

Scripts
  ✅ All scripts executable

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ Setup incomplete (1 error, 1 warning)

How to fix:

  1. Set up API keys (REQUIRED):
     Run: adversarial init --interactive

     Or manually:
       - Anthropic: https://console.anthropic.com/settings/keys
       - OpenAI: https://platform.openai.com/api-keys
       - Add to .env file (copy from .env.example)

  2. Need help?
     Run: adversarial doctor --fix

Quick fix: adversarial init --interactive
```

---

## .env File Creation

**Interactive Prompt:**

```
Do you want me to create the .env file with your API keys?

This will create .env in your project root with:
  ANTHROPIC_API_KEY=sk-ant-***
  OPENAI_API_KEY=sk-proj-***

The file will be added to .gitignore (won't be committed to git).

Create .env file? [Y/n]: _
```

**If Yes:**
```
✅ Created .env with your API keys
✅ Added .env to .gitignore

Your API keys are safe and won't be committed to git.
```

**If No:**
```
No problem! Create .env manually:

  1. Copy the example:
     cp .env.example .env

  2. Edit .env and add your keys:

     # Anthropic API (for Claude 3.5 Sonnet)
     ANTHROPIC_API_KEY=sk-ant-your-key-here

     # OpenAI API (for GPT-4o)
     OPENAI_API_KEY=sk-proj-your-key-here

  3. Verify setup:
     adversarial check

Get API keys:
  - Anthropic: https://console.anthropic.com/settings/keys
  - OpenAI: https://platform.openai.com/api-keys
```

---

## Implementation Tasks

### Phase 1: Enhanced `init --interactive` (HIGH Priority)
- [ ] Add `--interactive` flag to `init` command
- [ ] Implement API key setup wizard
- [ ] Add API key validation (test with actual API call)
- [ ] Add .env file creation (with confirmation)
- [ ] Update .env.example template with better comments
- [ ] Add educational explanations about two-model system

### Phase 2: `quickstart` Command (HIGH Priority)
- [ ] Implement `quickstart` command
- [ ] Create example task template (bug fix)
- [ ] Auto-run first evaluation
- [ ] Show tutorial-style output
- [ ] Detect missing API keys and trigger setup

### Phase 3: Enhanced `check` Command (MEDIUM Priority)
- [ ] Improve output formatting (boxes, colors)
- [ ] Add API credit balance checking
- [ ] Add `--fix` flag for automatic fixes
- [ ] Better error messages with exact commands
- [ ] Add `doctor` alias for `check`

### Phase 4: Examples System (MEDIUM Priority)
- [ ] Implement `examples` command
- [ ] Create 3-4 example task templates
- [ ] Add `examples list` subcommand
- [ ] Add `examples create <name>` subcommand
- [ ] Bundle examples in package

### Phase 5: Configuration Wizard (LOW Priority)
- [ ] Implement `config --setup` wizard
- [ ] Add model selection UI
- [ ] Add test command auto-detection
- [ ] Add `config --edit` to open in editor

---

## Educational Content

### API Key Setup Pages

**Anthropic (Claude):**
- URL: https://console.anthropic.com/settings/keys
- Steps:
  1. Sign up for Anthropic account (if needed)
  2. Go to Settings → API Keys
  3. Click "Create Key"
  4. Copy key (starts with `sk-ant-`)
  5. Paste into adversarial-workflow setup

**OpenAI (GPT-4o):**
- URL: https://platform.openai.com/api-keys
- Steps:
  1. Sign up for OpenAI account (if needed)
  2. Go to API Keys page
  3. Click "+ Create new secret key"
  4. Copy key (starts with `sk-proj-` or `sk-`)
  5. Paste into adversarial-workflow setup

### Cost Estimates

**Per Workflow (Typical):**
- Plan Evaluation: $0.01-0.03
- Code Review: $0.01-0.05
- Test Validation: $0.00-0.02
- **Total: $0.02-0.10**

**Monthly (10 workflows/week):**
- ~40 workflows: $0.80-4.00/month
- Very affordable for professional use

---

## User Experience Goals

**First 60 Seconds:**
1. User runs `pip install adversarial-workflow`
2. User runs `adversarial quickstart`
3. User is guided through API setup (if needed)
4. User sees successful evaluation
5. **User feels: "That was easy and educational!"**

**First 5 Minutes:**
1. User understands two-model system
2. User has API keys configured
3. User has seen example workflow
4. User knows next steps
5. **User feels: "I'm ready to use this on my project!"**

**First Hour:**
1. User has run workflow on real task
2. User has seen evaluation feedback
3. User trusts the system
4. **User feels: "This is worth the cost/effort!"**

---

## Success Criteria

- [ ] New user can get started in <3 minutes
- [ ] API key setup is educational, not frustrating
- [ ] `.env` file created by default (safe defaults)
- [ ] Clear guidance on which APIs to use
- [ ] Working example runs successfully
- [ ] User understands cost before spending
- [ ] Zero blockers to first success

---

## Files to Modify

1. `adversarial_workflow/cli.py` - Main implementation
2. `adversarial_workflow/templates/.env.example.template` - Better comments
3. `adversarial_workflow/templates/example-task.md.template` - New template
4. `README.md` - Update quick start section
5. `docs/INSTALLATION.md` - Add API key guidance

---

## Testing Plan

1. **Fresh User Testing**:
   - Test in clean VM/container
   - No API keys configured
   - Follow onboarding flow
   - Time to first success: <5 minutes

2. **API Key Validation**:
   - Test with valid keys (success)
   - Test with invalid keys (helpful error)
   - Test with one key only (fallback)
   - Test with no keys (educational message)

3. **Edge Cases**:
   - Already initialized (offer overwrite)
   - Not a git repo (clear error)
   - No internet (graceful degradation)
   - API rate limits (helpful message)

---

## Future Enhancements (Phase 5+)

- [ ] Interactive tutorial (`adversarial tutorial`)
- [ ] Template selection (`--template python/js/go`)
- [ ] Model switching (`adversarial config --model`)
- [ ] Cost tracking (`adversarial cost --show`)
- [ ] Web UI for configuration
- [ ] Video walkthrough (embed in CLI)

---

**Document Created**: 2025-10-15
**Status**: READY_FOR_IMPLEMENTATION
**Estimated Effort**: 8-12 hours (Phase 1-3)
**Priority**: HIGH (User experience critical)
