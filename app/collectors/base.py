from abc import ABC, abstractmethod

class JobCollector(ABC):
    @abstractmethod
    def collect(self) -> list[dict]:
        """Return normalized job dictionaries."""
        raise NotImplementedError
