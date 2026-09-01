"""Behavior tests for linear recipes and the runner."""

import logging

import pytest
from pydantic import BaseModel

from skillflow import Recipe, Runner, Skill, SkillContractError


class QueryIn(BaseModel):
    query: str


class QueryOut(BaseModel):
    query: str
    text: str


class OtherIn(BaseModel):
    other: str


class UpperSkill(Skill[QueryIn, QueryOut]):
    def run(self, data: QueryIn) -> QueryOut:
        return QueryOut(query=data.query, text=data.query.upper())


class SuffixSkill(Skill[QueryOut, QueryOut]):
    def run(self, data: QueryOut) -> QueryOut:
        return QueryOut(query=data.query, text=f"{data.text}!")


class NeedsOtherSkill(Skill[OtherIn, QueryOut]):
    def run(self, data: OtherIn) -> QueryOut:
        return QueryOut(query=data.other, text=data.other)


def test_runner_wires_output_into_next_input() -> None:
    recipe = Recipe("echo", [UpperSkill(), SuffixSkill()])

    result = Runner().run(recipe, QueryIn(query="hello"))

    assert isinstance(result, QueryOut)
    assert result.text == "HELLO!"


def test_runner_logs_pydantic_models_between_steps(caplog: pytest.LogCaptureFixture) -> None:
    recipe = Recipe("echo", [UpperSkill(), SuffixSkill()])

    with caplog.at_level(logging.INFO, logger="skillflow"):
        Runner().run(recipe, QueryIn(query="hello"))

    assert "Starting recipe 'echo' with 2 step(s)" in caplog.text
    assert 'skill=UpperSkill input={"query":"hello"}' in caplog.text
    assert 'skill=UpperSkill output={"query":"hello","text":"HELLO"}' in caplog.text
    assert 'skill=SuffixSkill output={"query":"hello","text":"HELLO!"}' in caplog.text
    assert "Finished recipe 'echo'" in caplog.text


def test_runner_fails_fast_when_contracts_do_not_match() -> None:
    recipe = Recipe("broken", [UpperSkill(), NeedsOtherSkill()])

    with pytest.raises(SkillContractError, match="NeedsOtherSkill"):
        Runner().run(recipe, QueryIn(query="hello"))


def test_recipe_requires_a_name_and_skills() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        Recipe(" ", [UpperSkill()])
    with pytest.raises(ValueError, match="at least one skill"):
        Recipe("empty", [])
