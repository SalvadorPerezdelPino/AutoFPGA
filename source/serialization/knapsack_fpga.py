from pathlib import Path
from problems.knapsack import KnapsackProblem
from serialization.base import ProblemSerializer

class KnapsackFPGASerializer(ProblemSerializer):
    def __init__(self, bit_width: int):
        self.bit_width = bit_width

    def _fmt(self, value: int) -> str:
        return format(value, f"0{self.bit_width}b")

    def write(self, problem: KnapsackProblem, path: Path):
        data = problem.inputs()

        save_path = path / f"input_{problem.id}.mem"
        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, "w") as f:
            f.write(self._fmt(data["items"]) + "\n")
            f.write(self._fmt(data["capacity"]) + "\n")

            for w in data["weights"]:
                f.write(self._fmt(w) + "\n")

            for v in data["values"]:
                f.write(self._fmt(v) + "\n")
