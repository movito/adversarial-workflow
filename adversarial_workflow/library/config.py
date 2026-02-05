"""Library configuration with env > file > defaults precedence."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class LibraryConfig:
    """Configuration for the evaluator library.

    Precedence: environment variables > config file > defaults.
    """

    url: str = "https://raw.githubusercontent.com/movito/adversarial-evaluator-library/main"
    ref: str = "main"
    cache_ttl: int = 3600  # 1 hour
    cache_dir: Path = field(default_factory=lambda: Path.home() / ".cache" / "adversarial-workflow")
    enabled: bool = True


def get_library_config(config_path: Optional[Path] = None) -> LibraryConfig:
    """
    Load library configuration with precedence: env > file > defaults.

    Args:
        config_path: Optional path to config file. Defaults to .adversarial/config.yml

    Returns:
        LibraryConfig with merged settings.
    """
    config = LibraryConfig()

    # Load from config file if exists
    config_file = config_path or Path(".adversarial/config.yml")
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            lib_config = data.get("library", {})

            if "url" in lib_config:
                config.url = lib_config["url"]
            if "ref" in lib_config:
                config.ref = lib_config["ref"]
            if "cache_ttl" in lib_config:
                config.cache_ttl = int(lib_config["cache_ttl"])
            if "cache_dir" in lib_config:
                # Expand ~ in path
                config.cache_dir = Path(lib_config["cache_dir"]).expanduser()
            if "enabled" in lib_config:
                config.enabled = bool(lib_config["enabled"])
        except (yaml.YAMLError, OSError, ValueError):
            # Config file is invalid, use defaults
            pass

    # Apply environment variable overrides (highest precedence)
    if url := os.environ.get("ADVERSARIAL_LIBRARY_URL"):
        config.url = url

    # Process TTL first, then NO_CACHE (so NO_CACHE always wins)
    if ttl := os.environ.get("ADVERSARIAL_LIBRARY_CACHE_TTL"):
        try:
            config.cache_ttl = int(ttl)
        except ValueError:
            pass  # Invalid TTL, keep current value

    # NO_CACHE takes precedence over CACHE_TTL - check it last
    if os.environ.get("ADVERSARIAL_LIBRARY_NO_CACHE"):
        config.cache_ttl = 0

    if ref := os.environ.get("ADVERSARIAL_LIBRARY_REF"):
        config.ref = ref

    return config
