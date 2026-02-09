"""
Adversarial Workflow - Multi-stage AI code review system

A package for integrating Author-Evaluator adversarial code review
into existing projects. Prevents "phantom work" through multi-stage verification.

Usage:
    pip install adversarial-workflow
    adversarial init
    adversarial evaluate task.md
    adversarial review
    adversarial validate "pytest"
"""

try:
    from importlib.metadata import version as _get_version
    __version__ = _get_version("adversarial-workflow")
except Exception:
    __version__ = "0.9.6"  # Fallback for editable installs
__author__ = "Fredrik Matheson"
__license__ = "MIT"

from .cli import check, evaluate, init, main, review, validate

__all__ = ["main", "init", "check", "evaluate", "review", "validate", "__version__"]
