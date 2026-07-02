from abc import ABC, abstractmethod
from pathlib import Path

from rie.application.batch import Batch


class BatchDiscovery(ABC):

    @abstractmethod
    def discover(
        self,
        root: Path
    ) -> Batch:
        """Discover and build a Batch from the given path."""
        raise NotImplementedError()