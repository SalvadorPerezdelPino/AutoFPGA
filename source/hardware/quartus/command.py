from pathlib import Path
import subprocess
import logging

logger = logging.getLogger(__name__)

class QuartusCommandError(RuntimeError):
    pass

class QuartusCommand:
    def __init__(self, command: list[str]):
        self.base_command = command
        
    def run(self, project: Path = None, extra_args: list[str] = None, cwd: Path = None, verbose: bool = False, auto_append_project: bool = True):
        if project and not project.exists():
            raise FileNotFoundError(f"Project file/path not found: {project}")
            
        if cwd and not cwd.exists():
            raise FileNotFoundError(f"Working directory not found: {cwd}")
        
        final_cmd = self.base_command.copy()
        
        if extra_args: # For adding arguments next to the command
            final_cmd.extend(extra_args)

        if auto_append_project:
            final_cmd.append(project.as_posix())
        
        execution_dir = cwd if cwd else (project.parent if project else Path.cwd())

        logger.info(f"Executing {final_cmd} command in project {execution_dir}")

        result = subprocess.run(
            final_cmd,
            cwd=execution_dir, 
            stdout=None if verbose else subprocess.DEVNULL, 
            stderr=None if verbose else subprocess.DEVNULL
        )
        
        if result.returncode != 0:
            raise QuartusCommandError(
                f"{final_cmd} failed for project {execution_dir}"
            )