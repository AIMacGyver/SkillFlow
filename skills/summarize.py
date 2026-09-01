"""LLM-backed skill that turns extracted findings into a short brief."""

from pydantic import BaseModel, Field

from skillflow import ChatMessage, LLMClient, Skill


class SummarizeInput(BaseModel):
    """Input contract for ``SummarizeSkill``. Matches ``ExtractOutput``.

    Attributes:
        query: Original research query.
        findings: Facts to summarize.
        sources: Source URLs to keep with the brief.
    """

    query: str
    findings: list[str]
    sources: list[str] = Field(default_factory=list)


class SummarizeOutput(BaseModel):
    """Output contract for ``SummarizeSkill``.

    Attributes:
        query: Original research query.
        summary: Short research brief.
        sources: Source URLs to keep with the brief.
    """

    query: str
    summary: str
    sources: list[str] = Field(default_factory=list)


class SummarizeSkill(Skill[SummarizeInput, SummarizeOutput]):
    """Write a concise brief from extracted findings.

    The skill stays generic. Audience, length, and style live in the
    specificity file passed to the constructor.

    Args:
        llm: Chat client used to write the brief.
        specificity: External summarization instructions.
    """

    def __init__(self, llm: LLMClient, specificity: str) -> None:
        """Create the skill.

        Args:
            llm: Chat client used to write the brief.
            specificity: External summarization instructions.
        """
        self._llm = llm
        self._specificity = specificity

    def run(self, data: SummarizeInput) -> SummarizeOutput:
        """Summarize findings into a short brief.

        Args:
            data: Query, findings, and sources.

        Returns:
            A brief plus the original source URLs.
        """
        bullets = "\n".join(f"- {finding}" for finding in data.findings) or "- (no findings)"
        user_prompt = f"Query: {data.query}\n\nFindings:\n{bullets}"
        summary = self._llm.complete(
            [
                ChatMessage(role="system", content=self._specificity),
                ChatMessage(role="user", content=user_prompt),
            ]
        )
        return SummarizeOutput(query=data.query, summary=summary, sources=data.sources)
