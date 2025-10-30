from abc import ABC, abstractmethod
import json

class BaseProblem(ABC):
    """Interface for any problem"""

    def __init__(self, config_file=None):
        self.config = {}
        if config_file:
            self.load_config(config_file)

    def load_config(self, json_file):
        with open(json_file, "r") as file:
            self.config = json.load(file)

    def run(self, store_dir):
        self.store_dir = store_dir
        self.generate_inputs()
        self.save_inputs()
        self.save_inputs_for_fpga()
        self.solve()
        self.save_result()
        self.save_result_for_fpga()
    
    @abstractmethod
    def generate_inputs(self):
        pass

    @abstractmethod
    def save_inputs(self):
        pass

    @abstractmethod
    def save_inputs_for_fpga(self):
        pass

    @abstractmethod
    def solve(self):
        pass

    @abstractmethod
    def save_result(self):
        pass

    @abstractmethod
    def save_result_for_fpga(self):
        pass