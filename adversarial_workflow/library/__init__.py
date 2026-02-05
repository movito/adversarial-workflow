"""Evaluator library client for adversarial-workflow.

This module provides functionality to browse, install, and update evaluator
configurations from the community adversarial-evaluator-library.

Philosophy: "Copy, Don't Link"
- Evaluators are copied to projects, not referenced at runtime
- Projects remain self-contained and work offline
- Users can customize their local copies freely
- Updates are explicit and user-controlled
"""

from .cache import DEFAULT_CACHE_DIR, DEFAULT_CACHE_TTL, CacheManager
from .client import (
    DEFAULT_LIBRARY_URL,
    LibraryClient,
    LibraryClientError,
    NetworkError,
    ParseError,
)
from .commands import (
    library_check_updates,
    library_info,
    library_install,
    library_list,
    library_update,
)
from .config import LibraryConfig, get_library_config
from .models import EvaluatorEntry, IndexData, InstalledEvaluatorMeta, UpdateInfo

__all__ = [
    # Client
    "LibraryClient",
    "LibraryClientError",
    "NetworkError",
    "ParseError",
    "DEFAULT_LIBRARY_URL",
    # Models
    "EvaluatorEntry",
    "IndexData",
    "InstalledEvaluatorMeta",
    "UpdateInfo",
    # Cache
    "CacheManager",
    "DEFAULT_CACHE_DIR",
    "DEFAULT_CACHE_TTL",
    # Config
    "LibraryConfig",
    "get_library_config",
    # Commands
    "library_list",
    "library_info",
    "library_install",
    "library_check_updates",
    "library_update",
]
