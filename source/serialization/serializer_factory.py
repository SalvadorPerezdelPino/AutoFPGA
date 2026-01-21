from typing import Dict, Type
from serialization.base import ProblemSerializer
from serialization.alignment_fpga import AlignmentFPGASerializer
from serialization.knapsack_fpga import KnapsackFPGASerializer

class SerializerFactory:
    _serializers: Dict[str, Type[ProblemSerializer]] = {
        "alignment": AlignmentFPGASerializer,
        "knapsack": KnapsackFPGASerializer
    }

    @classmethod
    def get(cls, problem_name: str, config: dict) -> ProblemSerializer:
        if problem_name not in cls._serializers:
            raise ValueError(f"Unknown serializer for problem: {problem_name}")

        serializer_class = cls._serializers[problem_name]
        
        bit_width = config.get("bit_width", 32)
        
        return serializer_class(bit_width=bit_width)