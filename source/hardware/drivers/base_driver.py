from hardware.quartus.compiler import QuartusCompiler
from pathlib import Path
from abc import ABC, abstractmethod

class DeviceDriver(ABC):
    def __init__(self, project_path: Path, simulation_path: Path, name: str, compiler: QuartusCompiler):
        self.name = name
        self.project_path = project_path
        self.simulation_path = simulation_path
        self.compiler = compiler

    @abstractmethod
    def prepare_hardware(self, device_name: str, params: dict):
        pass

    @abstractmethod
    def build(self):
        pass

    @abstractmethod
    def run_simulation(self, output_dir: Path):
        pass