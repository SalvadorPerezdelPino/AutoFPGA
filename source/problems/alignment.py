from .base_problem import BaseProblem
import random
from pathlib import Path

class AlignmentProblem(BaseProblem):
    def __init__(self, config_file=None) -> None:
        super().__init__(config_file)
        self.alphabet = self.config.get("alphabet", "ACGT")
        self.match_score = self.config.get("match_score", 1)
        self.mismatch_penalty = self.config.get("mismatch_penalty", -1)
        self.gap_penalty = self.config.get("gap_penalty", -2)
        self.sequence_1 = ""
        self.sequence_2 = ""
        self.result = None

    def generate_inputs(self) -> None:
        size_1 = self.config.get("sequence_1_size", 10)
        size_2 = self.config.get("sequence_2_size", 10)
        self.sequence_1 = "".join(random.choice(self.alphabet) for _ in range(size_1))
        self.sequence_2 = "".join(random.choice(self.alphabet) for _ in range(size_2))
        print(f"Generated sequences: {self.sequence_1}, {self.sequence_2}\n")

    def save_inputs(self) -> None:
        save_path = Path(self.store_dir) / f"input_{self.id}.txt"
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w+") as file:
            file.write(f"Match score: {self.match_score}\n")
            file.write(f"Mismatch score: {self.mismatch_penalty}\n")
            file.write(f"Gap penalty: {self.gap_penalty}\n")
            file.write(f"Sequence 1: {self.sequence_1}\n")
            file.write(f"Sequence 2: {self.sequence_2}\n")
        #print(f"Input stored in {save_path}\n")

    def save_inputs_for_fpga(self) -> None:
        save_path = Path(self.store_dir) / f"input_{self.id}.mem"
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w+") as file:
            file.write(f"{self.match_score & 0xFFFF:016b}\n")
            file.write(f"{self.mismatch_penalty & 0xFFFF:016b}\n")
            file.write(f"{self.gap_penalty & 0xFFFF:016b}\n")
            file.write(f"{len(self.sequence_1):016b}\n")
            file.write(f"{len(self.sequence_2):016b}\n")
            for symbol in self.sequence_1:
                file.write(f"{ord(symbol):016b}\n")
            for symbol in self.sequence_2:
                file.write(f"{ord(symbol):016b}\n")
        #print(f"Input stored for FPGA in {save_path}\n")

    def solve(self) -> int:
        rows = len(self.sequence_1)
        columns = len(self.sequence_2)

        scoring_matrix = [[0] * (columns + 1) for _ in range (rows + 1)]
        for i in range(1, rows + 1):
            for j in range(1, columns + 1):
                diagonal_score = self.match_score if self.sequence_1[i - 1] == self.sequence_2[j - 1] else self.mismatch_penalty
                scoring_matrix[i][j] = max(
                        scoring_matrix[i - 1][j - 1] + diagonal_score, 
                        scoring_matrix[i - 1][j] + self.gap_penalty, 
                        scoring_matrix[i][j - 1] + self.gap_penalty)
        self.result = scoring_matrix[rows][columns]
        return self.result

    def save_result(self) -> None:
        save_path = Path(self.store_dir) / f"expected_{self.id}.txt"
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w+") as file:
            file.write(f"Max score: {self.result}\n")
        #print(f"Solution stored in {save_path}\n")

    def save_result_for_fpga(self) -> None:
        save_path = Path(self.store_dir) / f"expected_{self.id}.mem"
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w+") as file:
            file.write(f"{self.result &0xFFFF:016b}\n")
        #print(f"Solution stored for FPGA in {save_path}\n")
