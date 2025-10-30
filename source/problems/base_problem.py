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

    
    @abstractmethod
    def generate_inputs(self):
        pass

    @abstractmethod
    def solve(self):
        pass

    @abstractmethod
    def save_result(self, save_path):
        pass