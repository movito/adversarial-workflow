"""Built-in evaluator configurations."""

from __future__ import annotations

from .config import EvaluatorConfig

# Built-in evaluators use shell scripts - prompts are in the scripts
BUILTIN_EVALUATORS: dict[str, EvaluatorConfig] = {
    "evaluate": EvaluatorConfig(
        name="evaluate",
        description="Plan evaluation (GPT-4o)",
        model="gpt-4o",
        api_key_env="OPENAI_API_KEY",
        prompt="",  # Prompt is in shell script
        output_suffix="PLAN-EVALUATION",
        source="builtin",
    ),
    "proofread": EvaluatorConfig(
        name="proofread",
        description="Teaching content review (GPT-4o)",
        model="gpt-4o",
        api_key_env="OPENAI_API_KEY",
        prompt="",  # Prompt is in shell script
        output_suffix="PROOFREADING",
        source="builtin",
    ),
    "review": EvaluatorConfig(
        name="review",
        description="Code review (GPT-4o)",
        model="gpt-4o",
        api_key_env="OPENAI_API_KEY",
        prompt="",  # Prompt is in shell script
        output_suffix="CODE-REVIEW",
        source="builtin",
    ),
}
