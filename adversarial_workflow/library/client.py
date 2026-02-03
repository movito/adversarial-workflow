"""HTTP client for the evaluator library."""

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, Optional, Tuple

from .cache import DEFAULT_CACHE_DIR, CacheManager
from .models import IndexData

# Library repository URLs
DEFAULT_LIBRARY_URL = "https://raw.githubusercontent.com/movito/adversarial-evaluator-library/main"
INDEX_PATH = "evaluators/index.json"
EVALUATOR_PATH_TEMPLATE = "evaluators/{provider}/{name}/evaluator.yml"

# HTTP settings
DEFAULT_TIMEOUT = 10  # seconds


class LibraryClientError(Exception):
    """Base exception for library client errors."""

    pass


class NetworkError(LibraryClientError):
    """Network-related errors."""

    pass


class ParseError(LibraryClientError):
    """Parsing errors for malformed responses."""

    pass


class LibraryClient:
    """Client for fetching evaluators from the community library."""

    def __init__(
        self,
        base_url: str = DEFAULT_LIBRARY_URL,
        cache_dir: Optional[Path] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """
        Initialize the library client.

        Args:
            base_url: Base URL for the library repository.
            cache_dir: Directory for caching. Defaults to ~/.cache/adversarial-workflow
            timeout: HTTP timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.cache = CacheManager(cache_dir=cache_dir or DEFAULT_CACHE_DIR)

    def _fetch_url(self, url: str) -> str:
        """
        Fetch content from a URL.

        Args:
            url: The URL to fetch.

        Returns:
            The response content as a string.

        Raises:
            NetworkError: If the request fails.
        """
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "adversarial-workflow-library-client"},
            )
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return response.read().decode("utf-8")
        except urllib.error.URLError as e:
            raise NetworkError(f"Failed to fetch {url}: {e}") from e
        except urllib.error.HTTPError as e:
            raise NetworkError(f"HTTP error {e.code} fetching {url}: {e.reason}") from e
        except TimeoutError as e:
            raise NetworkError(f"Timeout fetching {url}") from e
        except OSError as e:
            raise NetworkError(f"Network error fetching {url}: {e}") from e

    def fetch_index(self, no_cache: bool = False) -> Tuple[IndexData, bool]:
        """
        Fetch the library index.

        Args:
            no_cache: If True, bypass the cache and fetch fresh data.

        Returns:
            Tuple of (IndexData, from_cache) where from_cache indicates if
            the data came from cache.

        Raises:
            NetworkError: If the request fails and no cache is available.
            ParseError: If the response cannot be parsed.
        """
        cache_key = "library-index"

        # Try cache first (unless no_cache is set)
        if not no_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data:
                try:
                    return IndexData.from_dict(cached_data), True
                except (KeyError, TypeError) as e:
                    # Cache data is invalid, will try to fetch fresh
                    pass

        # Fetch fresh data
        url = f"{self.base_url}/{INDEX_PATH}"
        try:
            content = self._fetch_url(url)
            data = json.loads(content)
        except NetworkError:
            # Try stale cache as fallback
            stale_data = self.cache.get_stale(cache_key)
            if stale_data:
                try:
                    return IndexData.from_dict(stale_data), True
                except (KeyError, TypeError):
                    pass
            raise
        except json.JSONDecodeError as e:
            raise ParseError(f"Invalid JSON in index: {e}") from e

        # Validate and parse
        try:
            index_data = IndexData.from_dict(data)
        except (KeyError, TypeError) as e:
            raise ParseError(f"Invalid index structure: {e}") from e

        # Update cache
        self.cache.set(cache_key, data)

        return index_data, False

    def fetch_evaluator(self, provider: str, name: str) -> str:
        """
        Fetch an evaluator configuration.

        Args:
            provider: The provider name (e.g., 'google', 'openai').
            name: The evaluator name (e.g., 'gemini-flash').

        Returns:
            The raw YAML content of the evaluator configuration.

        Raises:
            NetworkError: If the request fails.
        """
        path = EVALUATOR_PATH_TEMPLATE.format(provider=provider, name=name)
        url = f"{self.base_url}/{path}"
        return self._fetch_url(url)

    def is_online(self) -> bool:
        """
        Check if the library is reachable.

        Returns:
            True if the library can be reached, False otherwise.
        """
        try:
            url = f"{self.base_url}/{INDEX_PATH}"
            self._fetch_url(url)
            return True
        except LibraryClientError:
            return False

    def get_cache_age(self) -> Optional[float]:
        """
        Get the age of the cached index in seconds.

        Returns:
            Age in seconds, or None if not cached.
        """
        return self.cache.get_age("library-index")

    def clear_cache(self) -> int:
        """
        Clear all cached data.

        Returns:
            Number of cache entries cleared.
        """
        return self.cache.clear()
