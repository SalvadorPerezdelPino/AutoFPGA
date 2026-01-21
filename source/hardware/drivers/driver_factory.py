from hardware.drivers.base_driver import DeviceDriver
from hardware.drivers.cpu import CPUDriver
from hardware.drivers.asic import ASICDriver
from hardware.quartus.compiler import QuartusCompiler
from hardware.quartus.timing import TimingAnalyzer
from hardware.quartus.simulator import QuartusSimulator
from pathlib import Path

class DriverFactory():
    def __init__(self, devices_config: dict, compiler: QuartusCompiler, timing_analyzer: TimingAnalyzer, simulator: QuartusSimulator):
        self.config = devices_config
        self.compiler = compiler
        self.timing_analyzer = timing_analyzer
        self.simulator = simulator
        self._instances = {}

    def get(self, driver_name: str) -> DeviceDriver:
        if driver_name in self._instances:
            return self._instances[driver_name]
        
        if driver_name not in self.config:
            raise ValueError(f"Device {driver_name} not defined in the configuration file.")

        driver_config = self.config[driver_name]
        driver_type = driver_config.get("type")
        project_path = Path(driver_config["quartus_project_path"])
        simulation_path = Path(driver_config["simulation_path"])

        driver = None
        if driver_type == "cpu":
            driver = CPUDriver(
                name=driver_name, 
                project_path=project_path,
                simulation_path=simulation_path, 
                compiler=self.compiler, 
                timing_analyzer=self.timing_analyzer,
                simulator=self.simulator
            )
        elif driver_type == "asic":
            driver = ASICDriver(
                name=driver_name, 
                project_path=project_path, 
                compiler=self.compiler, 
                timing_analyzer=self.timing_analyzer,
                simulator=self.simulator
            )
        else:
            raise ValueError(f"Unknown device type: {driver_type}")
        
        self._instances[driver_name] = driver
        return driver
        
