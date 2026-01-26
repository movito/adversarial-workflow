"""Evaluators module for adversarial-workflow plugin architecture."""

from .builtins import BUILTIN_EVALUATORS
from .config import EvaluatorConfig
from .discovery import (
    EvaluatorParseError,
    discover_local_evaluators,
    parse_evaluator_yaml,
)
from .runner import run_evaluator


def get_all_evaluators() -> dict[str, EvaluatorConfig]:
    """Get all available evaluators (built-in + local).

    Local evaluators override built-in evaluators with the same name.
    Aliases from local evaluators are also included in the returned dictionary.
    """
    import logging

    logger = logging.getLogger(__name__)

    evaluators: dict[str, EvaluatorConfig] = {}

    # Add built-in evaluators first
    evaluators.update(BUILTIN_EVALUATORS)

    # Discover and add local evaluators (may override built-ins)
    local = discover_local_evaluators()
    for name, config in local.items():
        if name in BUILTIN_EVALUATORS:
            logger.info("Local evaluator '%s' overrides built-in", name)
        evaluators[name] = config

    return evaluators


__all__ = [
    "EvaluatorConfig",
    "EvaluatorParseError",
    "run_evaluator",
    "get_all_evaluators",
    "discover_local_evaluators",
    "parse_evaluator_yaml",
    "BUILTIN_EVALUATORS",
]
