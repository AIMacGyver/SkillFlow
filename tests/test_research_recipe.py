"""Offline behavior tests for the example research recipe."""

import pytest
from recipes.research import build_research_recipe, main
from skills.search import SearchInput
from skills.summarize import SummarizeOutput
from tests.helpers import FakeSearchClient

from skillflow import Runner, StubLLMClient


def test_research_recipe_runs_offline_with_stubs() -> None:
    search = FakeSearchClient()
    llm = StubLLMClient(
        responses=[
            "- Kubeflow runs ML on Kubernetes\n- It includes pipelines and serving",
            "Kubeflow is an open-source toolkit for running ML on Kubernetes.",
        ]
    )

    result = Runner().run(
        build_research_recipe(llm=llm, search_client=search),
        SearchInput(query="What is Kubeflow?"),
    )

    assert isinstance(result, SummarizeOutput)
    assert result.query == "What is Kubeflow?"
    assert result.summary == "Kubeflow is an open-source toolkit for running ML on Kubernetes."
    assert result.sources == ["https://example.com/kubeflow"]
    assert search.queries == [("What is Kubeflow?", 5)]


def test_research_cli_requires_a_query(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 2
    assert "Usage:" in capsys.readouterr().out
