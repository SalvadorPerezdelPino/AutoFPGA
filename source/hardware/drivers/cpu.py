from hardware.drivers.base_driver import DeviceDriver
from hardware.quartus.command import QuartusCommandError
from hardware.quartus.compiler import QuartusCompiler
from hardware.quartus.timing import TimingAnalyzer
from pathlib import Path
import logging


logger = logging.getLogger(__name__)

class CPUDriver(DeviceDriver):
    def __init__(self, project_path: Path, name: str, compiler: QuartusCompiler, timing_analyzer: TimingAnalyzer):
        super().__init__(project_path, name, compiler)
        self.compiled = False
        self.timing_analyzer = timing_analyzer
        self.fmax = None

    def prepare_hardware(self, params: dict) -> None:
        # No need to compile between test, but at least once per machine
        if not self.compiled:
            try:
                self.build()
                self.compiled = True
            except QuartusCommandError:
                logger.error(f"Failed to compile {self.name}")
        else:
            logger.info(f"{self.name} already compiled, skipping process")
    
    def build(self) -> None:
        self.compiler.compile_all(project_path=self.project_path)
        self.fmax = self.timing_analyzer.get_fmax(project_path=self.project_path)
        logger.info(f"Device {self.name} fmax: {self.fmax} MHz")

    def run_simulation(self, output_dir: Path) -> None:
        logger.debug(f"Running {self.name} simulation")
        # TODO: Finish