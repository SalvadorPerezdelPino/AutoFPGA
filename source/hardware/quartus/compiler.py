from hardware.quartus.command import QuartusCommand, QuartusCommandError
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class QuartusCompiler:
    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose
        self.commands = {
            "map": QuartusCommand(["quartus_map"]),
            "fit": QuartusCommand(["quartus_fit"]),
            "asm": QuartusCommand(["quartus_asm"]),
            "sta": QuartusCommand(["quartus_sta"]),
            "eda": QuartusCommand(["quartus_eda"]),
            "full": QuartusCommand(["quartus_sh", "--flow", "compile"])
        }

    def _run(self, project_path: Path, command_key: str):
        try:
            self.commands[command_key].run(project_path, self.verbose)
        except QuartusCommandError as e:
            logger.error(str(e))
            raise

    def synthetize(self, project_path: Path) -> None:
        self._run(project_path, "map")

    def fit(self, project_path) -> None:
        self._run(project_path, "fit")

    def assemble(self, project_path: Path) -> None:
        self._run(project_path, "asm")

    def timing(self, project_path: Path) -> None:
        self._run(project_path, "sta")

    def netlist(self, project_path: Path) -> None:
        self._run(project_path, "eda")

    def compile_all(self, project_path: Path) -> None:
        self._run(project_path, "full")