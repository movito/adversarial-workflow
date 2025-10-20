# ADR-0004: Template-Based Initialization

**Status**: Accepted

**Date**: 2025-10-15 (v0.1.0)

**Deciders**: Fredrik Matheson

## Context

The adversarial workflow requires installing several files into user projects:
- Configuration file (config.yml)
- Three workflow scripts (evaluate_plan.sh, review_implementation.sh, validate_tests.sh)
- Aider configuration (.aider.conf.yml)
- Environment template (.env.example)
- Optional agent coordination files (agent-handoffs.json, current-state.json, etc.)
- Project README documentation

### Setup Requirements

**Per-Project Customization:**
- Different projects use different models (GPT-4o, Claude, etc.)
- Different test commands (pytest, npm test, cargo test, etc.)
- Different task directories (tasks/, docs/tasks/, delegation/tasks/, etc.)
- Different project-specific settings

**Installation Constraints:**
- Must work across different operating systems (macOS, Linux, WSL)
- Should handle existing files gracefully (don't overwrite user modifications)
- Need to validate package integrity (all templates present)
- Must set correct file permissions (scripts need +x)
- Should be non-destructive (don't break existing projects)

**Developer Experience:**
- Setup should be quick (<5 minutes)
- Configuration should be obvious and editable
- Scripts should be readable and modifiable
- Users should understand what's installed where

**Maintenance:**
- Package updates should be possible
- Template improvements should reach users
- Customizations should survive updates (with warnings)
- Bug fixes in scripts should be distributable

### Forces at Play

**Flexibility vs Consistency:**
- Want consistent structure across projects
- But need per-project customization
- Balance standardization with adaptability

**Simplicity vs Power:**
- Simple setup for new users
- But powerful customization for advanced users
- Avoid overwhelming beginners

**Package Distribution:**
- Templates must ship with package
- Must work with pip installation
- Need to handle both wheel and source distributions
- Should work with editable installs (`pip install -e .`)

### Problem Statement

How do we:
1. Ship standardized workflow scripts with the package
2. Allow per-project customization
3. Handle installation and updates cleanly
4. Maintain script readability and modifiability
5. Ensure package integrity and validation

## Decision

Use **template files with variable substitution** for initialization, storing templates in package data and rendering them during `adversarial init`.

### Architecture

**Template Storage:**
```
adversarial_workflow/
├── templates/
│   ├── config.yml.template              # Configuration
│   ├── evaluate_plan.sh.template        # Phase 1 script
│   ├── review_implementation.sh.template # Phase 3 script
│   ├── validate_tests.sh.template       # Phase 4 script
│   ├── .aider.conf.yml.template         # Aider config
│   ├── .env.example.template            # API key template
│   ├── README.template                  # Project documentation
│   └── agent-context/                   # Agent coordination
│       ├── agent-handoffs.json.template
│       ├── current-state.json.template
│       ├── README.md.template
│       └── AGENT-SYSTEM-GUIDE.md
```

**Template Variables:**

Configuration variables use `{{VARIABLE}}` syntax:

```yaml
# config.yml.template
evaluator_model: {{EVALUATOR_MODEL}}
task_directory: {{TASK_DIRECTORY}}
log_directory: {{LOG_DIRECTORY}}
test_command: {{TEST_COMMAND}}
```

**Default values** (can be overridden interactively):
```python
config_vars = {
    "EVALUATOR_MODEL": "gpt-4o",
    "TASK_DIRECTORY": "tasks/",
    "TEST_COMMAND": "pytest",
    "LOG_DIRECTORY": ".adversarial/logs/",
    "ARTIFACTS_DIRECTORY": ".adversarial/artifacts/",
}
```

**Initialization Process:**

1. **Pre-flight Validation**
   ```python
   required_templates = [
       "config.yml.template",
       "evaluate_plan.sh.template",
       "review_implementation.sh.template",
       "validate_tests.sh.template",
       ".aider.conf.yml.template",
       ".env.example.template",
   ]
   # Verify all templates exist before proceeding
   ```

2. **Directory Creation**
   ```
   project/
   └── .adversarial/
       ├── config.yml           # Rendered from template
       ├── scripts/
       │   ├── evaluate_plan.sh
       │   ├── review_implementation.sh
       │   └── validate_tests.sh
       ├── logs/                # Empty, for runtime
       └── artifacts/           # Empty, for runtime
   ```

3. **Template Rendering**
   ```python
   def render_template(template_path, output_path, variables):
       # Read template
       content = read_file(template_path)

       # Replace {{VAR}} with values
       for key, value in variables.items():
           content = content.replace(f"{{{{{key}}}}}", value)

       # Write output
       write_file(output_path, content)

       # Set permissions (+x for .sh files)
       if output_path.endswith(".sh"):
           os.chmod(output_path, 0o755)
   ```

4. **Project Root Files**
   ```
   project/
   ├── .aider.conf.yml      # Copied to root
   ├── .env.example         # Copied to root
   └── .adversarial/        # (as above)
   ```

5. **Gitignore Updates**
   ```
   # Added to .gitignore
   .adversarial/logs/
   .adversarial/artifacts/
   .env
   ```

### Package Data Configuration

**pyproject.toml:**
```toml
[tool.setuptools.package-data]
adversarial_workflow = [
    "templates/*.template",
    "templates/**/*.template",
    "templates/**/*.md",
    "templates/agent-context/*",
]
```

This ensures templates ship with wheel and source distributions.

### Interactive vs Non-Interactive

**Interactive mode** (`adversarial init --interactive`):
- Prompts for custom values
- Shows preview of what will be created
- Asks before overwriting existing files
- Validates API keys
- Explains each setting

**Non-interactive mode** (`adversarial init`):
- Uses default values
- Fails if .adversarial/ exists (safe default)
- Suitable for automation/CI

### Customization After Installation

Users can modify installed files:

```bash
# Edit configuration
vim .adversarial/config.yml

# Customize scripts
vim .adversarial/scripts/review_implementation.sh

# Changes persist across package updates
# (unless user explicitly re-runs adversarial init)
```

**Philosophy**: Templates provide starting point, users own the files after installation.

## Consequences

### Positive

**Flexibility:**
- ✅ **Per-project customization**: Each project gets appropriate defaults
- ✅ **Variable substitution**: Easy to adapt to different test frameworks, models
- ✅ **Post-install modification**: Users can customize scripts after installation
- ✅ **Version-specific**: Different projects can use different workflow versions

**Distribution:**
- ✅ **Package integrity**: Pre-flight checks validate all templates present
- ✅ **Standard pip install**: Works with pip, pipx, and editable installs
- ✅ **Wheel compatibility**: Templates included in both wheel and source distributions
- ✅ **No network dependency**: All templates ship with package

**Developer Experience:**
- ✅ **Quick setup**: `adversarial init` takes <30 seconds
- ✅ **Readable scripts**: Bash scripts are plain text, easy to understand
- ✅ **Modifiable**: Users can adapt scripts to project needs
- ✅ **No magic**: Clear what's installed where

**Maintenance:**
- ✅ **Centralized updates**: Improve templates in one place
- ✅ **Bug fix distribution**: Script improvements reach new installations
- ✅ **Version control**: Templates tracked in git
- ✅ **Testing**: Can test template rendering in CI

### Negative

**Complexity:**
- ⚠️ **Two-stage process**: Template storage + rendering adds complexity
- ⚠️ **Variable management**: Must keep variables in sync across templates
- ⚠️ **Package data**: Must configure pyproject.toml correctly (easy to miss)
- ⚠️ **Testing overhead**: Must test both template and rendered output

**Update Challenges:**
- ⚠️ **User modifications preserved**: Can't easily update customized scripts
- ⚠️ **No auto-update**: Users must manually re-run init for updates
- ⚠️ **Divergence risk**: User scripts may diverge from latest templates
- ⚠️ **Version confusion**: Unclear which template version user has

**File Management:**
- ⚠️ **Multiple copies**: Each project has full copy of scripts
- ⚠️ **Disk space**: ~50KB per project (trivial but not zero)
- ⚠️ **Consistency**: Same bug appears in all projects until re-initialized

**Edge Cases:**
- ⚠️ **Missing templates**: If package-data misconfigured, installation fails
- ⚠️ **Overwrite protection**: Must handle existing .adversarial/ gracefully
- ⚠️ **Permission issues**: Script +x may not work on some filesystems

### Neutral

**Alternative Approaches Considered** (see below)

**Template Format:**
- 📊 Simple `{{VAR}}` syntax (not Jinja2, Mustache, etc.)
- 📊 Minimal variables (5-6 per template)
- 📊 Plain text templates (no compiled formats)

**File Organization:**
- 📊 Scripts in `.adversarial/scripts/`
- 📊 Config in `.adversarial/config.yml`
- 📊 Logs/artifacts in `.adversarial/`
- 📊 Dotfiles at project root

## Alternatives Considered

### Alternative 1: Configuration-Only (No Templates)

**Structure:** Ship scripts with package, configure via config.yml only

```
adversarial_workflow/scripts/
├── evaluate_plan.sh  # Static, references config.yml
└── ...
```

**Rejected because:**
- ❌ **No per-project customization**: All projects use same scripts
- ❌ **Update complications**: Package updates change behavior unexpectedly
- ❌ **Path complexity**: Scripts must discover package installation location
- ❌ **User modifications impossible**: Can't edit package scripts
- ❌ **No version control**: Scripts not in user's repo

### Alternative 2: Hard-Coded Initialization

**Structure:** Generate scripts with Python code (no templates)

```python
def create_evaluate_script():
    script = f"""#!/bin/bash
EVALUATOR_MODEL={model}
# ... 200 lines of bash ...
"""
    write_file(".adversarial/scripts/evaluate_plan.sh", script)
```

**Rejected because:**
- ❌ **Unmaintainable**: Bash in Python strings is error-prone
- ❌ **Testing nightmare**: Can't easily test generated bash
- ❌ **Syntax highlighting**: No highlighting in Python strings
- ❌ **Version control**: Harder to track script changes
- ❌ **Complexity**: Must escape quotes, handle multi-line

### Alternative 3: Interactive Wizard Only

**Structure:** Prompt for every setting, no templates

```python
model = input("Evaluator model? ")
test_cmd = input("Test command? ")
# ... 20 more prompts ...
```

**Rejected because:**
- ❌ **Poor UX**: Too many questions for simple setup
- ❌ **No defaults**: Users must answer everything
- ❌ **Not automatable**: Can't use in CI/scripts
- ❌ **Slow**: Takes 5-10 minutes instead of 30 seconds
- ❌ **Intimidating**: Beginners don't know what to answer

### Alternative 4: Git Clone Approach

**Structure:** Clone template repository into project

```bash
adversarial init  # clones github.com/movito/adversarial-workflow-template
```

**Rejected because:**
- ❌ **Network dependency**: Requires internet connection
- ❌ **Version coupling**: Hard to match package version to template version
- ❌ **Git complexity**: What if project isn't git? Or has submodules?
- ❌ **Rate limits**: GitHub API limits could cause failures
- ❌ **Offline usage**: Doesn't work on air-gapped systems

### Alternative 5: No Templates (User Writes Scripts)

**Structure:** Just install CLI, users write their own scripts

**Rejected because:**
- ❌ **High barrier**: Most users won't write bash scripts
- ❌ **No standardization**: Every project different
- ❌ **Reinventing wheel**: Users recreate what we already solved
- ❌ **Error-prone**: Easy to miss edge cases
- ❌ **Poor UX**: Package should work out of box

## Implementation Details

### Template Variable Convention

**Naming:** `SCREAMING_SNAKE_CASE` for clarity
**Syntax:** `{{VARIABLE}}` (double braces, no spaces)
**Scope:** Limited set (5-6 variables, not dozens)

**Why not Jinja2/Mustache?**
- Simple string replacement sufficient
- No control flow needed in templates
- Avoids dependency on template engine
- Faster rendering (no parsing)

### Script Permissions

Scripts automatically made executable:
```python
if output_path.endswith(".sh"):
    os.chmod(output_path, 0o755)
```

**Why:** Users expect `.sh` files to be executable

### Overwrite Protection

```python
if os.path.exists(".adversarial/"):
    if interactive:
        response = input("Overwrite? (y/N): ")
        if response.lower() != "y":
            abort()
    else:
        error("Already initialized. Use --force to overwrite.")
```

**Why:** Protect user modifications from accidental overwrite

### Package Data Verification

```python
required_templates = [...]
missing = [t for t in required if not exists(t)]
if missing:
    error("Package installation incomplete. Missing: " + ", ".join(missing))
```

**Why:** Catch pyproject.toml misconfiguration early

## Related Decisions

- ADR-0002: Bash and Aider foundation (what templates contain)
- ADR-0003: Multi-stage workflow design (why we need these scripts)
- ADR-0007: YAML + .env configuration (what config.yml contains)
- ADR-0009: Interactive onboarding (how interactive mode works)

## References

- [Python packaging guide](https://packaging.python.org/guides/distributing-packages-using-setuptools/) - Package data
- [setuptools.package-data](https://setuptools.pypa.io/en/latest/userguide/datafiles.html) - Including non-Python files
- [cli.py:554-572](../../../adversarial_workflow/cli.py#L554-L572) - render_template implementation
- [cli.py:600-750](../../../adversarial_workflow/cli.py#L600-L750) - init() function

## Revision History

- 2025-10-15: Initial decision (v0.1.0)
- 2025-10-20: Documented as ADR-0004
