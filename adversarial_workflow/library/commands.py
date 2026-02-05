"""CLI commands for the evaluator library."""

import difflib
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import yaml

from .client import LibraryClient, LibraryClientError, NetworkError, ParseError
from .models import IndexData, InstalledEvaluatorMeta, UpdateInfo

# ANSI color codes (matching cli.py)
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
GRAY = "\033[90m"


def get_evaluators_dir() -> Path:
    """Get the evaluators directory for the current project."""
    return Path.cwd() / ".adversarial" / "evaluators"


def format_table(
    headers: List[str], rows: List[List[str]], widths: Optional[List[int]] = None
) -> str:
    """
    Format data as a simple table.

    Args:
        headers: Column headers.
        rows: List of row data (each row is a list of strings).
        widths: Optional column widths. If None, auto-calculated.

    Returns:
        Formatted table string.
    """
    if not widths:
        # Calculate widths from data
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(widths):
                    widths[i] = max(widths[i], len(str(cell)))

    # Format header
    header_line = "  ".join(h.ljust(w) for h, w in zip(headers, widths))
    lines = [header_line]

    # Format rows
    for row in rows:
        row_line = "  ".join(str(c).ljust(w) for c, w in zip(row, widths))
        lines.append(row_line)

    return "\n".join(lines)


def generate_provenance_header(provider: str, name: str, version: str) -> str:
    """Generate the provenance header for installed evaluators."""
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    return f"""# Installed from adversarial-evaluator-library
# Source: {provider}/{name}
# Version: {version}
# Installed: {timestamp}
#
# To check for updates: adversarial library check-updates
# To update: adversarial library update {name}
#
# Feel free to edit this file - it's yours now!

_meta:
  source: adversarial-evaluator-library
  source_path: {provider}/{name}
  version: "{version}"
  installed: "{timestamp}"

"""


def scan_installed_evaluators() -> List[InstalledEvaluatorMeta]:
    """
    Scan the evaluators directory for installed library evaluators.

    Returns:
        List of metadata for installed evaluators with _meta blocks.
    """
    evaluators_dir = get_evaluators_dir()
    if not evaluators_dir.exists():
        return []

    installed = []
    for yaml_file in evaluators_dir.glob("*.yml"):
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if data and "_meta" in data:
                meta = InstalledEvaluatorMeta.from_dict(data["_meta"])
                if meta and meta.source == "adversarial-evaluator-library":
                    meta.file_path = str(yaml_file)  # Track file path for updates
                    installed.append(meta)
        except (yaml.YAMLError, OSError):
            # Skip files that can't be parsed
            continue

    return installed


def library_list(
    provider: Optional[str] = None,
    category: Optional[str] = None,
    verbose: bool = False,
    no_cache: bool = False,
) -> int:
    """
    List available evaluators from the library.

    Args:
        provider: Filter by provider name.
        category: Filter by category name.
        verbose: Show detailed information.
        no_cache: Bypass cache and fetch fresh data.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    client = LibraryClient()

    try:
        index, from_cache = client.fetch_index(no_cache=no_cache)
    except NetworkError as e:
        print(f"{RED}Error: Network unavailable{RESET}")
        print(f"  {e}")
        print()
        print("Check your internet connection and try again.")
        print(f"Or use {CYAN}--no-cache{RESET} to force a fresh fetch.")
        return 1
    except ParseError as e:
        print(f"{RED}Error: Could not parse library index{RESET}")
        print(f"  {e}")
        return 1

    # Filter evaluators
    evaluators = index.evaluators

    if provider:
        evaluators = [e for e in evaluators if e.provider == provider]
        if not evaluators:
            print(f"{YELLOW}No evaluators found for provider: {provider}{RESET}")
            print()
            print("Available providers:")
            providers = sorted(set(e.provider for e in index.evaluators))
            for p in providers:
                print(f"  - {p}")
            return 1

    if category:
        evaluators = [e for e in evaluators if e.category == category]
        if not evaluators:
            print(f"{YELLOW}No evaluators found for category: {category}{RESET}")
            print()
            print("Available categories:")
            for cat_name, cat_desc in sorted(index.categories.items()):
                print(f"  - {cat_name}: {cat_desc}")
            return 1

    # Print header
    cache_note = f" {GRAY}(cached){RESET}" if from_cache else ""
    print()
    print(
        f"{BOLD}Available evaluators from adversarial-evaluator-library (v{index.version}){RESET}{cache_note}"
    )
    print()

    if verbose:
        # Detailed view
        for e in evaluators:
            print(f"{CYAN}{e.provider}/{e.name}{RESET}")
            print(f"  Model: {e.model}")
            print(f"  Category: {e.category}")
            print(f"  Description: {e.description}")
            print()
    else:
        # Table view
        headers = ["PROVIDER", "NAME", "CATEGORY", "DESCRIPTION"]
        rows = []
        for e in evaluators:
            # Truncate description if too long
            desc = e.description
            if len(desc) > 40:
                desc = desc[:37] + "..."
            rows.append([e.provider, e.name, e.category, desc])

        print(format_table(headers, rows))
        print()

    # Summary
    count = len(evaluators)
    total = len(index.evaluators)
    if provider or category:
        print(f"{count} evaluators shown (of {total} total).")
    else:
        print(f"{count} evaluators available.")
    print()
    print(f"Use '{CYAN}adversarial library install <provider>/<name>{RESET}' to install.")

    return 0


def library_info(evaluator_spec: str) -> int:
    """
    Show detailed information about a library evaluator.

    Args:
        evaluator_spec: Evaluator in 'provider/name' format.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    client = LibraryClient()

    # Parse spec
    parts = evaluator_spec.split("/")
    if len(parts) != 2:
        print(f"{RED}Error: Invalid format. Use provider/name (e.g., google/gemini-flash){RESET}")
        return 1

    provider, name = parts

    # Fetch index
    try:
        index, _ = client.fetch_index()
    except NetworkError as e:
        print(f"{RED}Error: Network unavailable{RESET}")
        print(f"  {e}")
        return 1
    except ParseError as e:
        print(f"{RED}Error: Could not parse library index{RESET}")
        print(f"  {e}")
        return 1

    # Get evaluator entry
    entry = index.get_evaluator(provider, name)
    if not entry:
        print(f"{RED}Error: Evaluator not found: {evaluator_spec}{RESET}")
        print()
        print("Use 'adversarial library list' to see available evaluators.")
        return 1

    # Display basic info from index
    print()
    print(f"{BOLD}{provider}/{name}{RESET}")
    print()
    print(f"Version:     {index.version}")
    print(f"Provider:    {provider}")
    print(f"Model:       {entry.model}")
    print(f"Category:    {entry.category}")
    print()
    print("Description:")
    print(f"  {entry.description}")
    print()

    # Try to fetch extended info from README
    readme = client.fetch_readme(provider, name)
    if readme:
        _display_extended_info(readme)
    else:
        print(f"{GRAY}Extended info unavailable (README.md not found).{RESET}")
        print()

    # Installation hint
    print(f"Install: {CYAN}adversarial library install {evaluator_spec}{RESET}")
    print()

    return 0


def _display_extended_info(readme: str) -> None:
    """
    Parse and display extended info from README.md.

    Extracts changelog, cost estimates, and API key info from README.
    """
    lines = readme.split("\n")

    # Look for API Key section
    api_key = None
    for line in lines:
        if "api_key" in line.lower() or "API key" in line:
            # Try to extract env var name
            import re

            match = re.search(r"([A-Z_]+_API_KEY)", line)
            if match:
                api_key = match.group(1)
                break

    if api_key:
        print(f"API Key:     {api_key}")
        print()

    # Look for Changelog section
    in_changelog = False
    changelog_lines = []
    for line in lines:
        if line.strip().lower().startswith("## changelog") or line.strip().lower().startswith(
            "# changelog"
        ):
            in_changelog = True
            continue
        if in_changelog:
            if line.strip().startswith("##") or line.strip().startswith("# "):
                break
            if line.strip():
                changelog_lines.append(line.strip())
            if len(changelog_lines) >= 5:  # Limit changelog entries
                break

    if changelog_lines:
        print("Changelog:")
        for cl in changelog_lines[:5]:
            print(f"  {cl}")
        print()

    # Look for Cost section
    in_cost = False
    cost_lines = []
    for line in lines:
        if "cost" in line.lower() and line.strip().startswith("#"):
            in_cost = True
            continue
        if in_cost:
            if line.strip().startswith("#"):
                break
            if line.strip():
                cost_lines.append(line.strip())
            if len(cost_lines) >= 3:
                break

    if cost_lines:
        print("Estimated Cost:")
        for cl in cost_lines[:3]:
            print(f"  {cl}")
        print()


def library_install(
    evaluator_specs: List[str],
    force: bool = False,
    skip_validation: bool = False,
    dry_run: bool = False,
    category: Optional[str] = None,
    yes: bool = False,
) -> int:
    """
    Install evaluators from the library.

    Args:
        evaluator_specs: List of evaluator specs in 'provider/name' format.
        force: Overwrite existing files.
        skip_validation: Skip schema validation.
        dry_run: Preview without making changes.
        category: Install all evaluators in this category.
        yes: Skip confirmation prompts (required for non-TTY).

    Returns:
        Exit code (0 for success, 1 for error).
    """
    client = LibraryClient()

    # Non-TTY detection: require --yes for non-interactive mode (unless dry-run)
    if not yes and not dry_run and not sys.stdin.isatty():
        print(f"{RED}Error: Use --yes for non-interactive mode{RESET}")
        return 1

    # Fetch index first
    try:
        index, _ = client.fetch_index()
    except NetworkError as e:
        print(f"{RED}Error: Network unavailable{RESET}")
        print(f"  {e}")
        return 1
    except ParseError as e:
        print(f"{RED}Error: Could not parse library index{RESET}")
        print(f"  {e}")
        return 1

    # Handle --category flag: get all evaluators in that category
    if category:
        matching = index.filter_by_category(category)
        if not matching:
            print(f"{RED}Error: No evaluators found in category '{category}'{RESET}")
            print()
            print("Available categories:")
            for cat_name, cat_desc in sorted(index.categories.items()):
                print(f"  - {cat_name}: {cat_desc}")
            return 1

        print(f"Installing all evaluators in category '{category}':")
        print()
        for e in matching:
            print(f"  - {e.provider}/{e.name} (v{index.version})")
        print()

        # Skip confirmation for --yes or --dry-run (dry-run makes no changes)
        if not yes and not dry_run:
            response = input("Proceed? [y/N]: ").strip().lower()
            if response not in ("y", "yes"):
                print("Cancelled.")
                return 0

        evaluator_specs = [f"{e.provider}/{e.name}" for e in matching]

    # Require at least one evaluator spec
    if not evaluator_specs:
        print(f"{RED}Error: No evaluators specified{RESET}")
        print()
        print("Usage:")
        print("  adversarial library install <provider>/<name> [<provider>/<name> ...]")
        print("  adversarial library install --category <category-name>")
        return 1

    evaluators_dir = get_evaluators_dir()
    if not dry_run:
        evaluators_dir.mkdir(parents=True, exist_ok=True)

    success_count = 0
    for spec in evaluator_specs:
        # Parse spec (provider/name or provider/name@version - version ignored for now)
        if "@" in spec:
            spec = spec.split("@")[0]  # Strip version for now

        parts = spec.split("/")
        if len(parts) != 2:
            print(f"{RED}Error: Invalid evaluator spec: {spec}{RESET}")
            print("  Expected format: provider/name (e.g., google/gemini-flash)")
            continue

        provider, name = parts

        # Check if evaluator exists in index
        entry = index.get_evaluator(provider, name)
        if not entry:
            print(f"{RED}Error: Evaluator not found: {spec}{RESET}")
            print("  Use 'adversarial library list' to see available evaluators.")
            continue

        # Check if file already exists (use provider-name format to avoid collisions)
        dest_path = evaluators_dir / f"{provider}-{name}.yml"

        if dry_run:
            # Dry-run mode: show preview without making changes
            print(f"Dry run: Would install {CYAN}{spec}{RESET} (v{index.version})")
            print()
            print(f"  Target: {dest_path}")
            if dest_path.exists():
                print(f"  Status: {YELLOW}File exists (would overwrite with --force){RESET}")
            else:
                print(f"  Status: {GREEN}New file (clean install){RESET}")
            print()

            # Fetch and preview evaluator config
            preview_success = False
            try:
                yaml_content = client.fetch_evaluator(provider, name)
                yaml_content_clean = yaml_content.lstrip()
                if yaml_content_clean.startswith("---"):
                    yaml_content_clean = yaml_content_clean[3:].lstrip("\n")

                print("  Evaluator config preview:")
                print("  " + "─" * 25)
                preview_lines = yaml_content_clean.split("\n")[:10]
                for line in preview_lines:
                    print(f"  {line}")
                if len(yaml_content_clean.split("\n")) > 10:
                    print("  ...")
                print()
                preview_success = True
            except NetworkError as e:
                print(f"  {RED}Error: Could not fetch preview{RESET}")
                print(f"    {e}")
                print()

            print(f"{YELLOW}No changes made (dry run).{RESET}")
            print()
            if preview_success:
                success_count += 1
            continue

        if dest_path.exists() and not force:
            print(f"{YELLOW}Skipping: {provider}-{name}.yml already exists{RESET}")
            print(f"  Use {CYAN}--force{RESET} to overwrite.")
            continue

        # Fetch evaluator config
        print(f"Installing {CYAN}{spec}{RESET}...")
        try:
            yaml_content = client.fetch_evaluator(provider, name)
        except NetworkError as e:
            print(f"  {RED}Error: Failed to fetch evaluator{RESET}")
            print(f"    {e}")
            continue

        # Strip leading YAML document separator to prevent multi-document issues
        yaml_content_clean = yaml_content.lstrip()
        if yaml_content_clean.startswith("---"):
            # Remove the document separator and any following newline
            yaml_content_clean = yaml_content_clean[3:].lstrip("\n")

        # Validate YAML
        try:
            parsed = yaml.safe_load(yaml_content_clean)
            if not parsed:
                raise ValueError("Empty YAML content")
        except (yaml.YAMLError, ValueError) as e:
            print(f"  {RED}Error: Invalid YAML in evaluator{RESET}")
            print(f"    {e}")
            if skip_validation:
                print(f"  {YELLOW}Warning: --skip-validation is set, continuing anyway{RESET}")
            else:
                continue

        # Add provenance header
        full_content = (
            generate_provenance_header(provider, name, index.version) + yaml_content_clean
        )

        # Write file
        try:
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(full_content)
            print(f"  {GREEN}Installed: {dest_path}{RESET}")
            success_count += 1
        except OSError as e:
            print(f"  {RED}Error: Could not write file{RESET}")
            print(f"    {e}")
            continue

    # Summary
    print()
    if dry_run:
        if success_count == 0 and len(evaluator_specs) > 0:
            print(f"{RED}Dry run failed: No evaluators could be previewed.{RESET}")
            return 1
        print(
            f"{CYAN}Dry run complete. {success_count} evaluator(s) previewed successfully.{RESET}"
        )
        return 0
    elif success_count == len(evaluator_specs):
        print(f"{GREEN}All {success_count} evaluator(s) installed successfully.{RESET}")
    elif success_count > 0:
        print(f"{YELLOW}{success_count} of {len(evaluator_specs)} evaluator(s) installed.{RESET}")
    else:
        print(f"{RED}No evaluators installed.{RESET}")
        return 1

    if not dry_run:
        print()
        print("Next steps:")
        print(f"  1. Configure API keys if needed (check {CYAN}.env{RESET})")
        print(f"  2. Run: {CYAN}adversarial <evaluator-name> <task-file>{RESET}")

    return 0


def library_check_updates(name: Optional[str] = None, no_cache: bool = False) -> int:
    """
    Check for available updates to installed evaluators.

    Args:
        name: Specific evaluator name to check (optional).
        no_cache: Bypass cache and fetch fresh data.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    client = LibraryClient()

    # Scan installed evaluators
    installed = scan_installed_evaluators()
    if not installed:
        print(f"{YELLOW}No library-installed evaluators found.{RESET}")
        print()
        print("Install evaluators with: adversarial library install <provider>/<name>")
        return 0

    # Filter by name if specified
    if name:
        installed = [m for m in installed if m.name == name]
        if not installed:
            print(f"{YELLOW}Evaluator '{name}' not found or not from library.{RESET}")
            return 1

    # Fetch index
    print("Checking for evaluator updates...")
    print()

    try:
        index, from_cache = client.fetch_index(no_cache=no_cache)
    except NetworkError as e:
        print(f"{RED}Error: Network unavailable{RESET}")
        print(f"  {e}")
        return 1
    except ParseError as e:
        print(f"{RED}Error: Could not parse library index{RESET}")
        print(f"  {e}")
        return 1

    # Compare versions
    updates: List[UpdateInfo] = []
    for meta in installed:
        entry = index.get_evaluator(meta.provider, meta.name)
        if entry:
            is_outdated = meta.version != index.version
            updates.append(
                UpdateInfo(
                    name=meta.name,
                    installed_version=meta.version,
                    available_version=index.version,
                    is_outdated=is_outdated,
                )
            )
        else:
            # Evaluator no longer in index
            updates.append(
                UpdateInfo(
                    name=meta.name,
                    installed_version=meta.version,
                    available_version="-",
                    is_outdated=False,
                    is_local_only=True,
                )
            )

    # Print table
    headers = ["EVALUATOR", "INSTALLED", "AVAILABLE", "STATUS"]
    rows = []
    for u in updates:
        status = u.status
        if u.is_outdated:
            status = f"{YELLOW}{status}{RESET}"
        elif u.is_local_only:
            status = f"{GRAY}{status}{RESET}"
        else:
            status = f"{GREEN}{status}{RESET}"
        rows.append([u.name, u.installed_version, u.available_version, status])

    print(format_table(headers, rows))
    print()

    # Summary
    outdated_count = sum(1 for u in updates if u.is_outdated)
    if outdated_count > 0:
        print(f"{YELLOW}{outdated_count} update(s) available.{RESET}")
        print()
        print(f"Run '{CYAN}adversarial library update <name>{RESET}' to update.")
        print(f"Or '{CYAN}adversarial library update --all{RESET}' to update all.")
    else:
        print(f"{GREEN}All evaluators are up to date.{RESET}")

    return 0


def library_update(
    name: Optional[str] = None,
    all_evaluators: bool = False,
    yes: bool = False,
    diff_only: bool = False,
    no_cache: bool = False,
    dry_run: bool = False,
) -> int:
    """
    Update installed evaluators to newer versions.

    Args:
        name: Specific evaluator name to update.
        all_evaluators: Update all outdated evaluators.
        yes: Skip confirmation prompts.
        diff_only: Show diff without applying changes (same as dry_run).
        no_cache: Bypass cache.
        dry_run: Preview without making changes (same as diff_only).

    Returns:
        Exit code (0 for success, 1 for error).
    """
    # Combine dry_run and diff_only (they do the same thing)
    preview_only = dry_run or diff_only

    client = LibraryClient()

    # Non-TTY detection: require --yes for non-interactive mode (unless preview mode)
    if not yes and not preview_only and not sys.stdin.isatty():
        print(f"{RED}Error: Use --yes for non-interactive mode{RESET}")
        return 1

    if not name and not all_evaluators:
        print(f"{RED}Error: Specify an evaluator name or use --all{RESET}")
        print()
        print("Usage:")
        print("  adversarial library update <name>")
        print("  adversarial library update --all")
        return 1

    # Scan installed evaluators
    installed = scan_installed_evaluators()
    if not installed:
        print(f"{YELLOW}No library-installed evaluators found.{RESET}")
        return 0

    # Fetch index
    try:
        index, _ = client.fetch_index(no_cache=no_cache)
    except NetworkError as e:
        print(f"{RED}Error: Network unavailable{RESET}")
        print(f"  {e}")
        return 1
    except ParseError as e:
        print(f"{RED}Error: Could not parse library index{RESET}")
        print(f"  {e}")
        return 1

    # Find evaluators to update
    to_update = []
    for meta in installed:
        if name and meta.name != name:
            continue

        entry = index.get_evaluator(meta.provider, meta.name)
        if not entry:
            if name:
                print(f"{YELLOW}Evaluator '{name}' not found in library.{RESET}")
            continue

        if meta.version != index.version:
            to_update.append((meta, entry))
        elif name:
            print(f"{GREEN}Evaluator '{name}' is already up to date (v{meta.version}).{RESET}")
            return 0

    if not to_update:
        if all_evaluators:
            print(f"{GREEN}All evaluators are up to date.{RESET}")
        return 0

    evaluators_dir = get_evaluators_dir()
    updated_count = 0

    for meta, entry in to_update:
        print()
        print(f"Updating {CYAN}{meta.name}{RESET} ({meta.version} → {index.version})...")

        # Fetch new content
        try:
            new_yaml = client.fetch_evaluator(entry.provider, entry.name)
        except NetworkError as e:
            print(f"  {RED}Error: Failed to fetch evaluator{RESET}")
            print(f"    {e}")
            continue

        # Read current content using tracked file path
        if meta.file_path:
            current_path = Path(meta.file_path)
        else:
            # Fallback: check both old and new naming conventions
            new_path = evaluators_dir / f"{meta.provider}-{meta.name}.yml"
            old_path = evaluators_dir / f"{meta.name}.yml"
            current_path = new_path if new_path.exists() else old_path
        try:
            with open(current_path, "r", encoding="utf-8") as f:
                current_content = f.read()
        except OSError as e:
            print(f"  {RED}Error: Could not read current file{RESET}")
            print(f"    {e}")
            continue

        # Generate new content with updated provenance
        # Strip leading YAML document separator to prevent multi-document issues
        new_yaml_clean = new_yaml.lstrip()
        if new_yaml_clean.startswith("---"):
            new_yaml_clean = new_yaml_clean[3:].lstrip("\n")
        new_content = (
            generate_provenance_header(entry.provider, entry.name, index.version) + new_yaml_clean
        )

        # Show diff
        print()
        diff = list(
            difflib.unified_diff(
                current_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"{meta.name}.yml (current)",
                tofile=f"{meta.name}.yml (new)",
            )
        )

        if not diff:
            print(f"  {GRAY}No changes in evaluator content.{RESET}")
            continue

        print("  Changes:")
        for line in diff[:50]:  # Limit diff output
            if line.startswith("+") and not line.startswith("+++"):
                print(f"  {GREEN}{line.rstrip()}{RESET}")
            elif line.startswith("-") and not line.startswith("---"):
                print(f"  {RED}{line.rstrip()}{RESET}")
            else:
                print(f"  {line.rstrip()}")

        if len(diff) > 50:
            print(f"  {GRAY}... ({len(diff) - 50} more lines){RESET}")

        if preview_only:
            print()
            print(f"  {GRAY}(dry run mode, no changes applied){RESET}")
            continue

        # Confirm update
        if not yes:
            print()
            response = input(f"  Apply update? [y/N]: ").strip().lower()
            if response not in ("y", "yes"):
                print(f"  {GRAY}Skipped.{RESET}")
                continue

        # Apply update
        try:
            with open(current_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"  {GREEN}Updated!{RESET}")
            updated_count += 1
        except OSError as e:
            print(f"  {RED}Error: Could not write file{RESET}")
            print(f"    {e}")

    # Summary
    print()
    if preview_only:
        print(f"Dry run complete. Use without {CYAN}--dry-run{RESET} to apply changes.")
    elif updated_count > 0:
        print(f"{GREEN}{updated_count} evaluator(s) updated.{RESET}")
    else:
        print(f"{YELLOW}No evaluators were updated.{RESET}")

    return 0
