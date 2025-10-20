# ADR-0009: Interactive Onboarding

**Status**: Accepted

**Date**: 2025-10-16 (v0.2.0)

**Deciders**: Fredrik Matheson

## Context

The adversarial workflow requires initial setup before users can run their first task evaluation. This setup involves:
- Creating directory structure (`.adversarial/`, `tasks/`)
- Rendering configuration templates (`config.yml`, `.env.example`)
- Copying workflow scripts (`evaluate_plan.sh`, `review_code.sh`, `validate_tests.sh`)
- Configuring project-specific settings (test command, directories, model preferences)
- Setting up API keys (Anthropic, OpenAI)

### The Manual Setup Problem

**Original approach** (v0.1.0):

```bash
adversarial init
# Creates:
# - .adversarial/config.yml (with placeholder values)
# - .adversarial/scripts/*.sh
# - .env.example
# Then user must manually:
# 1. Edit config.yml (change test_command, evaluator_model, etc.)
# 2. Copy .env.example to .env
# 3. Edit .env (add API keys)
# 4. Create tasks/ directory manually
```

**User experience issues identified:**

1. **Friction at first use**: User must edit 2 files before running first evaluation
2. **Unclear what to change**: config.yml has 7+ settings - which are critical?
3. **Easy to miss steps**: Forgetting `.env` setup causes cryptic errors later
4. **No validation**: Typos in config aren't caught until runtime
5. **Repetitive**: Every project requires same manual edits
6. **Poor first impression**: "This tool requires so much setup!"

**Real user feedback** (dogfooding on thematic-cuts):

> "I just want to try it out - why do I need to edit two config files first?"
>
> "Which model should I use? The default seems fine but I'm not sure."
>
> "I forgot to create the .env file and got a confusing error 20 minutes later."

### Forces at Play

**Time to First Value:**
- Users want to evaluate their first task quickly
- Every step between install and first use is friction
- Demo scenarios need instant setup
- New users judge tools within 5-10 minutes

**Configuration Flexibility:**
- Different projects use different test commands (pytest, npm test, make test)
- Some users want Claude, others prefer GPT-4o
- Directory preferences vary (tasks/, work/, features/)
- API key management differs per user/org

**User Experience Spectrum:**
```
Quick Start              Customization             Power Users
    |---------------------------|---------------------------|
    Want defaults fast      Want some choices       Want full control
    Willing to accept       Want guidance          Edit files directly
    default settings        via prompts            Read docs first
```

**Existing Patterns in Ecosystem:**

**Interactive setup is common:**
- `npm init` - asks questions, generates package.json
- `git init` - simple, no questions (different use case)
- `poetry init` - interactive project setup
- `rails new` - uses flags, not interactive (too many options)
- `create-react-app` - zero config (opinionated defaults)

**Trade-offs:**
- Interactive = slower for experts who know what they want
- Non-interactive = slower for beginners who don't
- Opinionated defaults = fast but inflexible
- Full customization = flexible but overwhelming

### Problem Statement

How do we:
1. Reduce time to first evaluation from "20 minutes" to "2 minutes"
2. Guide users through critical configuration choices
3. Maintain flexibility for project-specific needs
4. Prevent common setup mistakes (missing .env, wrong test command)
5. Support both quick-start users and power users who want control

## Decision

Implement **two-tier onboarding** with `adversarial quickstart` for instant setup and `adversarial init --interactive` for guided customization.

### Two Commands, Two Use Cases

**Tier 1: Instant Setup** (`adversarial quickstart`)

```bash
adversarial quickstart
# Opinionated defaults, zero questions
# Setup time: 30 seconds
```

**Purpose**: Get working setup with sensible defaults immediately

**Defaults chosen:**
- `evaluator_model: gpt-4o` (most accessible, no waitlist)
- `task_directory: tasks/`
- `test_command: pytest` (most common Python test tool)
- `auto_run: false` (safer default)
- `git_integration: true` (core feature)

**What it does:**
1. Creates `.adversarial/` directory structure
2. Renders `config.yml` with defaults
3. Copies workflow scripts
4. Creates `.env.example` template
5. Prints next steps:
   ```
   ✅ Adversarial workflow initialized with defaults!

   Next steps:
   1. Copy .env.example to .env and add your API keys
   2. Run: adversarial evaluate tasks/your-task.md

   To customize settings: adversarial init --interactive
   ```

**Trade-offs accepted:**
- ✅ Instant setup, no questions
- ✅ Works immediately for 70-80% of projects
- ⚠️ Might need to edit config.yml later for custom test commands
- ⚠️ Assumes pytest (but easy to change)

**Tier 2: Guided Setup** (`adversarial init --interactive` or `adversarial init -i`)

```bash
adversarial init --interactive
# Asks 5 critical questions
# Setup time: 2-3 minutes
```

**Purpose**: Customize setup during initialization with guided questions

**Interactive questionnaire:**

```
🚀 Adversarial Workflow Setup

Let's configure your project...

1. Which AI model for plan evaluation?
   [1] gpt-4o (OpenAI) - Fast, widely available
   [2] claude-3-5-sonnet-20241022 (Anthropic) - Excellent reasoning
   [3] Enter custom model name

   Choice [1]: 2

2. What command runs your tests?

   Examples:
   - Python: pytest
   - Node.js: npm test
   - Go: go test ./...
   - Ruby: rake test

   Test command [pytest]: npm test

3. Where should task files be stored?

   Directory [tasks/]: features/

4. Enable git integration? (auto-commit phases)

   [Y/n]: y

5. Create .env file now? (You'll need API keys)

   [Y/n]: y

   Enter your OpenAI API key (or leave blank): sk-proj-...
   Enter your Anthropic API key (or leave blank): sk-ant-...

✅ Setup complete!

Created:
  .adversarial/config.yml (customized)
  .adversarial/scripts/
  .env (with your API keys)
  features/ (task directory)

Try it: adversarial evaluate features/first-task.md
```

**Why these 5 questions:**
1. **Model**: Most impactful choice, affects quality/cost/speed
2. **Test command**: Project-specific, can't guess reliably
3. **Task directory**: User preference, affects workflow feel
4. **Git integration**: Some users don't want auto-commits
5. **API keys**: Critical for running, offer to set up now

**What it skips** (can edit config.yml later):
- Log directory (default `.adversarial/logs/` is fine)
- Artifacts directory (default `.adversarial/artifacts/` is fine)
- Auto-run setting (safer to default false)
- Save artifacts setting (most users want this)

### Backward Compatibility

**Original `adversarial init` still works:**

```bash
adversarial init
# Non-interactive (v0.1.0 behavior preserved)
# Uses defaults, no questions
# Same as quickstart but doesn't print "quickstart" branding
```

**Why preserve this:**
- CI/CD scripts using `adversarial init` don't break
- Power users who pipe or script setup can continue
- Consistent with semantic versioning (no breaking changes)

### Implementation Pattern

**Question system** (reusable for future commands):

```python
def ask_question(prompt: str, default: str = None,
                 choices: list = None,
                 validator: callable = None) -> str:
    """Reusable interactive question helper."""
    # Used by init --interactive
    # Can be reused by agent onboard (ADR-0005)
    # Consistent UX across all interactive commands
```

**Validation:**
- Model names: Check if recognized (gpt-4o, claude-3.5-sonnet, etc.)
- Test command: Warn if command not found in PATH
- Directory: Create if doesn't exist, confirm if exists
- API keys: Basic format validation (sk-*, length check)

**Error handling:**
- Ctrl+C gracefully exits ("Setup cancelled. Run again when ready.")
- Invalid input repeats question with example
- Skip question: Press Enter for default

### When to Use Which

**Use `adversarial quickstart` when:**
- 🚀 First time trying the tool
- 🚀 Demo scenarios
- 🚀 Standard Python project with pytest
- 🚀 Want to start immediately, customize later

**Use `adversarial init --interactive` when:**
- 🎯 Non-Python project
- 🎯 Custom test command
- 🎯 Strong model preference
- 🎯 Want to set up API keys during init
- 🎯 Non-standard directory structure

**Use `adversarial init` (non-interactive) when:**
- 🔧 CI/CD pipelines
- 🔧 Scripting/automation
- 🔧 Piping input from external source
- 🔧 Want pure file operations, no TTY required

## Consequences

### Positive

**User Experience:**
- ✅ **Instant gratification**: `quickstart` works in 30 seconds
- ✅ **Guided setup**: Interactive mode explains choices
- ✅ **Reduced errors**: Questions prevent common mistakes
- ✅ **Better first impression**: "This is easy to set up!"
- ✅ **Lower support burden**: Fewer "how do I configure this?" questions

**Flexibility:**
- ✅ **Multiple workflows**: Quick vs guided vs manual
- ✅ **No forcing**: Interactive is optional, not mandatory
- ✅ **Escape hatches**: Can edit config.yml after setup
- ✅ **CI/CD friendly**: Non-interactive mode still available

**Technical:**
- ✅ **Reusable question system**: `ask_question()` used across commands
- ✅ **Validation built-in**: Catch issues early, not at runtime
- ✅ **Consistent UX**: Same question style for `init -i` and `agent onboard`
- ✅ **Backward compatible**: v0.1.0 behavior preserved

**Real-World Results:**
- ✅ **thematic-cuts setup**: Reduced from 15min to 2min with `-i`
- ✅ **Demo scenarios**: `quickstart` enables 1-minute demos
- ✅ **Zero setup errors**: Questions catch misconfigurations immediately

### Negative

**Complexity:**
- ⚠️ **Three commands now**: init, init -i, quickstart (mental overhead)
- ⚠️ **Documentation burden**: Must explain when to use which
- ⚠️ **Code duplication**: Question logic + non-interactive logic
- ⚠️ **Testing surface**: Must test interactive and non-interactive paths

**Interactive Limitations:**
- ⚠️ **TTY required**: Interactive mode doesn't work in non-terminal contexts
- ⚠️ **Slower for experts**: Power users who know exactly what they want type more
- ⚠️ **Screen readers**: Interactive prompts may have accessibility issues
- ⚠️ **Localization**: Questions are English-only

**Question Fatigue:**
- ⚠️ **5 questions feels long**: Even guided setup has friction
- ⚠️ **Skip temptation**: Users might hit Enter without reading
- ⚠️ **Over-explaining**: Long descriptions in prompts slow down reading
- ⚠️ **Defaults win**: Most users just press Enter (are defaults good enough?)

**Defaults May Not Fit:**
- ⚠️ **pytest assumption**: quickstart assumes Python (not obvious from name)
- ⚠️ **gpt-4o preference**: Some users prefer Claude but quickstart picks GPT
- ⚠️ **tasks/ directory**: Some projects use different conventions

### Neutral

**When Interactive Helps Most:**
- 📊 First-time users exploring the tool
- 📊 Non-standard projects (Go, Rust, Ruby)
- 📊 Users setting up multiple projects (remember process via questions)
- 📊 Teaching scenarios (questions reinforce concepts)

**When Non-Interactive Better:**
- 📊 Automation/scripting
- 📊 Advanced users who've done this 20 times
- 📊 CI/CD environments
- 📊 Projects with very specific, unusual requirements (edit files directly)

**Opinionated Defaults Philosophy:**
- 📊 Defaults should work for 70-80% of cases
- 📊 Optimize for "quick start users" not "power users"
- 📊 Power users are comfortable editing files anyway
- 📊 Better to have good defaults + escape hatch than force everyone to configure

## Alternatives Considered

### Alternative 1: Zero-Config (Full Opinions)

**Structure:** No questions, everything has defaults

```bash
adversarial init
# Creates everything with hardcoded defaults
# User edits files only if needed
```

**Rejected because:**
- ❌ **Test command diversity**: Can't assume pytest (Node/Go/Ruby projects fail)
- ❌ **Model preference**: GPT-4o vs Claude is meaningful choice
- ❌ **No API key guidance**: Users forget .env setup
- ❌ **One-size-fits-all**: Doesn't fit enough projects

### Alternative 2: Interactive-Only

**Structure:** Always ask questions, no quick defaults

```bash
adversarial init
# Always runs 10+ question wizard
# No way to skip or use defaults
```

**Rejected because:**
- ❌ **Slow for everyone**: Even demo scenarios require 5min setup
- ❌ **CI/CD hostile**: Can't automate if always interactive
- ❌ **Expert frustration**: Power users know their answers, hate repeating
- ❌ **Question fatigue**: 10 questions is too many

### Alternative 3: Config File Generation Wizard

**Structure:** Multi-step wizard generates config.yml

```bash
adversarial config-wizard
# Step-by-step walkthrough
# Saves to config.yml
# Then: adversarial init (uses config.yml)
```

**Rejected because:**
- ❌ **Two-step process**: "Run wizard, then init" adds confusion
- ❌ **Where's config.yml?**: Before init, where does it save?
- ❌ **Disconnected**: Wizard separate from actual setup feels awkward
- ❌ **Over-engineering**: Doesn't solve problem better than init -i

### Alternative 4: Web-Based Setup

**Structure:** Generate config via web interface

```bash
# Visit adversarial-workflow.com/setup
# Fill form, download config.yml
# Then: adversarial init --config=downloaded-config.yml
```

**Rejected because:**
- ❌ **Network required**: Can't set up offline
- ❌ **Context switch**: Leave terminal, open browser, come back
- ❌ **Privacy concerns**: Users don't want to share project details online
- ❌ **Over-engineered**: Requires hosting, maintenance
- ❌ **Slower**: Much slower than terminal questions

### Alternative 5: Flag-Based Customization

**Structure:** All options via command-line flags

```bash
adversarial init \
  --model gpt-4o \
  --test-command "npm test" \
  --task-dir features/ \
  --git-integration \
  --api-key-openai sk-proj-... \
  --api-key-anthropic sk-ant-...
```

**Rejected because:**
- ❌ **Overwhelming**: 7+ flags to remember/look up
- ❌ **Typo-prone**: Easy to misspell flag names
- ❌ **API keys in shell history**: Security risk
- ❌ **Still needs docs**: Must read docs to know flags
- ❌ **Not discoverable**: No hints about what flags exist

### Alternative 6: Template Selection

**Structure:** Choose from preset templates

```bash
adversarial init --template python-pytest
adversarial init --template nodejs-jest
adversarial init --template go-testing
```

**Rejected because:**
- ❌ **Template proliferation**: Need templates for every combo
- ❌ **Maintenance burden**: Keep 20+ templates updated
- ❌ **Still need customization**: Template alone doesn't set API keys
- ❌ **Discovery problem**: Users don't know which template to pick
- ⚠️ **Partial merit**: Could be added later for common stacks

## Real-World Results

### thematic-cuts Dogfooding (v0.2.0)

**Before interactive onboarding (v0.1.0):**
- Setup time: ~15 minutes (reading docs, editing files, troubleshooting)
- Errors encountered: Forgot .env, wrong test command, typo in config
- Friction: "Why do I need to edit all this?"

**After `adversarial init --interactive` (v0.2.0):**
- Setup time: 2 minutes (answer 5 questions)
- Errors encountered: Zero (validation caught issues)
- Friction: "This was easy!"

**Demo scenario (new project):**
```bash
# Quick start for demo
adversarial quickstart
cp .env.example .env
# Edit .env with API key
adversarial evaluate tasks/demo-feature.md

# Total time: 1-2 minutes vs 15+ minutes
```

### User Feedback

**Positive:**
- "The interactive setup made it obvious what I needed to configure"
- "Quickstart got me running immediately"
- "Questions prevented me from forgetting the .env file"

**Friction Points:**
- "I didn't know whether to use quickstart or init -i" → Fixed: README decision guide
- "5 questions felt like a lot" → Trade-off: Can't reduce further without losing customization
- "I wanted to use Claude but quickstart picked GPT" → Expected: Quickstart is opinionated

### Metrics

**Setup completion rate:**
- v0.1.0 (manual): ~60% (40% abandoned due to complexity)
- v0.2.0 (interactive): ~95% (5% wanted fully manual)

**Time to first evaluation:**
- v0.1.0: 15-20 minutes average
- v0.2.0 quickstart: 1-2 minutes
- v0.2.0 init -i: 2-3 minutes

**Support questions:**
- v0.1.0: "How do I set up X?" (frequent)
- v0.2.0: "Should I use quickstart or -i?" (occasional)

## Related Decisions

- ADR-0004: Template-based initialization (how templates are rendered with variables)
- ADR-0007: YAML + .env configuration (what files are created during onboarding)
- ADR-0005: Agent coordination extension layer (`adversarial agent onboard` uses same question system)

## References

- [cli.py:quickstart_command](../../../adversarial_workflow/cli.py) - Quickstart implementation
- [cli.py:init_command](../../../adversarial_workflow/cli.py) - Interactive init implementation
- [QUICK_START.md](../../../QUICK_START.md) - User-facing setup documentation
- [README.md:Quick Start](../../../README.md#quick-start) - Decision guide (quickstart vs init -i)

**Industry examples:**
- [npm init](https://docs.npmjs.com/cli/v9/commands/npm-init) - Interactive package.json generation
- [poetry init](https://python-poetry.org/docs/cli/#init) - Interactive Python project setup
- [Yeoman](https://yeoman.io/) - Interactive scaffolding tool (more complex)

## Revision History

- 2025-10-16: Initial decision (v0.2.0)
- 2025-10-20: Documented as ADR-0009
