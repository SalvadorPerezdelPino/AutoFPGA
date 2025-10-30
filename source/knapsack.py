from base_problem import BaseProblem
import random
from pathlib import Path

class KnapsackProblem(BaseProblem):
    def __init__(self, config_file=None) -> None:
        super.__init__(config_file)
        self.capacity = config_file.get("capacity", 50)
        self.items = config_file.get("items", 20)
        self.values = []
        self.weights = []
        self.result = None

    def generate_inputs(self):
        self.values = [random.randint(1, 100) for _ in range(self.items)]
        self.weights = [random.randint(self.capacity/4, self.capacity/2) for _ in range(self.items)]
        print(f"Values: {self.values}")
        print(f"Weights: {self.weights}")

    def save_inputs(self):
        pass

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

    def save_result(self, save_path):
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w") as f:
            f.write(f"{self.result:016b}\n")
        print(f"Result stored in {save_path}")
