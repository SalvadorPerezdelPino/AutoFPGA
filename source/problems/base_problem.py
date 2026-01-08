from abc import ABC, abstractmethod

class BaseProblem(ABC):
    """Interface for any problem"""

    def __init__(self, config: dict, problem_id: int = None):
        self.config = config 
        self.id = problem_id

    @abstractmethod
    def inputs(self) -> dict:
        pass

    @abstractmethod
    def solution(self) -> dict:
        pass

    @abstractmethod
    def size(self) -> int:
        pass

    @abstractmethod
    def dimensions(self) -> dict:
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    def problem_type(self) -> str:
        return self.__class__.__name__.lower()