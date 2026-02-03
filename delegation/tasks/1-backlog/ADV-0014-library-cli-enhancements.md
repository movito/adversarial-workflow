# ADV-0014: Evaluator Library CLI Enhancements

**Status**: Backlog
**Priority**: Low
**Estimated Effort**: 1-2 days
**Depends On**: ADV-0013 (Library CLI Core)
**Source**: Proposal from gas-taxes project (AWF-evaluator-library-cli-integration.md)

---

## Summary

Extend the library CLI (implemented in ADV-0013) with additional features: detailed evaluator info command, dry-run mode, category-based installation, and configuration options. These enhancements improve usability but are not required for core functionality.

---

## Background

ADV-0013 implements the core library CLI commands:
- `adversarial library list`
- `adversarial library install`
- `adversarial library check-updates`
- `adversarial library update`

This task adds quality-of-life enhancements that improve the user experience.

---

## Requirements

### 1. `adversarial library info`

**Purpose**: Show detailed information about a library evaluator before installing.

**Usage**:
```bash
adversarial library info google/gemini-flash
```

**Output**:
```
google/gemini-flash

Version:     1.2.0
Provider:    Google (Gemini)
Model:       gemini/gemini-2.5-flash
Category:    quick-check
API Key:     GEMINI_API_KEY

Description:
  Fast, cost-effective initial validation using Gemini 2.5 Flash.
  Ideal for quick syntax and structure checks before deeper review.
  Typical response time: 5-15 seconds.

Estimated Cost:
  ~$0.001-0.005 per evaluation (varies by document size)

Changelog:
  1.2.0 (2026-01-28): Increased timeout to 240s, improved prompt clarity
  1.1.0 (2026-01-15): Added structured output format
  1.0.0 (2026-01-01): Initial release

Install: adversarial library install google/gemini-flash
```

**Data Source**:
- Basic info from `index.json`
- Extended info (changelog, full description) from evaluator's `README.md`

**Error Handling**:
- If README.md not found: show basic info only with note "Extended info unavailable"
- If changelog missing: omit changelog section gracefully
- Inherits network/validation error handling from ADV-0013

---

### 2. `--dry-run` Flag for Install and Update

**Purpose**: Preview what would happen without making changes.

**Usage**:
```bash
# Show what would be installed
adversarial library install google/gemini-flash --dry-run

# Show what would be updated
adversarial library update gemini-flash --dry-run
```

**Output for Install**:
```
Dry run: Would install google/gemini-flash (v1.2.0)

  Target: .adversarial/evaluators/gemini-flash.yml
  Status: File does not exist (clean install)

  Evaluator config preview:
  ─────────────────────────
  name: gemini-flash
  model: gemini/gemini-2.5-flash
  api_key_env: GEMINI_API_KEY
  timeout: 240
  ...

No changes made (dry run).
```

**Output for Update**:
```
Dry run: Would update gemini-flash: 1.0.0 → 1.2.0

Changes:
--- .adversarial/evaluators/gemini-flash.yml (current)
+++ google/gemini-flash@1.2.0 (library)
@@ -8,7 +8,7 @@
-timeout: 180
+timeout: 240

No changes made (dry run).
```

---

### 3. `--category` Install Flag

**Purpose**: Install all evaluators in a category with one command.

**Usage**:
```bash
# Install all quick-check evaluators
adversarial library install --category quick-check

# Install all deep-reasoning evaluators
adversarial library install --category deep-reasoning
```

**Behavior**:
1. Query `index.json` for all evaluators in category
2. Show list and confirm before proceeding
3. Install each evaluator, reporting progress
4. Skip already-installed evaluators (unless `--force`)

**Output**:
```
Installing all evaluators in category 'quick-check':

  - google/gemini-flash (v1.2.0)
  - openai/fast-check (v1.1.0)
  - mistral/mistral-fast (v1.0.0)

Proceed? [y/N]: y

Installing google/gemini-flash... ✓
Installing openai/fast-check... ✓
Installing mistral/mistral-fast... ✓

3 evaluators installed successfully.
```

---

### 4. Configuration Options

**Purpose**: Allow customization of library behavior via config file and environment variables.

**Config File** (`.adversarial/config.yml`):
```yaml
# Evaluator Library Settings (all optional)
library:
  # Library repository URL (default: official library)
  url: https://github.com/movito/adversarial-evaluator-library

  # Branch/tag to use (default: main)
  ref: main

  # Cache duration for index.json in seconds (default: 3600 = 1 hour)
  cache_ttl: 3600

  # Local cache directory (default: ~/.cache/adversarial-workflow/)
  cache_dir: ~/.cache/adversarial-workflow/

  # Disable library features entirely
  enabled: true
```

**Environment Variables**:
```bash
# Override library URL (for private/custom libraries)
ADVERSARIAL_LIBRARY_URL=https://github.com/myorg/my-evaluator-library

# Disable caching (always fetch fresh)
ADVERSARIAL_LIBRARY_NO_CACHE=1

# Override cache TTL (seconds)
ADVERSARIAL_LIBRARY_CACHE_TTL=7200
```

**Precedence**: Environment variables > config file > defaults

**Config File Creation**:
- If `.adversarial/config.yml` doesn't exist, library commands work with defaults
- Config file is optional; library feature doesn't require it
- `adversarial init` already creates config.yml during project setup

---

### 6. Non-Interactive Mode

**Purpose**: Support CI/CD pipelines and automation.

**Usage**:
```bash
# Install without confirmation prompt
adversarial library install --yes google/gemini-flash

# Category install in CI (no prompts)
adversarial library install --category quick-check --yes

# Update all in CI (requires --yes for safety)
adversarial library update --all --yes
```

**Behavior**:
- Without `--yes`: prompt for confirmation on destructive operations (overwrite, category install)
- With `--yes`: proceed without prompts
- If stdin is not a TTY and `--yes` not provided: error with message "Use --yes for non-interactive mode"

---

### 5. Nice to Have: Shell Completions

**Purpose**: Enable tab completion for evaluator names.

**Usage**:
```bash
# Bash
eval "$(adversarial --completion bash)"

# Zsh
eval "$(adversarial --completion zsh)"

# Fish
adversarial --completion fish | source
```

**Completion Scope**:
- `adversarial library install <TAB>` - complete from index.json
- `adversarial library update <TAB>` - complete from installed evaluators
- `adversarial library info <TAB>` - complete from index.json

**Implementation**: Use Click's built-in completion support with custom completers.

---

## Technical Implementation

### File Changes

```
adversarial_workflow/
├── library/
│   ├── commands.py          # Add info command, --dry-run, --category
│   ├── config.py            # NEW: Configuration loading
│   └── completions.py       # NEW: Shell completion helpers (if implementing)
```

### Configuration Loading

```python
def get_library_config() -> LibraryConfig:
    """Load library config with precedence: env > file > defaults."""
    defaults = LibraryConfig(
        url="https://github.com/movito/adversarial-evaluator-library",
        ref="main",
        cache_ttl=3600,
        cache_dir=Path.home() / ".cache" / "adversarial-workflow",
        enabled=True,
    )

    # Load from config file
    config_file = Path(".adversarial/config.yml")
    if config_file.exists():
        # ... merge with defaults

    # Apply environment overrides
    if url := os.environ.get("ADVERSARIAL_LIBRARY_URL"):
        config.url = url
    # ... etc

    return config
```

---

## Acceptance Criteria

### Must Have (for this task)

- [ ] `adversarial library info <provider>/<name>` shows detailed evaluator info
- [ ] `adversarial library info` gracefully handles missing README.md
- [ ] `adversarial library install --dry-run` shows preview without changes
- [ ] `adversarial library update --dry-run` shows diff without applying
- [ ] `adversarial library install --category <name>` installs all in category
- [ ] `--yes` flag for non-interactive mode on install and update commands
- [ ] Non-TTY detection with clear error message if `--yes` not provided
- [ ] `library:` config section in `.adversarial/config.yml` is respected
- [ ] Config file is optional; commands work with defaults if missing
- [ ] `ADVERSARIAL_LIBRARY_URL` environment variable overrides default URL
- [ ] `ADVERSARIAL_LIBRARY_NO_CACHE` environment variable disables caching
- [ ] Unit tests for all new functionality

### Nice to Have

- [ ] Shell completions for Bash/Zsh/Fish
- [ ] `adversarial library search <query>` fuzzy search
- [ ] `adversarial library export` to share custom evaluator

---

## Testing Strategy

### Unit Tests

```python
# tests/test_library_info.py
- test_info_displays_all_fields()
- test_info_missing_evaluator()
- test_info_with_changelog()

# tests/test_library_dry_run.py
- test_install_dry_run_new_file()
- test_install_dry_run_existing_file()
- test_update_dry_run_shows_diff()

# tests/test_library_category.py
- test_install_category_all()
- test_install_category_skip_existing()
- test_install_category_with_force()

# tests/test_library_config.py
- test_config_defaults()
- test_config_file_override()
- test_config_env_override()
- test_config_precedence()
```

### Manual Testing Checklist

```bash
# Info command
adversarial library info google/gemini-flash
adversarial library info nonexistent/evaluator  # Should error gracefully

# Dry run
adversarial library install google/gemini-flash --dry-run
adversarial library update gemini-flash --dry-run

# Category install
adversarial library install --category quick-check

# Config override
ADVERSARIAL_LIBRARY_URL=https://github.com/myorg/custom-lib adversarial library list
```

---

## Dependencies

- **Required**: ADV-0013 (Library CLI Core) must be completed first
- **External**: None beyond what ADV-0013 requires

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Complexity creep | Low | Keep scope focused; defer fuzzy search to separate task |
| Config file conflicts | Low | Clear precedence rules; document thoroughly |
| Shell completion edge cases | Low | Mark as "nice to have"; test common shells only |

---

## Related Documents

- **Proposal**: `docs/proposals/AWF-evaluator-library-cli-integration.md`
- **Prerequisite Task**: ADV-0013 (Library CLI Core)
- **Library Repo**: https://github.com/movito/adversarial-evaluator-library
