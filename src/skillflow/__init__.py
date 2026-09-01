"""SkillFlow — a minimal framework for composing reusable agent skills."""

from skillflow.skill import Skill, SkillContractError
from skillflow.specificity import SpecificityError, load_specificity

__all__ = ["Skill", "SkillContractError", "SpecificityError", "load_specificity"]
__version__ = "0.1.0"
