import random
import json

class Alignment():
    def __init__(self):
        self.sequence_1 = None
        self.sequence_2 = None
        self.gap_penalty = -1
        self.scoring_matrix = []
        self.match_score = 1

    def load_json_data(self, json_file):
        with open(json_file, "r") as file:
            data = json.load(json_file)
        
        self.gap_penalty = data
        self.match_score = data.get("match_score", 1)
        self.alphabet = data.get("alphabet", "")


    def solve_problem(self, sequence_1, sequence_2) -> int:
        rows = len(sequence_1)
        columns = len(sequence_2)
        scoring_matrix = [[0] * (columns + 1) for _ in range (rows + 1)]
        for i in range(1, rows + 1):
            for j in range(1, columns + 1):
                if sequence_1[i - 1] == sequence_2[j - 1]:
                    scoring_matrix[i][j] = scoring_matrix[i - 1][j - 1] + self.match_score
                else:
                    scoring_matrix[i][j] = max(scoring_matrix[i - 1][j], scoring_matrix[i][j - 1])
        return scoring_matrix[rows][columns]
        

    def generate_inputs(self):
        size_1 = 10
        size_2 = 10
        sequence_1 = []
        sequence_2 = []
        alphabet = "ACGT"

        for _ in range(size_1):
            sequence_1.append(random.randint(0, len(alphabet)))

        for _ in range(size_2):
            sequence_2.append(random.randint(0, len(alphabet)))

        with open("", "w+") as file1:
            for symbol in sequence_1:
                file1.write(f"{symbol:016b}\n")
        
        with open("", "w+") as file2:
            for symbol in sequence_2:
                file2.write(f"{symbol:016b}\n")

    def generate_solution(self):
        a = None
        b = None
        result = self.solve_problem(a, b)
        
        with open("", "w+") as file:
            file.write(result)