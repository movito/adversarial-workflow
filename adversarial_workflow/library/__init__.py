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
    "DEFAULT_CACHE_DIR",
    "DEFAULT_CACHE_TTL",
    "DEFAULT_LIBRARY_URL",
    "CacheManager",
    "EvaluatorEntry",
    "IndexData",
    "InstalledEvaluatorMeta",
    "LibraryClient",
    "LibraryClientError",
    "LibraryConfig",
    "NetworkError",
    "ParseError",
    "UpdateInfo",
    "get_library_config",
    "library_check_updates",
    "library_info",
    "library_install",
    "library_list",
    "library_update",
]
