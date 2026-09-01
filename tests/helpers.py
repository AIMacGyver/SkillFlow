"""Shared test doubles used by behavior tests."""

from skills.search import SearchResult


class FakeSearchClient:
    """Return canned search hits without touching the network."""

    def __init__(self, results: list[SearchResult] | None = None) -> None:
        self.results = results or [
            SearchResult(
                title="Kubeflow",
                url="https://example.com/kubeflow",
                snippet="Kubeflow is an open-source ML toolkit on Kubernetes.",
            )
        ]
        self.queries: list[tuple[str, int]] = []

    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        self.queries.append((query, limit))
        return self.results[:limit]
