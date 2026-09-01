"""Behavior tests for Pydantic skill contracts."""

import pytest
from pydantic import BaseModel

from skillflow import Skill, SkillContractError


class QueryIn(BaseModel):
    query: str


class QueryOut(BaseModel):
    query: str
    text: str


class OtherIn(BaseModel):
    other: str


class EchoSkill(Skill[QueryIn, QueryOut]):
    def run(self, data: QueryIn) -> QueryOut:
        return QueryOut(query=data.query, text=data.query.upper())


class NeedsOtherSkill(Skill[OtherIn, QueryOut]):
    def run(self, data: OtherIn) -> QueryOut:
        return QueryOut(query=data.other, text=data.other)


def test_adapt_input_accepts_matching_model() -> None:
    skill = EchoSkill()
    adapted = skill.adapt_input(QueryIn(query="hello"))

    assert adapted.query == "hello"
    assert skill.run(adapted).text == "HELLO"


def test_adapt_input_coerces_compatible_payload() -> None:
    skill = EchoSkill()
    adapted = skill.adapt_input({"query": "hello"})

    assert isinstance(adapted, QueryIn)
    assert adapted.query == "hello"


def test_adapt_input_fails_fast_on_mismatch() -> None:
    skill = NeedsOtherSkill()

    with pytest.raises(SkillContractError, match="NeedsOtherSkill") as exc_info:
        skill.adapt_input(QueryIn(query="hello"))

    message = str(exc_info.value)
    assert "other" in message
    assert "query" in message
