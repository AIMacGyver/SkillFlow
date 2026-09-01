"""Deterministic web search skill with a swappable search client."""

from typing import Protocol

from ddgs import DDGS
from pydantic import BaseModel, Field

from skillflow import Skill


class SearchResult(BaseModel):
    """A single search hit.

    Attributes:
        title: Result title.
        url: Result URL.
        snippet: Short text excerpt.
    """

    title: str
    url: str
    snippet: str


class SearchInput(BaseModel):
    """Input contract for ``SearchSkill``.

    Attributes:
        query: Search query.
        limit: Maximum number of results to return.
    """

    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=10)


class SearchOutput(BaseModel):
    """Output contract for ``SearchSkill``.

    Attributes:
        query: Echo of the original query.
        results: Ranked search hits.
    """

    query: str
    results: list[SearchResult]


class SearchClient(Protocol):
    """Looks up web results for a query without using an LLM."""

    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        """Return search hits for ``query``.

        Args:
            query: Search query.
            limit: Maximum number of results.

        Returns:
            Ranked search hits.
        """


class DuckDuckGoSearchClient:
    """Search the web with DuckDuckGo. No API key required."""

    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        """Return DuckDuckGo text results.

        Args:
            query: Search query.
            limit: Maximum number of results.

        Returns:
            Ranked search hits.
        """
        hits = DDGS().text(query, max_results=limit)
        return [
            SearchResult(
                title=str(hit.get("title") or ""),
                url=str(hit.get("href") or ""),
                snippet=str(hit.get("body") or ""),
            )
            for hit in hits
        ]


class SearchSkill(Skill[SearchInput, SearchOutput]):
    """Find source pages for a query using a deterministic search client.

    Args:
        client: Search backend. Defaults to DuckDuckGo.
    """

    def __init__(self, client: SearchClient | None = None) -> None:
        """Create the skill.

        Args:
            client: Search backend. Defaults to DuckDuckGo.
        """
        self._client = client or DuckDuckGoSearchClient()

    def run(self, data: SearchInput) -> SearchOutput:
        """Search the web and return structured hits.

        Args:
            data: Query and result limit.

        Returns:
            Structured search results for the next skill.
        """
        results = self._client.search(data.query, limit=data.limit)
        return SearchOutput(query=data.query, results=results)
