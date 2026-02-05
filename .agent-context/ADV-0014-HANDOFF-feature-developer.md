# ADV-0014 Handoff: Feature Developer

**Created**: 2026-02-05
**Task**: Evaluator Library CLI Enhancements
**Branch**: Create `feat/adv-0014-library-cli-enhancements`

---

## Quick Context

ADV-0013 (Library CLI Core) is complete and merged. It provides:
- `adversarial library list` - List available evaluators
- `adversarial library install` - Install evaluators
- `adversarial library check-updates` - Check for updates
- `adversarial library update` - Update installed evaluators

ADV-0014 adds quality-of-life enhancements to these commands.

---

## Existing Code Structure

```
adversarial_workflow/library/
├── __init__.py      # Exports LibraryClient, cache functions
├── cache.py         # Cache management (TTL-based)
├── client.py        # LibraryClient - fetch index, evaluators
├── commands.py      # CLI commands (list, install, check-updates, update)
└── models.py        # LibraryIndex, EvaluatorEntry dataclasses
```

### Key Functions in `commands.py`

| Function | Lines | Purpose |
|----------|-------|---------|
| `library_list` | 103-163 | List available evaluators |
| `library_install` | 214-334 | Install evaluators (needs --dry-run, --category, --yes) |
| `library_check_updates` | 337-413 | Check for updates |
| `library_update` | 416-540 | Update evaluators (needs --dry-run, --yes) |

### Key Classes in `models.py`

- `EvaluatorEntry` - Single evaluator metadata
- `LibraryIndex` - Full index with `get_evaluator(provider, name)` method

### Key Classes in `client.py`

- `LibraryClient` - Handles GitHub raw content fetching
  - `fetch_index()` → `(LibraryIndex, is_cached)`
  - `fetch_evaluator(provider, name)` → YAML content string

---

## Implementation Guide

### 1. `adversarial library info` Command (NEW)

**Add to `commands.py`** after `library_list`:

```python
def library_info(evaluator_spec: str) -> int:
    """
    Show detailed information about a library evaluator.

    Args:
        evaluator_spec: Evaluator in 'provider/name' format

    Returns:
        Exit code (0 for success, 1 for error)
    """
    client = LibraryClient()

    # Parse spec
    parts = evaluator_spec.split("/")
    if len(parts) != 2:
        print(f"{RED}Error: Invalid format. Use provider/name{RESET}")
        return 1

    provider, name = parts

    # Fetch index
    try:
        index, _ = client.fetch_index()
    except (NetworkError, ParseError) as e:
        print(f"{RED}Error: {e}{RESET}")
        return 1

    # Get evaluator entry
    entry = index.get_evaluator(provider, name)
    if not entry:
        print(f"{RED}Error: Evaluator not found: {evaluator_spec}{RESET}")
        return 1

    # Display info (see task file for output format)
    print(f"{BOLD}{provider}/{name}{RESET}")
    print()
    print(f"Version:     {entry.version}")
    print(f"Provider:    {entry.provider}")
    print(f"Model:       {entry.model}")
    # ... etc

    # Optionally fetch README for extended info
    # try:
    #     readme = client.fetch_readme(provider, name)
    # except NetworkError:
    #     pass  # Extended info unavailable

    return 0
```

**Register in CLI** (`adversarial_workflow/cli.py`):

```python
@library.command("info")
@click.argument("evaluator_spec")
def library_info_cmd(evaluator_spec: str):
    """Show detailed information about an evaluator."""
    from adversarial_workflow.library.commands import library_info
    sys.exit(library_info(evaluator_spec))
```

---

### 2. `--dry-run` Flag

**Modify `library_install`** (line ~214):

```python
def library_install(
    evaluator_specs: List[str],
    force: bool = False,
    skip_validation: bool = False,
    dry_run: bool = False,  # NEW
) -> int:
    # ... existing code ...

    if dry_run:
        print(f"Dry run: Would install {spec}")
        print(f"  Target: {dest_path}")
        print(f"  Status: {'Exists (would overwrite)' if dest_path.exists() else 'New file'}")
        print()
        print("  Evaluator config preview:")
        print("  " + "─" * 25)
        for line in yaml_content_clean.split("\n")[:10]:
            print(f"  {line}")
        print("  ...")
        print()
        print(f"{YELLOW}No changes made (dry run).{RESET}")
        continue  # Skip actual write

    # ... existing write code ...
```

**Same pattern for `library_update`**.

---

### 3. `--category` Flag

**Modify `library_install`**:

```python
def library_install(
    evaluator_specs: List[str],
    force: bool = False,
    skip_validation: bool = False,
    dry_run: bool = False,
    category: str | None = None,  # NEW
    yes: bool = False,  # NEW (for confirmation bypass)
) -> int:
    client = LibraryClient()
    index, _ = client.fetch_index()

    # If category specified, get all evaluators in that category
    if category:
        matching = [e for e in index.evaluators if e.category == category]
        if not matching:
            print(f"{RED}Error: No evaluators in category '{category}'{RESET}")
            return 1

        print(f"Installing all evaluators in category '{category}':")
        for e in matching:
            print(f"  - {e.provider}/{e.name} (v{e.version})")
        print()

        if not yes:
            confirm = input("Proceed? [y/N]: ")
            if confirm.lower() != 'y':
                print("Cancelled.")
                return 0

        evaluator_specs = [f"{e.provider}/{e.name}" for e in matching]

    # ... rest of existing code ...
```

---

### 4. `--yes` Flag (Non-Interactive)

Add to both `library_install` and `library_update`:

```python
# At the start of the function
if not yes and not sys.stdin.isatty():
    print(f"{RED}Error: Use --yes for non-interactive mode{RESET}")
    return 1
```

---

### 5. Configuration System (NEW FILE)

**Create `adversarial_workflow/library/config.py`**:

```python
"""Library configuration with env > file > defaults precedence."""

from dataclasses import dataclass
from pathlib import Path
import os
import yaml

@dataclass
class LibraryConfig:
    url: str = "https://github.com/movito/adversarial-evaluator-library"
    ref: str = "main"
    cache_ttl: int = 3600
    cache_dir: Path = Path.home() / ".cache" / "adversarial-workflow"
    enabled: bool = True

def get_library_config() -> LibraryConfig:
    """Load library config with precedence: env > file > defaults."""
    config = LibraryConfig()

    # Load from config file if exists
    config_file = Path(".adversarial/config.yml")
    if config_file.exists():
        with open(config_file) as f:
            data = yaml.safe_load(f) or {}
        lib_config = data.get("library", {})
        if "url" in lib_config:
            config.url = lib_config["url"]
        if "ref" in lib_config:
            config.ref = lib_config["ref"]
        if "cache_ttl" in lib_config:
            config.cache_ttl = lib_config["cache_ttl"]
        if "enabled" in lib_config:
            config.enabled = lib_config["enabled"]

    # Apply environment overrides
    if url := os.environ.get("ADVERSARIAL_LIBRARY_URL"):
        config.url = url
    if os.environ.get("ADVERSARIAL_LIBRARY_NO_CACHE"):
        config.cache_ttl = 0
    if ttl := os.environ.get("ADVERSARIAL_LIBRARY_CACHE_TTL"):
        config.cache_ttl = int(ttl)

    return config
```

**Update `LibraryClient`** to use config:

```python
from .config import get_library_config

class LibraryClient:
    def __init__(self):
        config = get_library_config()
        self.base_url = config.url
        self.ref = config.ref
        # ... use config values
```

---

## CLI Registration

All new options need to be registered in `adversarial_workflow/cli.py`:

```python
@library.command("install")
@click.argument("evaluator_specs", nargs=-1)
@click.option("--force", "-f", is_flag=True, help="Overwrite existing files")
@click.option("--skip-validation", is_flag=True, help="Skip YAML validation")
@click.option("--dry-run", is_flag=True, help="Preview without making changes")  # NEW
@click.option("--category", "-c", help="Install all evaluators in category")  # NEW
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompts")  # NEW
def library_install_cmd(evaluator_specs, force, skip_validation, dry_run, category, yes):
    # ...
```

---

## Testing Strategy

### Unit Tests to Add

```python
# tests/test_library_info.py
def test_info_displays_all_fields(): ...
def test_info_evaluator_not_found(): ...
def test_info_invalid_format(): ...

# tests/test_library_dry_run.py
def test_install_dry_run_shows_preview(): ...
def test_install_dry_run_no_file_written(): ...
def test_update_dry_run_shows_diff(): ...

# tests/test_library_category.py
def test_install_category_lists_evaluators(): ...
def test_install_category_empty(): ...
def test_install_category_with_yes(): ...

# tests/test_library_config.py
def test_config_defaults(): ...
def test_config_file_override(): ...
def test_config_env_override(): ...
def test_config_precedence_env_over_file(): ...

# tests/test_library_noninteractive.py
def test_yes_flag_skips_prompt(): ...
def test_no_tty_without_yes_errors(): ...
```

---

## Verification Checklist

Before marking complete:
- [ ] `adversarial library info google/gemini-flash` works
- [ ] `adversarial library install --dry-run` shows preview
- [ ] `adversarial library install --category quick-check` works
- [ ] `--yes` flag bypasses prompts
- [ ] Non-TTY without `--yes` shows error
- [ ] Config file settings are respected
- [ ] `ADVERSARIAL_LIBRARY_URL` env var works
- [ ] All new tests pass
- [ ] All existing tests still pass (110+)

---

## Resources

- Task file: `delegation/tasks/2-todo/ADV-0014-library-cli-enhancements.md`
- Existing library code: `adversarial_workflow/library/`
- CLI registration: `adversarial_workflow/cli.py`
- ADV-0013 PR for reference: https://github.com/movito/adversarial-workflow/pull/20
