from pathlib import Path
import subprocess
import logging

logger = logging.getLogger(__name__)

class QuartusCommandError(RuntimeError):
    pass

class QuartusCommand:
    def __init__(self, command: list[str]):
        self.command = command
        
    def run(self, project: Path, verbose: bool = False):
        if not project.exists():
            raise FileNotFoundError(f"Project not found: {project}")

        logger.info(f"Executing {self.command} command in project {project}")

        result = subprocess.run(
            self.command + [project.as_posix()], 
            stdout=None if verbose else subprocess.DEVNULL, 
            stderr=None if verbose else subprocess.DEVNULL
        )
        
        if result.returncode != 0:
            raise QuartusCommandError(
                f"{self.command} failed for project {project}"
            )