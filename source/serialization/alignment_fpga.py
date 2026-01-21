from pathlib import Path
from problems.alignment import AlignmentProblem
from serialization.base import ProblemSerializer

class AlignmentFPGASerializer(ProblemSerializer):
    def __init__(self, bit_width: int, memory_depth: int = 2048):
        self.bit_width = bit_width
        self.memory_depth = memory_depth

    def _fmt(self, value: int) -> str:
        return format(value, f"0{self.bit_width}b")
    
    def _to_twos_complement(self, value: int) -> int:
        mask = (1 << self.bit_width) - 1
        return value & mask

    def _fmt(self, value: int) -> str:
        max_val = (1 << (self.bit_width - 1)) - 1
        min_val = -(1 << (self.bit_width - 1))

        if not (min_val <= value <= max_val):
            raise ValueError(
                f"Value {value} does not fit in "
                f"{self.bit_width}-bit signed integer"
            )

        return format(
            self._to_twos_complement(value),
            f"0{self.bit_width}b"
        )
    
    def write(self, problem: AlignmentProblem, path: Path):
        data = problem.inputs()

        save_path = path / "input.mem"
        save_path.parent.mkdir(parents=True, exist_ok=True)

        lines = 0

        with open(save_path, "w") as file:
            def write_line(val):
                nonlocal lines
                file.write(self._fmt(val) + "\n")
                lines += 1

            write_line(data["match_score"])
            write_line(data["mismatch_penalty"])
            write_line(data["gap_penalty"])
            write_line(data["size_1"])
            write_line(data["size_2"])

            for symbol in data["sequence_1"]:
                write_line(ord(symbol))

            for symbol in data["sequence_2"]:
                write_line(ord(symbol))

            while lines < self.memory_depth:
                    write_line(0)

        solution = problem.solution()

        save_path = path / "expected.mem"

        with open(save_path, "w") as file:
            file.write(self._fmt(solution["solution"]) + "\n")