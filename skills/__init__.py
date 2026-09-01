"""Example reusable skills. Task-specific prompts live in ``specificity/``."""

from skills.extract import ExtractInput, ExtractOutput, ExtractSkill
from skills.search import SearchClient, SearchInput, SearchOutput, SearchResult, SearchSkill
from skills.summarize import SummarizeInput, SummarizeOutput, SummarizeSkill

__all__ = [
    "ExtractInput",
    "ExtractOutput",
    "ExtractSkill",
    "SearchClient",
    "SearchInput",
    "SearchOutput",
    "SearchResult",
    "SearchSkill",
    "SummarizeInput",
    "SummarizeOutput",
    "SummarizeSkill",
]
