from abc import ABC, abstractmethod
from pathlib import Path

class ProblemSerializer(ABC):
    @abstractmethod
    def write(self, problem, path: Path) -> None:
        pass