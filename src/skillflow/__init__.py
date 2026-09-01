"""SkillFlow — a minimal framework for composing reusable agent skills."""

from skillflow.llm import LLMClient, OpenAICompatibleClient, StubLLMClient
from skillflow.recipe import Recipe
from skillflow.runner import Runner
from skillflow.skill import Skill, SkillContractError
from skillflow.specificity import SpecificityError, load_specificity
from skillflow.types import ChatMessage

__all__ = [
    "ChatMessage",
    "LLMClient",
    "OpenAICompatibleClient",
    "Recipe",
    "Runner",
    "Skill",
    "SkillContractError",
    "SpecificityError",
    "StubLLMClient",
    "load_specificity",
]
__version__ = "0.1.0"
