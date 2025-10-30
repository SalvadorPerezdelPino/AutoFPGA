from base_problem import BaseProblem
import random
from pathlib import Path

class AlignmentProblem(BaseProblem):
    def __init__(self, config_file=None):
        super().__init__(config_file)
        self.alphabet = self.config.get("alphabet", "ACGT")
        self.match_score = self.config.get("match_score", 1)
        self.mismatch_penalty = self.config.get("mismatch_penalty", -1)
        self.gap_penalty = self.config.get("gap_penalty", -2)
        self.sequence_1 = ""
        self.sequence_2 = ""
        self.result = None

    def generate_inputs(self):
        size_1 = self.config.get("sequence_size_1", 10)
        size_2 = self.config.get("sequence_size_2", 10)
        self.sequence_1 = "".join(random.choice(self.alphabet) for _ in range(size_1))
        self.sequence_2 = "".join(random.choice(self.alphabet) for _ in range(size_2))
        print(f"Generated sequences: {self.sequence_1}, {self.sequence_2}")

    def save_inputs(self, save_path_1, save_path_2):
        Path(save_path_1).parent.mkdir(parents=True, exist_ok=True)
        Path(save_path_2).parent.mkdir(parents=True, exist_ok=True)

        with open(save_path_1, "w+") as file_1:
            for symbol in self.sequence_1:
                file_1.write(f"{ord(symbol):016b}\n")

        with open(save_path_2, "w+") as file_2:
            for symbol in self.sequence_2:
                file_2.write(f"{ord(symbol):016b}\n")

    def solve_problem(self) -> int:
        rows = len(self.sequence_1)
        columns = len(self.sequence_2)

        scoring_matrix = [[0] * (columns + 1) for _ in range (rows + 1)]
        for i in range(1, rows + 1):
            for j in range(1, columns + 1):
                if self.sequence_1[i - 1] == self.sequence_2[j - 1]:
                    scoring_matrix[i][j] = scoring_matrix[i - 1][j - 1] + self.match_score
                else:
                    scoring_matrix[i][j] = max(scoring_matrix[i - 1][j] + self.gap_penalty, scoring_matrix[i][j - 1] + self.gap_penalty)
        self.result = scoring_matrix[rows][columns]
        return self.result

    def save_result(self, save_path):
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w+") as file:
            file.write(f"{self.result:016b}\n")
        print(f"Solution stored in {save_path}")
