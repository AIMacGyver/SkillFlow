"""Run the example research pipeline: Search → Extract → Summarize."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from skills.extract import ExtractSkill
from skills.search import SearchInput, SearchSkill
from skills.summarize import SummarizeOutput, SummarizeSkill

from skillflow import LLMClient, OpenAICompatibleClient, Recipe, Runner, load_specificity


def build_research_recipe(llm: LLMClient | None = None) -> Recipe:
    """Compose the example research recipe.

    Args:
        llm: Optional chat client. Defaults to the local OpenAI-compatible client.

    Returns:
        A linear Search → Extract → Summarize recipe.
    """
    client = llm or OpenAICompatibleClient()
    extract_spec = load_specificity(REPO_ROOT / "specificity" / "extract.md")
    summarize_spec = load_specificity(REPO_ROOT / "specificity" / "summarize.md")
    if not isinstance(extract_spec, str) or not isinstance(summarize_spec, str):
        raise TypeError("Research specificity files must be Markdown or text.")

    return Recipe(
        name="research",
        skills=[
            SearchSkill(),
            ExtractSkill(llm=client, specificity=extract_spec),
            SummarizeSkill(llm=client, specificity=summarize_spec),
        ],
    )


def main(argv: list[str] | None = None) -> int:
    """Run the research recipe from the command line.

    Args:
        argv: Optional CLI arguments. Defaults to ``sys.argv[1:]``.

    Returns:
        Process exit code.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    query = " ".join(argv if argv is not None else sys.argv[1:]).strip()
    if not query:
        print('Usage: uv run python recipes/research.py "your research question"')
        return 2

    result = Runner().run(build_research_recipe(), SearchInput(query=query))
    if not isinstance(result, SummarizeOutput):
        raise TypeError(f"Expected SummarizeOutput, got {type(result).__name__}")

    print(result.summary)
    if result.sources:
        print("\nSources:")
        for url in result.sources:
            print(f"- {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
