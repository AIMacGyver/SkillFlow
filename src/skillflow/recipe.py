"""Linear recipe definitions that compose skills into a workflow."""

from collections.abc import Sequence

from skillflow.skill import Skill


class Recipe:
    """An ordered, linear pipeline of skills.

    Recipes stay simple on purpose: each skill's Output is adapted into the next
    skill's Input. Branching DAGs are out of scope for the MVP.

    Args:
        name: Human-readable recipe identifier used in logs.
        skills: Skills to run in order. Must contain at least one skill.
    """

    def __init__(self, name: str, skills: Sequence[Skill]) -> None:
        """Create a linear recipe.

        Args:
            name: Human-readable recipe identifier used in logs.
            skills: Skills to run in order.

        Raises:
            ValueError: If ``name`` is blank or ``skills`` is empty.
        """
        if not name.strip():
            raise ValueError("Recipe name must be a non-empty string.")
        if not skills:
            raise ValueError(f"Recipe '{name}' must include at least one skill.")

        self.name = name
        self.skills = list(skills)
