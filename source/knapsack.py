import random
from datetime import datetime

MEMORY_DEPTH = 2048

class Knapsack:
    def __init__(self) -> None:
        self.capacity = None
        self.items = None
        self.weights = None
        self.values = None
        self.solution = None

    def set_seed(self, new_seed: int) -> None:
        self.seed = new_seed
        random.seed(self.seed)

    def generate_random_seed(self) -> None:
        self.seed = int(datetime.microsecond)
        random.seed(self.seed)

    def generate_weights(self, capacity: int, items: int) -> list:
        weights = [random.randint(int(capacity/4), int(capacity/2)) for _ in range(items)]
        return weights

    def generate_values(self, items: int) -> list:
        values = [random.randint(1, 100) for _ in range(items)]
        return values

    def solve_knapsack(self, weights: list, values: list, capacity: int, items: int):
        n = items
        dp = [[0] * (capacity + 1) for _ in range(n + 1)]

        for i in range(1, n + 1):
            for w in range(capacity + 1):
                if weights[i-1] <= w:
                    dp[i][w] = max(dp[i-1][w], dp[i-1][w-weights[i-1]] + values[i-1])
                else:
                    dp[i][w] = dp[i-1][w]

        w = capacity
        selection = [0] * n
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i-1][w]:
                selection[i-1] = 1
                w -= weights[i-1]

        return dp[n][capacity], selection

    def generate_problem(self, capacity: int, items: int):
        self.items = items
        self.capacity = capacity
        self.weights = self.generate_weights(capacity=self.capacity, 
                items=self.items)
        self.values = self.generate_values(items=self.items)
        self.solution, _ = self.solve_knapsack(weights=self.weights, 
                values=self.values, capacity=self.capacity, items=self.items)
    
    def __int_to_bin_str(self, num: int, bits=16) -> str:
        return format(num, f'0{bits}b')
    
    def write_problem_file(self, filename: str):
        if None in (self.capacity, self.items, self.weights, self.values):
            raise ValueError("Problema no generado. Utilizar generate_problem() primero.")

        size = MEMORY_DEPTH - 2 - 2* len(self.weights)
        with open(filename, "w+") as f:
            f.write(self.__int_to_bin_str(self.items) + "\n")
            f.write(self.__int_to_bin_str(self.capacity) + "\n")
            for w in self.weights:
                f.write(self.__int_to_bin_str(w) + "\n")
            for v in self.values:
                f.write(self.__int_to_bin_str(v) + "\n")
            for _ in range(size):
                f.write(self.__int_to_bin_str(0) + "\n")

    def write_solution_file(self, filename: str):
        if self.solution is None:
            raise ValueError("Solución no generada. Utilizar generate_problem() primero.")
        with open(filename, "w+") as f:
            f.write(self.__int_to_bin_str(self.solution) + "\n")
