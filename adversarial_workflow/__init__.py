"""
Adversarial Workflow - Multi-stage AI code review system

A package for integrating Author-Reviewer adversarial code review
into existing projects. Prevents "phantom work" through multi-stage verification.

Usage:
    pip install adversarial-workflow
    adversarial init
    adversarial evaluate task.md
    adversarial review
    adversarial validate "pytest"
"""

__version__ = "0.2.0"
__author__ = "Fredrik Matheson"
__license__ = "MIT"

from .cli import check, evaluate, init, main, review, validate

__all__ = ["main", "init", "check", "evaluate", "review", "validate", "__version__"]
