"""Execute recipes and enforce Pydantic contracts between skills."""

from __future__ import annotations

import logging

from pydantic import BaseModel, ValidationError

from skillflow.recipe import Recipe
from skillflow.skill import Skill, SkillContractError

logger = logging.getLogger("skillflow")


class Runner:
    """Run a linear recipe, adapting each skill Output into the next Input.

    Intermediate models are logged as JSON so pipelines are easy to inspect.
    Contract mismatches fail immediately with a ``SkillContractError``.
    """

    def run(self, recipe: Recipe, initial: BaseModel) -> BaseModel:
        """Execute every skill in ``recipe`` in order.

        Args:
            recipe: Linear pipeline to execute.
            initial: Input for the first skill.

        Returns:
            The Output model from the last skill.

        Raises:
            SkillContractError: If a step's data cannot satisfy the next
                skill's Input or the current skill's Output.
        """
        current: object = initial
        logger.info("Starting recipe '%s' with %s step(s)", recipe.name, len(recipe.skills))

        for index, skill in enumerate(recipe.skills, start=1):
            adapted = skill.adapt_input(current)
            logger.info(
                "recipe=%s step=%s/%s skill=%s input=%s",
                recipe.name,
                index,
                len(recipe.skills),
                skill.name,
                adapted.model_dump_json(),
            )
            output = skill.run(adapted)
            current = _ensure_output(skill, output)
            logger.info(
                "recipe=%s step=%s/%s skill=%s output=%s",
                recipe.name,
                index,
                len(recipe.skills),
                skill.name,
                current.model_dump_json(),
            )

        logger.info("Finished recipe '%s'", recipe.name)
        return current


def _ensure_output(skill: Skill, output: object) -> BaseModel:
    """Validate that a skill returned its declared Output model.

    Args:
        skill: Skill that produced ``output``.
        output: Value returned by ``skill.run``.

    Returns:
        A validated instance of the skill's Output model.

    Raises:
        SkillContractError: If the return value does not match the Output model.
    """
    if isinstance(output, skill.output_model):
        return output

    payload: object = output.model_dump() if isinstance(output, BaseModel) else output
    try:
        return skill.output_model.model_validate(payload)
    except ValidationError as exc:
        expected = ", ".join(skill.output_model.model_fields)
        actual = type(output).__name__
        raise SkillContractError(
            f"{skill.name} must return Output fields [{expected}] but returned {actual}: {exc}"
        ) from exc
