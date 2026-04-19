from .base_problem import BaseProblem
import random
from pathlib import Path

class KnapsackProblem(BaseProblem):
    SWEEP_PARAMS = ["capacity", "items"]
    def __init__(self, config, problem_id) -> None:
        super().__init__(config, problem_id)
        self.capacity = config.get("capacity", 50)
        self.items = config.get("items", 20)
        self.values = []
        self.weights = []
        self.result = None

        self.values = [self.rng.randint(1, 100) for _ in range(self.items)]
        self.weights = [self.rng.randint(int(self.capacity/4), int(self.capacity/2)) for _ in range(self.items)]

    def inputs(self) -> dict:
        return {
            "capacity": self.capacity,
            "items": self.items,
            "values": self.values,
            "weights": self.weights
        }

    def solution(self) -> dict:
        return {
            "solution": self.solve()
        }

    def size(self):
        return (self.capacity + 1) * (self.items + 1)

    def dimensions(self) -> dict:
        return {
            "sizeA": self.capacity,
            "sizeB": self.items,
            "matrix_elements": self.size()
        }

    def solve(self):
        dp = [[0] * (self.capacity + 1) for _ in range(self.items + 1)]

        for i in range(1, self.items + 1):
            for w in range(self.capacity + 1):
                if self.weights[i - 1] <= w:
                    dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - self.weights[i - 1]] + self.values[i - 1])
                else:
                    dp[i][w] = dp[i - 1][w]

        self.result = dp[self.items][self.capacity]
        return self.result
    
    def to_dict(self) -> dict:
        data = {
            "problem_name" : "knapsack",
            "capacity" : self.capacity,
            "items": self.items
        }
        return data
