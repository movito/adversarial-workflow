# Task: Evaluator Library CLI Integration

**For**: adversarial-workflow team
**From**: gas-taxes project
**Date**: 2026-02-02
**Priority**: Medium
**Estimated Effort**: 2-3 days

---

## Executive Summary

Add CLI commands to `adversarial-workflow` that allow users to browse, install, and update evaluator configurations from the community [adversarial-evaluator-library](https://github.com/movito/adversarial-evaluator-library). This enables evaluator sharing across projects while maintaining full local ownership of configurations.

---

## Background

### The Problem

The `adversarial-workflow` tool requires users to write evaluator YAML configurations from scratch. This creates several issues:

1. **High barrier to entry**: New users must understand prompt engineering, model selection, and timeout tuning before they can evaluate anything
2. **Duplicated effort**: Multiple projects independently develop similar evaluators (e.g., "quick syntax check", "deep reasoning review")
3. **No knowledge sharing**: Hard-won insights about effective prompts and configurations stay siloed in individual projects
4. **Discovery problem**: Users don't know what evaluator patterns exist or which models work well for which tasks

### The Solution

A **community evaluator library** (already created at `github.com/movito/adversarial-evaluator-library`) provides curated, tested evaluator configurations. The `adversarial-workflow` CLI needs commands to interact with this library.

### Design Philosophy: "Copy, Don't Link"

**Critical**: The library is a *catalog*, not a *dependency*. Evaluators are **copied** to projects, not referenced at runtime.

This means:
- Library unavailable? Your project still works
- Want to customize? Edit your local copy freely
- Need reproducibility? Your configs are self-contained
- Updates are explicit and user-controlled

---

## Architecture Context

### Four-Layer Model

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Project Configs                                   │
│  .adversarial/evaluators/*.yml                              │
│  Fully owned by project. Mix of custom + library-sourced.   │
└─────────────────────────────────────────────────────────────┘
                           ▲ copy (one-time)
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: CLI Helper ◀── THIS TASK                          │
│  adversarial library list|install|update                    │
│  Convenience layer. Not required. Manual copy works too.    │
└─────────────────────────────────────────────────────────────┘
                           ▲ fetches from
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Evaluator Library (separate repo)                 │
│  github.com/movito/adversarial-evaluator-library            │
│  Versioned, community-contributed, provider-organized.      │
└─────────────────────────────────────────────────────────────┘
                           (no dependency)
┌─────────────────────────────────────────────────────────────┐
│  Layer 0: Core Tool (adversarial-workflow)                  │
│  Defines YAML schema. Validates. Executes.                  │
│  NO built-in evaluators. NO knowledge of library.           │
└─────────────────────────────────────────────────────────────┘
```

### Library Repository Structure

The evaluator library follows this structure:

```
adversarial-evaluator-library/
├── index.json                    # Machine-readable catalog
├── evaluators/
│   ├── google/
│   │   ├── gemini-flash/
│   │   │   ├── evaluator.yml     # The config
│   │   │   ├── README.md         # Usage, examples
│   │   │   └── CHANGELOG.md      # Version history
│   │   ├── gemini-pro/
│   │   └── gemini-deep/
│   ├── openai/
│   │   ├── fast-check/
│   │   ├── o3-chain/
│   │   └── gpt52-reasoning/
│   └── mistral/
│       ├── mistral-fast/
│       ├── mistral-content/
│       └── codestral-code/
└── categories.json               # Category definitions
```

### index.json Schema

```json
{
  "version": "1.0.0",
  "updated": "2026-02-01T00:00:00Z",
  "evaluators": [
    {
      "name": "gemini-flash",
      "provider": "google",
      "path": "evaluators/google/gemini-flash",
      "version": "1.0.0",
      "categories": ["quick-check"],
      "description": "Fast, cost-effective initial validation using Gemini 2.5 Flash",
      "model": "gemini/gemini-2.5-flash",
      "estimated_cost_per_eval": "$0.001-0.005"
    }
  ],
  "categories": {
    "quick-check": "Fast, cost-effective initial validation",
    "deep-reasoning": "Extended analysis for complex documents",
    "adversarial": "Critical stress-testing for edge cases",
    "knowledge-synthesis": "Large-context cross-referencing",
    "cognitive-diversity": "Alternative model perspectives",
    "code-review": "Specialized code analysis"
  }
}
```

---

## Requirements

### 1. `adversarial library list`

**Purpose**: Browse available evaluators from the library.

**Usage**:
```bash
# List all evaluators
adversarial library list

# Filter by provider
adversarial library list --provider google
adversarial library list --provider openai
adversarial library list --provider mistral

# Filter by category
adversarial library list --category quick-check
adversarial library list --category deep-reasoning

# Show detailed info
adversarial library list --verbose
```

**Output Format** (default):
```
Available evaluators from adversarial-evaluator-library (v1.0.0):

PROVIDER   NAME              CATEGORY           DESCRIPTION
google     gemini-flash      quick-check        Fast initial validation
google     gemini-pro        knowledge-synthesis Large-context analysis
google     gemini-deep       deep-reasoning     Extended thinking analysis
openai     fast-check        quick-check        GPT-4o-mini quick review
openai     o3-chain          deep-reasoning     Chain-of-thought analysis
openai     gpt52-reasoning   adversarial        Critical stress-testing
mistral    mistral-fast      quick-check        Rapid Mistral check
mistral    mistral-content   cognitive-diversity Alternative perspective
mistral    codestral-code    code-review        Code-specialized review

9 evaluators available. Use 'adversarial library install <provider>/<name>' to install.
```

**Output Format** (--verbose):
```
google/gemini-flash (v1.0.0)
  Category: quick-check
  Model: gemini/gemini-2.5-flash
  Cost: ~$0.001-0.005 per evaluation
  Description: Fast, cost-effective initial validation using Gemini 2.5 Flash.
               Ideal for quick syntax and structure checks before deeper review.

  Install: adversarial library install google/gemini-flash
```

**Behavior**:
- Fetches `index.json` from library repo (with caching, see Configuration)
- Graceful failure if network unavailable (show cached data or helpful error)
- No authentication required (public repo)

---

### 2. `adversarial library install`

**Purpose**: Copy an evaluator configuration from library to project.

**Usage**:
```bash
# Install latest version
adversarial library install google/gemini-flash

# Install specific version
adversarial library install google/gemini-flash@1.0.0

# Install multiple
adversarial library install google/gemini-flash openai/fast-check

# Install by category (all evaluators in category)
adversarial library install --category quick-check

# Force overwrite existing
adversarial library install google/gemini-flash --force

# Dry run (show what would be installed)
adversarial library install google/gemini-flash --dry-run
```

**Behavior**:

1. **Fetch evaluator.yml** from library repo
2. **Add provenance metadata** (see format below)
3. **Write to** `.adversarial/evaluators/<name>.yml`
4. **Validate** the config against schema
5. **Report success** with usage hint

**Provenance Metadata Format**:

The installed file should include metadata as a YAML comment block AND as parseable fields:

```yaml
# Installed from adversarial-evaluator-library
# Source: google/gemini-flash
# Version: 1.0.0
# Installed: 2026-02-02T15:30:00Z
#
# To check for updates: adversarial library check-updates
# To update: adversarial library update google/gemini-flash
#
# Feel free to edit this file - it's yours now!

_meta:
  source: adversarial-evaluator-library
  source_path: google/gemini-flash
  version: "1.0.0"
  installed: "2026-02-02T15:30:00Z"

name: gemini-flash
model: gemini/gemini-2.5-flash
api_key_env: GEMINI_API_KEY
timeout: 180
output_suffix: gemini-flash
prompt: |
  You are a document reviewer performing a quick validation check.
  ...
```

**Conflict Handling**:
- If file exists and `--force` not specified: prompt user or error
- Show diff if updating existing file
- Never silently overwrite

**Output**:
```
Installing google/gemini-flash (v1.0.0)...
  ✓ Fetched evaluator configuration
  ✓ Validated against schema
  ✓ Written to .adversarial/evaluators/gemini-flash.yml

Installed successfully!

To use: adversarial evaluate --evaluator gemini-flash <document>

Note: Requires GEMINI_API_KEY environment variable.
```

---

### 3. `adversarial library check-updates`

**Purpose**: Check if installed library evaluators have newer versions available.

**Usage**:
```bash
# Check all installed evaluators
adversarial library check-updates

# Check specific evaluator
adversarial library check-updates gemini-flash
```

**Behavior**:
1. Scan `.adversarial/evaluators/` for files with `_meta.source` field
2. Compare `_meta.version` against library's `index.json`
3. Report available updates

**Output**:
```
Checking for evaluator updates...

EVALUATOR        INSTALLED   AVAILABLE   STATUS
gemini-flash     1.0.0       1.2.0       Update available
fast-check       1.1.0       1.1.0       Up to date
mistral-content  1.0.0       -           Not in library (custom?)

1 update available. Run 'adversarial library update <name>' to update.
```

---

### 4. `adversarial library update`

**Purpose**: Update an installed evaluator to a newer library version.

**Usage**:
```bash
# Update specific evaluator (interactive diff review)
adversarial library update gemini-flash

# Update to specific version
adversarial library update gemini-flash@1.1.0

# Update all outdated evaluators
adversarial library update --all

# Skip diff review (auto-accept)
adversarial library update gemini-flash --yes

# Show diff only, don't apply
adversarial library update gemini-flash --diff-only
```

**Behavior**:

1. Fetch new version from library
2. **Show diff** between current and new version (critical!)
3. **Prompt for confirmation** (unless `--yes`)
4. Apply update, preserving any `_meta` customizations
5. Update `_meta.version` and `_meta.installed`

**Diff Output**:
```
Updating gemini-flash: 1.0.0 → 1.2.0

Changes:
--- .adversarial/evaluators/gemini-flash.yml (current)
+++ google/gemini-flash@1.2.0 (library)
@@ -8,7 +8,7 @@
 name: gemini-flash
 model: gemini/gemini-2.5-flash
 api_key_env: GEMINI_API_KEY
-timeout: 180
+timeout: 240
 output_suffix: gemini-flash
 prompt: |
-  You are a document reviewer performing a quick validation check.
+  You are an expert document reviewer. Perform a thorough validation check.
   ...

Apply this update? [y/N]:
```

**Important**: If user has made local modifications (detected by comparing non-`_meta` fields against original version), warn them:

```
⚠️  Warning: Your local gemini-flash.yml has been modified since installation.
   Local changes will be overwritten by this update.

   Consider:
   - Backup your current file first
   - Review the diff carefully
   - Re-apply your customizations after update

   Proceed anyway? [y/N]:
```

---

### 5. `adversarial library info`

**Purpose**: Show detailed information about a library evaluator.

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

---

## Configuration

### config.yml Options

Add these optional settings to `.adversarial/config.yml`:

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

### Environment Variables

```bash
# Override library URL
ADVERSARIAL_LIBRARY_URL=https://github.com/myorg/my-evaluator-library

# Disable caching (always fetch fresh)
ADVERSARIAL_LIBRARY_NO_CACHE=1
```

---

## Implementation Notes

### Network Handling

1. **Caching**: Cache `index.json` locally to avoid repeated fetches
2. **Offline Mode**: If network unavailable, use cached data with warning
3. **Timeouts**: 10-second timeout for fetches, configurable
4. **Retry**: Single retry with exponential backoff on transient failures

### GitHub Raw URLs

For fetching from GitHub without authentication:

```python
# index.json
f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/index.json"

# evaluator.yml
f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/evaluators/{provider}/{name}/evaluator.yml"
```

### Schema Validation

After fetching, validate evaluator configs against the existing schema before writing. Reject invalid configs with clear error messages.

### Backward Compatibility

- `_meta` field should be ignored by the evaluate command (it's metadata only)
- Existing evaluator configs without `_meta` should continue to work
- The `library` subcommand is additive; no changes to existing commands

---

## Acceptance Criteria

### Must Have

- [ ] `adversarial library list` shows available evaluators with filtering
- [ ] `adversarial library install <provider>/<name>` copies evaluator to project
- [ ] Installed evaluators include `_meta` provenance block
- [ ] `adversarial library check-updates` identifies outdated evaluators
- [ ] `adversarial library update` shows diff and prompts before applying
- [ ] Graceful offline handling (use cache, clear error messages)
- [ ] Works with the official `adversarial-evaluator-library` repo

### Should Have

- [ ] `adversarial library info` shows detailed evaluator information
- [ ] `--category` filter for install (install all in category)
- [ ] `--dry-run` flag for install and update
- [ ] Configurable library URL for private/custom libraries
- [ ] Cache TTL configuration

### Nice to Have

- [ ] `adversarial library search <query>` fuzzy search
- [ ] `adversarial library export` to share custom evaluator to library format
- [ ] Integration with `adversarial init` to offer library evaluators during setup
- [ ] Shell completions for evaluator names

---

## Testing Guidance

### Unit Tests

- Parse `index.json` correctly
- Handle malformed/missing index gracefully
- Provenance metadata added correctly
- Version comparison logic
- Diff generation

### Integration Tests

- Fetch from real GitHub raw URLs
- Install/update cycle with actual library
- Offline mode with cached data
- Config file precedence

### Manual Testing Checklist

```bash
# Fresh project, no evaluators
adversarial library list
adversarial library install google/gemini-flash
adversarial evaluate --evaluator gemini-flash test.md  # Should work

# Update flow
# (Manually change version in library, or use older version)
adversarial library check-updates
adversarial library update gemini-flash --diff-only
adversarial library update gemini-flash

# Offline mode
# (Disconnect network)
adversarial library list  # Should show cached
adversarial library install openai/fast-check  # Should fail gracefully
```

---

## Reference Implementation

For reference, here's a sketch of the command structure (Python/Click):

```python
@cli.group()
def library():
    """Browse and install evaluators from the community library."""
    pass

@library.command("list")
@click.option("--provider", help="Filter by provider (google, openai, mistral)")
@click.option("--category", help="Filter by category")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed info")
def list_evaluators(provider, category, verbose):
    """List available evaluators from the library."""
    ...

@library.command("install")
@click.argument("evaluators", nargs=-1)
@click.option("--category", help="Install all evaluators in category")
@click.option("--force", is_flag=True, help="Overwrite existing files")
@click.option("--dry-run", is_flag=True, help="Show what would be installed")
def install(evaluators, category, force, dry_run):
    """Install evaluator(s) from the library."""
    ...

@library.command("check-updates")
@click.argument("evaluator", required=False)
def check_updates(evaluator):
    """Check for available updates to installed evaluators."""
    ...

@library.command("update")
@click.argument("evaluator")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
@click.option("--diff-only", is_flag=True, help="Show diff without applying")
@click.option("--all", "update_all", is_flag=True, help="Update all outdated")
def update(evaluator, yes, diff_only, update_all):
    """Update an installed evaluator to the latest library version."""
    ...

@library.command("info")
@click.argument("evaluator")
def info(evaluator):
    """Show detailed information about a library evaluator."""
    ...
```

---

## Questions for adversarial-workflow Team

1. **Subcommand naming**: Is `adversarial library ...` acceptable, or prefer `adversarial evaluator ...` or `adversarial eval-library ...`?

2. **Cache location**: Default to `~/.cache/adversarial-workflow/` or within `.adversarial/` in project?

3. **Private libraries**: How important is authentication support for private GitHub repos? (Could defer to v2)

4. **Monorepo considerations**: Any special handling needed if adversarial-workflow is used in monorepos?

---

## Related Resources

- **Evaluator Library Repo**: https://github.com/movito/adversarial-evaluator-library
- **Architecture Decision**: ADR-006 in gas-taxes project (attached below for reference)
- **Existing Evaluator Schema**: See `adversarial-workflow` documentation

---

## Appendix: ADR-006 Summary

The evaluator library architecture follows these core principles:

1. **Copy, Don't Link**: Library evaluators are copied to projects, never referenced at runtime
2. **Schema as Contract**: The only shared dependency is the YAML schema specification
3. **Graceful Degradation**: Every component works without the others
4. **User-Controlled Updates**: Updates are explicit, diffed, and approved by users

This ensures projects remain self-contained and the library is purely a convenience layer.

---

*Document prepared by gas-taxes project planner. Contact: [project maintainer]*
