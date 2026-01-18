from pathlib import Path
import re
from hardware.quartus.command import QuartusCommand, QuartusCommandError
import logging

logger = logging.getLogger(__name__)

class TimingAnalyzer:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.sta_command = QuartusCommand(["quartus_sta"])

    def get_fmax(self, project_path: Path) -> float:
        if project_path.is_file():
            project_dir = project_path.parent
            project_name = project_path.stem
        else:
            project_dir = project_path
            try:
                qpf_file = next(project_dir.glob("*.qpf"))
                project_name = qpf_file.stem
            except StopIteration:
                raise FileNotFoundError(f"No .qpf file found in {project_dir}")

        script_name = "get_fmax.tcl"
        report_name = "fmax_summary.txt"
        
        self._create_tcl_script(project_dir / script_name, project_name, report_name)
        try:
            self.sta_command.run(
                cwd=project_dir, 
                extra_args=["-t", script_name],
                verbose=self.verbose,
                auto_append_project=False 
            )
        except QuartusCommandError:
            logger.error(f"Timing analysis failed for {project_name}")
            return 0.0

        return self._parse_fmax_result(project_dir / report_name)

    def _create_tcl_script(self, script_path: Path, project_name: str, report_file: str):
        content = f"""
        project_open {project_name}
        create_timing_netlist
        read_sdc
        update_timing_netlist
        
        # Reportar a archivo
        report_clock_fmax_summary -file "{report_file}"
        
        project_close
        """
        with open(script_path, "w") as f:
            f.write(content)

    def _parse_fmax_result(self, report_path: Path) -> float:
        if not report_path.exists():
            logger.warning(f"Fmax report not found: {report_path}")
            return 0.0
            
        with open(report_path, "r") as f:
            content = f.read()
            
        matches = re.findall(r'(\d+\.?\d*)\s+MHz', content)
        
        if matches:
            return min(float(m) for m in matches)
        
        return 0.0