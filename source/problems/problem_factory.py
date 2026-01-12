from typing import Dict, Type
from problems.base_problem import BaseProblem
from problems.alignment import AlignmentProblem
from problems.knapsack import KnapsackProblem

class ProblemFactory:
    _problems: Dict[str, Type[BaseProblem]] = {
        "alignment": AlignmentProblem,
        "knapsack": KnapsackProblem
    }

    @classmethod
    def get(cls, name: str, params: dict, problem_id: str = None) -> BaseProblem:
        if name not in cls._problems:
            valid_keys = ", ".join(cls._problems.keys())
            raise ValueError(f"Unknown problem: '{name}'. Availables: {valid_keys}")

        problem_class = cls._problems[name]

        try:
            instance = problem_class(config=params, problem_id=problem_id)
            return instance
        except Exception as e:
            raise RuntimeError(f"Error while instancing '{name}' problem: {e}") from e
