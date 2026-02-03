"""Cache management for the evaluator library client."""

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

# Default cache TTL: 1 hour (3600 seconds)
DEFAULT_CACHE_TTL = 3600

# Cache directory
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "adversarial-workflow"


class CacheManager:
    """Manages caching for the library client."""

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        ttl: int = DEFAULT_CACHE_TTL,
    ):
        """
        Initialize the cache manager.

        Args:
            cache_dir: Directory to store cache files. Defaults to ~/.cache/adversarial-workflow
            ttl: Time-to-live in seconds. Defaults to 3600 (1 hour).
        """
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self.ttl = ttl
        self._ensure_cache_dir()

    def _ensure_cache_dir(self) -> None:
        """Ensure the cache directory exists."""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            # If we can't create the cache dir, we'll operate without caching
            pass

    def _get_cache_path(self, key: str) -> Path:
        """Get the path for a cache entry."""
        # Sanitize key for filesystem
        safe_key = key.replace("/", "_").replace(":", "_")
        return self.cache_dir / f"{safe_key}.json"

    def _is_expired(self, cache_path: Path) -> bool:
        """Check if a cache entry is expired."""
        if not cache_path.exists():
            return True
        try:
            mtime = cache_path.stat().st_mtime
            return (time.time() - mtime) > self.ttl
        except OSError:
            return True

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a value from the cache.

        Args:
            key: The cache key.

        Returns:
            The cached value, or None if not found or expired.
        """
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        if self._is_expired(cache_path):
            return None

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def get_stale(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a value from the cache even if expired.

        Useful for offline fallback scenarios.

        Args:
            key: The cache key.

        Returns:
            The cached value, or None if not found.
        """
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def set(self, key: str, value: Dict[str, Any]) -> bool:
        """
        Store a value in the cache.

        Args:
            key: The cache key.
            value: The value to cache.

        Returns:
            True if successfully cached, False otherwise.
        """
        cache_path = self._get_cache_path(key)

        try:
            self._ensure_cache_dir()
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(value, f, indent=2)
            return True
        except OSError:
            return False

    def invalidate(self, key: str) -> bool:
        """
        Invalidate a cache entry.

        Args:
            key: The cache key.

        Returns:
            True if successfully invalidated, False otherwise.
        """
        cache_path = self._get_cache_path(key)

        try:
            if cache_path.exists():
                cache_path.unlink()
            return True
        except OSError:
            return False

    def clear(self) -> int:
        """
        Clear all cache entries.

        Returns:
            The number of entries cleared.
        """
        count = 0
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    cache_file.unlink()
                    count += 1
                except OSError:
                    pass
        except OSError:
            pass
        return count

    def get_age(self, key: str) -> Optional[float]:
        """
        Get the age of a cache entry in seconds.

        Args:
            key: The cache key.

        Returns:
            Age in seconds, or None if not found.
        """
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        try:
            mtime = cache_path.stat().st_mtime
            return time.time() - mtime
        except OSError:
            return None
