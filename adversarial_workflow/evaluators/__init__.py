"""
Evaluators module for adversarial-workflow.

This module provides the plugin architecture for custom evaluators.
"""

from .config import EvaluatorConfig
from .discovery import (
    EvaluatorParseError,
    discover_local_evaluators,
    parse_evaluator_yaml,
)

__all__ = [
    "EvaluatorConfig",
    "EvaluatorParseError",
    "discover_local_evaluators",
    "parse_evaluator_yaml",
]
