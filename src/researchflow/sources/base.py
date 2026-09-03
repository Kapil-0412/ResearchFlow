from abc import ABC, abstractmethod
from collections.abc import Iterator

from researchflow.models import Paper


class PaperSource(ABC):
    """Interface that every paper source must implement."""

    name: str

    @abstractmethod
    def search(
        self,
        query: str,
        *,
        max_results: int = 100,
    ) -> Iterator[Paper]:
        """Search the source and yield normalized Paper objects."""
        raise NotImplementedError