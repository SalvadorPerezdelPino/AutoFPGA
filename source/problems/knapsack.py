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

        self.values = [random.randint(1, 100) for _ in range(self.items)]
        self.weights = [random.randint(int(self.capacity/4), int(self.capacity/2)) for _ in range(self.items)]

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

    #def generate_inputs(self):
    #    self.values = [random.randint(1, 100) for _ in range(self.items)]
    #    self.weights = [random.randint(int(self.capacity/4), int(self.capacity/2)) for _ in range(self.items)]
    #    print(f"Values: {self.values}")
    #    print(f"Weights: {self.weights}")

    #def save_inputs(self) -> None:
    #    save_path = Path(self.store_dir) / f"input_{self.id}.txt"
    #    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    #    with open(save_path, "w+") as file:
    #        file.write(f"Number of items: {self.items}\n")
    #        file.write(f"Capacity: {self.capacity}\n")
    #        file.write(f"Weights: {self.weights}\n")
    #        file.write(f"Values: {self.values}\n")
    #    #print(f"Input stored in {save_path}\n")

    #def save_inputs_for_fpga(self):
    #    save_path = Path(self.store_dir) / f"input_{self.id}.mem"
    #    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    #    with open(save_path, "w+") as file:
    #        file.write(f"{self.items:016b}\n")
    #        file.write(f"{self.capacity:016b}\n")
    #        for w in self.weights:
    #            file.write(f"{w:016b}\n")
    #        for v in self.values:
    #            file.write(f"{v:016b}\n")
    #    #print(f"Input stored in {save_path}\n")

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

    #def save_result(self):
    #    save_path = Path(self.store_dir) / f"expected_{self.id}.txt"
    #    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    #    with open(save_path, "w") as f:
    #        f.write(f"Max value: {self.result}\n")
    #    #print(f"Result stored in {save_path}\n")

    #def save_result_for_fpga(self):
    #    save_path = Path(self.store_dir) / f"expected_{self.id}.mem"
    #    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    #    with open(save_path, "w") as f:
    #        f.write(f"{self.result:016b}\n")
    #    #print(f"Result stored in {save_path}\n")

    def to_dict(self) -> dict:
        data = {
            "problem_name" : "knapsack",
            "capacity" : self.capacity,
            "items": self.items
        }
        return data
