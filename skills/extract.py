"""LLM-backed skill that turns search hits into concise findings."""

from pydantic import BaseModel, Field

from skillflow import ChatMessage, LLMClient, Skill
from skills.search import SearchResult


class ExtractInput(BaseModel):
    """Input contract for ``ExtractSkill``. Matches ``SearchOutput``.

    Attributes:
        query: Original research query.
        results: Search hits to read.
    """

    query: str
    results: list[SearchResult]


class ExtractOutput(BaseModel):
    """Output contract for ``ExtractSkill``.

    Attributes:
        query: Original research query.
        findings: Bullet findings pulled from the sources.
        sources: Source URLs that informed the findings.
    """

    query: str
    findings: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)


class ExtractSkill(Skill[ExtractInput, ExtractOutput]):
    """Extract reusable facts from search results.

    The skill stays generic. Tone, focus, and formatting live in the
    specificity file passed to the constructor.

    Args:
        llm: Chat client used to read the sources.
        specificity: External extraction instructions.
    """

    def __init__(self, llm: LLMClient, specificity: str) -> None:
        """Create the skill.

        Args:
            llm: Chat client used to read the sources.
            specificity: External extraction instructions.
        """
        self._llm = llm
        self._specificity = specificity

    def run(self, data: ExtractInput) -> ExtractOutput:
        """Ask the model for findings grounded in the search hits.

        Args:
            data: Query plus search results.

        Returns:
            Findings and the source URLs they came from.
        """
        sources = [result.url for result in data.results if result.url]
        formatted = (
            "\n".join(f"- {result.title} ({result.url}): {result.snippet}" for result in data.results)
            or "(no search results)"
        )
        user_prompt = f"Query: {data.query}\n\nSearch results:\n{formatted}"
        text = self._llm.complete(
            [
                ChatMessage(role="system", content=self._specificity),
                ChatMessage(role="user", content=user_prompt),
            ]
        )
        findings = [line.lstrip("-* ").strip() for line in text.splitlines() if line.strip()]
        return ExtractOutput(query=data.query, findings=findings, sources=sources)
