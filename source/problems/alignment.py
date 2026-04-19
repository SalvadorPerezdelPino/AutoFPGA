from .base_problem import BaseProblem
import random
from pathlib import Path

class AlignmentProblem(BaseProblem):
    SWEEP_PARAMS = ["sequence_1_size", "sequence_2_size"]
    def __init__(self, config, problem_id) -> None:
        super().__init__(config, problem_id)
        self.alphabet = self.config.get("alphabet", "ACGT")
        self.match_score = self.config.get("match_score", 1)
        self.mismatch_penalty = self.config.get("mismatch_penalty", -1)
        self.gap_penalty = self.config.get("gap_penalty", -2)
        self.sequence_1 = ""
        self.sequence_2 = ""

        self.size_1 = self.config.get("sequence_1_size", 10)
        self.size_2 = self.config.get("sequence_2_size", 10)
        self.sequence_1 = "".join(self.rng.choice(self.alphabet) for _ in range(self.size_1))
        self.sequence_2 = "".join(self.rng.choice(self.alphabet) for _ in range(self.size_2))

    def inputs(self) -> dict:
        return {
            "size_1": self.size_1,
            "size_2": self.size_2,
            "sequence_1": self.sequence_1,
            "sequence_2": self.sequence_2,
            "match_score": self.match_score,
            "mismatch_penalty": self.mismatch_penalty,
            "gap_penalty": self.gap_penalty
        }

    def solution(self) -> dict:
        return {
            "solution": self.solve()
        }

    def size(self):
        return (self.size_1 + 1) * (self.size_2 + 1)

    def dimensions(self) -> dict:
        return {
            "sizeA": self.size_1,
            "sizeB": self.size_2,
            "matrix_elements": self.size()
        }

    def solve(self) -> int:
        rows = len(self.sequence_1)
        columns = len(self.sequence_2)

        scoring_matrix = [[0] * (columns + 1) for _ in range (rows + 1)]
        for j in range(1, columns + 1):
            scoring_matrix[0][j] = self.gap_penalty * j
        for i in range(1, rows + 1):
            scoring_matrix[i][0] = self.gap_penalty * i

        for i in range(1, rows + 1):
            for j in range(1, columns + 1):
                diagonal_score = self.match_score if self.sequence_1[i - 1] == self.sequence_2[j - 1] else self.mismatch_penalty
                scoring_matrix[i][j] = max(
                        scoring_matrix[i - 1][j - 1] + diagonal_score, 
                        scoring_matrix[i - 1][j] + self.gap_penalty, 
                        scoring_matrix[i][j - 1] + self.gap_penalty)
        result = scoring_matrix[rows][columns]
        return result

    def to_dict(self) -> dict:
        data = {
            "problem_name" : "alignment",
            "alphabet": self.alphabet,
            "match_score": self.match_score,
            "mismatch_penalty": self.mismatch_penalty,
            "gap_penalty": self.gap_penalty,
            "sequence_1_size" : self.size_1,
            "sequence_2_size": self.size_2
        }
        return data
