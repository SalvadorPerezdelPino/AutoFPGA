from hardware.quartus.command import QuartusCommand, QuartusCommandError
from pathlib import Path
import logging

logger = logging.getLogger('Quartus Simulator')

class QuartusSimulator:
    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose
        self.base_cmd = ["vsim", "-c", "-voptargs=+acc=npr", "-L", "altera_mf_ver"]

    def compile(self, project_path: Path, simulation_path: Path) -> None:
        sim_dir = simulation_path / "simulation_files"
        work_dir = sim_dir / "compiled_work"

        sim_dir.mkdir(parents=True, exist_ok=True)

        hdl_dir = project_path / "hdl"
        test_dir = project_path / "test"
        
        script_path = sim_dir / "scripts" / "compile_sim.tcl"

        script_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._create_compile_script(script_path, work_dir, hdl_dir, test_dir)
        cmd = QuartusCommand(self.base_cmd + ["-do", script_path.as_posix()])
        
        try:
            logger.info(f"Compiling simulation files for {project_path.name}...")
            cmd.run(cwd=sim_dir, verbose=self.verbose, auto_append_project=False)
        except QuartusCommandError:
            logger.error(f"Simulation compilation failed for {project_path.name}")
            raise


    def simulate(self, work_dir: Path, tb_name: str, script_path: Path, generics: dict = None, compiled_lib_path: Path = None) -> None:
        if compiled_lib_path:
            logger.info(f"Mapping 'work' library to {compiled_lib_path}")
            
            vmap_cmd = QuartusCommand(["vmap", "work", compiled_lib_path.as_posix()])
            
            try:
                vmap_cmd.run(
                    cwd=work_dir, 
                    verbose=self.verbose, 
                    auto_append_project=False
                )
            except QuartusCommandError:
                logger.error("Failed to map work library. Simulation might fail.")
                raise

        cmd_args = self.base_cmd.copy()
        cmd_args.append(tb_name)
        cmd_args.extend(["-do", f"do {script_path.as_posix()}"])
        if generics:
            for key, value in generics.items():
                cmd_args.append(f"+{key}={value}")

        command = QuartusCommand(cmd_args)
        
        try:
            command.run(
                cwd=work_dir, 
                verbose=self.verbose, 
                auto_append_project=False
            )
        except QuartusCommandError:
            logger.error(f"Simulation failed for {tb_name}")
            raise

    def _create_compile_script(self, script_path: Path, work_path: Path, hdl_path: Path, test_path: Path):
        work_str = work_path.as_posix()
        lines = [
            "onerror { quit -code 1 -f }", 
            f'if {{![file exists "{work_str}"]}} {{',
            f'    vlib "{work_str}"',
            f'    vmap work "{work_str}"',
            f'}} else {{',
            f'    vmap work "{work_str}"',
            f'}}',
            ""
        ]

        if list(hdl_path.glob("*.v")):
            lines.append(f'puts "Compiling Verilog files from {hdl_path.name}..."')
            lines.append(f'vlog -work work "{hdl_path.as_posix()}/*.v"')
        
        if list(hdl_path.glob("*.sv")):
            lines.append(f'puts "Compiling SystemVerilog files from {hdl_path.name}..."')
            lines.append(f'vlog -work work "{hdl_path.as_posix()}/*.sv"')

        if list(test_path.glob("*.v")):
            lines.append(f'puts "Compiling Testbench Verilog..."')
            lines.append(f'vlog -work work "{test_path.as_posix()}/*.v"')
            
        if list(test_path.glob("*.sv")):
            lines.append(f'puts "Compiling Testbench SystemVerilog..."')
            lines.append(f'vlog -work work "{test_path.as_posix()}/*.sv"')

        lines.append("quit -f")

        with open(script_path, "w") as f:
            f.write("\n".join(lines))