"""Shared types for SkillFlow contracts and LLM messages."""

from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single chat turn passed to an LLM client.

    Attributes:
        role: Speaker for this turn.
        content: Message text.
    """

    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)
