# ADR-0007: YAML + .env Configuration Pattern

**Status**: Accepted

**Date**: 2025-10-15 (v0.1.0)

**Deciders**: Fredrik Matheson

## Context

The adversarial workflow requires configuration at multiple levels:
- Model selection (which AI models for Evaluator)
- Directory paths (where tasks, logs, artifacts are stored)
- Test commands (project-specific test execution)
- Workflow behavior (auto-run, git integration, artifact saving)
- API authentication (OpenAI, Anthropic API keys)

### Configuration Requirements

**User-Facing Settings:**
- Must be easy to read and edit manually
- Should be version-controlled (committed to git)
- Need clear documentation/comments
- Should work across different environments
- Must be project-specific (not global)

**Secrets (API Keys):**
- Must NEVER be committed to git
- Should support multiple providers (OpenAI, Anthropic)
- Need to work with local development and CI/CD
- Should follow industry standards
- Must be easy to rotate/update

**Script Access:**
- Bash scripts need to read configuration
- No complex dependencies for parsing
- Fast loading (sub-second)
- Minimal error surface
- Support for defaults

### Forces at Play

**Security:**
- API keys are sensitive credentials
- Accidental git commits are a real risk
- Different keys for dev/staging/production
- Team members may have different keys

**Simplicity:**
- Developers need to understand configuration quickly
- Minimal learning curve for common formats
- Standard tooling support (editors, linters)
- Easy to document and explain

**Bash Script Constraints:**
- Core workflow uses Bash scripts (ADR-0002)
- Need simple parsing (no complex libraries)
- Standard Unix tools only (grep, awk)
- Must work on macOS, Linux, WSL

**Best Practices:**
- Industry standard for configuration files
- Clear separation: config vs secrets
- Support for comments and documentation
- Version control friendly

### Problem Statement

How do we:
1. Store workflow configuration in a readable format
2. Keep API keys secure and out of version control
3. Enable simple parsing from Bash scripts
4. Follow industry best practices
5. Make setup obvious for new users

## Decision

Use **YAML for workflow configuration** and **.env for API keys**, with clear separation of concerns and simple grep/awk parsing from Bash scripts.

### Two-File Configuration

**`.adversarial/config.yml` - Workflow Configuration**

```yaml
# Adversarial Workflow Configuration

# Model Configuration
evaluator_model: gpt-4o

# Directory Structure
task_directory: tasks/
log_directory: .adversarial/logs/
artifacts_directory: .adversarial/artifacts/

# Test Configuration
test_command: pytest

# Workflow Settings
auto_run: false
git_integration: true
save_artifacts: true
```

**Purpose:** Project-specific workflow settings
**Version Control:** Yes, committed to git
**Scope:** Non-sensitive configuration
**Format:** YAML (human-readable, commented)

**`.env` - API Keys (Secrets)**

```bash
# Adversarial Workflow - API Keys Configuration

# Anthropic API Key (for Claude 3.5 Sonnet)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# OpenAI API Key (for GPT-4o)
OPENAI_API_KEY=sk-proj-your-key-here
```

**Purpose:** Sensitive API credentials
**Version Control:** No, added to .gitignore
**Scope:** Secrets only
**Format:** Shell environment variables

**`.env.example` - Template (Committed)**

```bash
# Adversarial Workflow - API Keys Configuration
# Copy this to .env and add your actual keys

ANTHROPIC_API_KEY=your-anthropic-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

**Purpose:** Example/template for users
**Version Control:** Yes, shows required keys
**Scope:** Documentation

### Why YAML for Config?

**1. Human-Readable**
```yaml
# ✅ Clear and obvious
evaluator_model: gpt-4o
task_directory: tasks/
```

vs JSON:
```json
{
  "evaluator_model": "gpt-4o",  // ❌ Quotes, commas, no comments
  "task_directory": "tasks/"
}
```

**2. Comments Support**
```yaml
# Test Configuration
# Use your project's test command
test_command: pytest  # Default: pytest
```

**3. Standard Format**
- Widely used (Kubernetes, CI/CD, Docker Compose)
- Editor support (syntax highlighting, validation)
- Familiar to most developers

**4. Simple Values**
- No nesting needed (flat structure)
- String values (no types to worry about)
- Easy to parse with grep/awk

**5. .yml Extension**
- Standard file extension
- Recognized by tools and editors
- Clear purpose from filename

### Why .env for Secrets?

**1. Industry Standard**
- Used by virtually all frameworks (Rails, Django, Node.js)
- Standard for 12-factor apps
- Well-understood pattern

**2. Git Exclusion**
- Automatically added to .gitignore
- Standard pattern: commit .env.example, ignore .env
- Reduces risk of accidental exposure

**3. Shell-Native**
```bash
# Simple loading in Bash
export $(grep -v '^#' .env | xargs)
# Now all keys are in environment
```

**4. Tool Support**
- Works with docker-compose
- Supported by CI/CD systems
- Compatible with dotenv libraries

**5. Per-Environment**
- Each developer/environment has own .env
- Easy to have .env.production, .env.staging, etc.
- No conflicts in version control

### Simple Bash Parsing

**Loading .env:**
```bash
# Load environment variables from .env
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi
```

**Reading config.yml:**
```bash
# Parse YAML with grep and awk (simple values only)
EVALUATOR_MODEL=$(grep 'evaluator_model:' .adversarial/config.yml | awk '{print $2}')
TASK_DIR=$(grep 'task_directory:' .adversarial/config.yml | awk '{print $2}')
TEST_CMD=$(grep 'test_command:' .adversarial/config.yml | sed 's/test_command: //')
```

**Why this works:**
- Flat YAML structure (no nesting)
- Simple key: value pairs
- No arrays or complex types
- Standard Unix tools (grep, awk, sed)

### Separation of Concerns

| Concern | config.yml | .env |
|---------|-----------|------|
| **Purpose** | Workflow settings | API credentials |
| **Security** | Public | Secret |
| **Git** | Committed | Ignored |
| **Scope** | Project behavior | Authentication |
| **Updates** | Rare (setup once) | Occasional (key rotation) |
| **Examples** | Model, directories, test command | API keys only |

### Setup Flow

1. **Package install** creates templates:
   ```
   .adversarial/config.yml  (rendered from template)
   .env.example             (copied to project root)
   ```

2. **User setup** (first time):
   ```bash
   # Copy template
   cp .env.example .env

   # Edit with actual keys
   vim .env
   ```

3. **Git configuration** (automatic):
   ```gitignore
   # .gitignore (added by adversarial init)
   .env
   .adversarial/logs/
   .adversarial/artifacts/
   ```

4. **Scripts load both**:
   ```bash
   # Load secrets
   export $(grep -v '^#' .env | xargs)

   # Load config
   EVALUATOR_MODEL=$(grep 'evaluator_model:' .adversarial/config.yml | awk '{print $2}')
   ```

## Consequences

### Positive

**Clarity:**
- ✅ **Clear separation**: Config vs secrets, obvious from filenames
- ✅ **Standard formats**: YAML and .env are industry standards
- ✅ **Self-documenting**: Comments explain each setting
- ✅ **Version-control safe**: .env excluded, .env.example included

**Security:**
- ✅ **No accidental commits**: .env in .gitignore by default
- ✅ **Per-environment**: Each user/env has own .env
- ✅ **Key rotation**: Easy to update .env without changing config
- ✅ **Secrets-only in .env**: Only sensitive data, not mixed with config

**Usability:**
- ✅ **Easy to edit**: Plain text, any editor
- ✅ **Easy to understand**: Human-readable formats
- ✅ **Easy to debug**: cat config.yml shows settings
- ✅ **Copy-paste setup**: cp .env.example .env

**Technical:**
- ✅ **Simple parsing**: grep/awk for YAML, native shell for .env
- ✅ **No dependencies**: Standard Unix tools only
- ✅ **Fast loading**: Sub-second parsing
- ✅ **Cross-platform**: Works on macOS, Linux, WSL

### Negative

**YAML Limitations:**
- ⚠️ **Flat structure only**: Nesting not supported by grep/awk parsing
- ⚠️ **Simple values only**: No arrays, objects, or complex types
- ⚠️ **Manual parsing**: grep/awk is brittle for complex YAML
- ⚠️ **Type-less**: Everything is a string (no booleans, numbers)

**.env Limitations:**
- ⚠️ **Shell syntax**: Must follow shell variable rules (no spaces around =)
- ⚠️ **No nesting**: Flat key-value only
- ⚠️ **Manual management**: Users must create .env from .env.example
- ⚠️ **Error-prone**: Easy to forget .env or misconfigure

**Two-File Complexity:**
- ⚠️ **Mental overhead**: Must understand two config files
- ⚠️ **Setup friction**: Extra step to create .env
- ⚠️ **Duplication risk**: Similar info in config.yml and .env.example
- ⚠️ **Documentation burden**: Must explain both files

**Bash Parsing Fragility:**
- ⚠️ **Brittle parsing**: grep/awk breaks with complex YAML
- ⚠️ **No validation**: No schema validation for YAML
- ⚠️ **Silent failures**: Typos in keys return empty strings
- ⚠️ **Whitespace issues**: Spaces/tabs can break parsing

### Neutral

**When This Works Well:**
- 📊 Simple, flat configuration (most cases)
- 📊 Standard Unix environments (macOS, Linux, WSL)
- 📊 API-key based authentication
- 📊 Single-project setups

**When Alternatives Might Be Better:**
- 📊 Complex nested configuration (consider JSON)
- 📊 Type-safe config needed (consider TOML)
- 📊 Non-Bash workflows (consider JSON/TOML with parsers)
- 📊 Global configuration (consider ~/.config/)

## Alternatives Considered

### Alternative 1: All-in-One YAML

**Structure:** Everything in config.yml

```yaml
evaluator_model: gpt-4o
anthropic_api_key: sk-ant-...
openai_api_key: sk-...
```

**Rejected because:**
- ❌ **Security risk**: API keys in version control
- ❌ **No industry standard**: Not how secrets are handled
- ❌ **Sharing friction**: Can't share config without exposing keys
- ❌ **Key rotation**: Must edit config file (not just .env)

### Alternative 2: JSON Configuration

**Structure:** .adversarial/config.json

```json
{
  "evaluator_model": "gpt-4o",
  "task_directory": "tasks/",
  "test_command": "pytest"
}
```

**Rejected because:**
- ❌ **No comments**: JSON doesn't support comments
- ❌ **Less readable**: Quotes, commas, braces clutter
- ❌ **Brittle editing**: Easy to break JSON syntax
- ❌ **Parsing complexity**: Need jq or python for bash scripts

### Alternative 3: TOML Configuration

**Structure:** .adversarial/config.toml

```toml
[model]
evaluator = "gpt-4o"

[directories]
tasks = "tasks/"
logs = ".adversarial/logs/"
```

**Rejected because:**
- ❌ **Less familiar**: Not as widely used as YAML
- ❌ **Parsing complexity**: No standard Unix tool for TOML
- ❌ **Overkill**: Don't need sections/nesting
- ❌ **Learning curve**: Another format to learn

### Alternative 4: Python Config File

**Structure:** .adversarial/config.py

```python
EVALUATOR_MODEL = "gpt-4o"
TASK_DIRECTORY = "tasks/"
TEST_COMMAND = "pytest"
```

**Rejected because:**
- ❌ **Execution risk**: Running Python files is dangerous
- ❌ **Language-specific**: Ties config to Python
- ❌ **Parsing complexity**: Need python to read from bash
- ❌ **Not declarative**: Code execution, not pure data

### Alternative 5: Environment Variables Only

**Structure:** Everything in .env

```bash
EVALUATOR_MODEL=gpt-4o
TASK_DIRECTORY=tasks/
TEST_COMMAND=pytest
ANTHROPIC_API_KEY=sk-ant-...
```

**Rejected because:**
- ❌ **No separation**: Config mixed with secrets
- ❌ **Not version-controlled**: Can't commit workflow settings
- ❌ **Limited documentation**: Shell comments less expressive
- ❌ **Non-standard**: Config usually in structured files

### Alternative 6: Global Config (~/.config/)

**Structure:** Global configuration in home directory

```
~/.config/adversarial-workflow/config.yml
~/.config/adversarial-workflow/.env
```

**Rejected because:**
- ❌ **Not per-project**: Can't have project-specific settings
- ❌ **Team friction**: Different settings per team member
- ❌ **Version control**: Can't commit project config
- ❌ **Discovery issue**: Less obvious where config lives

## Real-World Results

### adversarial-workflow Development

**Setup experience:**
- Clear: Two files with obvious purposes
- Fast: cp .env.example .env, edit keys, done
- Safe: .env never committed (checked in git log)

**Daily usage:**
- Easy to change models (edit config.yml)
- Easy to rotate keys (edit .env)
- No confusion about which file for what

**Issues encountered:**
- None significant
- grep/awk parsing works reliably for flat YAML
- .env loading is instant

### User Feedback (Dogfooding)

**Positive:**
- "Obvious where to put API keys"
- ".env.example made setup clear"
- "config.yml comments are helpful"

**Friction points:**
- "Forgot to create .env" → Fixed: Better error messages in scripts
- "Not sure which API keys needed" → Fixed: Detailed .env.example

## Related Decisions

- ADR-0002: Bash and Aider foundation (why bash parsing matters)
- ADR-0004: Template-based initialization (how config files are created)
- ADR-0009: Interactive onboarding (alternative setup approach)

## References

- [config.yml.template](../../../adversarial_workflow/templates/config.yml.template) - Configuration template
- [.env.example.template](../../../adversarial_workflow/templates/.env.example.template) - API key template
- [YAML spec](https://yaml.org/) - YAML format specification
- [The Twelve-Factor App](https://12factor.net/config) - Configuration best practices
- [Bash script config loading](../../../adversarial_workflow/templates/evaluate_plan.sh.template#L12-L73) - Implementation example

## Revision History

- 2025-10-15: Initial decision (v0.1.0)
- 2025-10-20: Documented as ADR-0007
