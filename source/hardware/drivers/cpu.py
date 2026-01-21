from hardware.drivers.base_driver import DeviceDriver
from hardware.quartus.command import QuartusCommandError
from hardware.quartus.compiler import QuartusCompiler
from hardware.quartus.timing import TimingAnalyzer
from hardware.quartus.simulator import QuartusSimulator
from pathlib import Path
import pandas as pd
import logging


logger = logging.getLogger(__name__)

class CPUDriver(DeviceDriver):
    def __init__(self, project_path: Path, simulation_path: Path, name: str, compiler: QuartusCompiler, timing_analyzer: TimingAnalyzer, simulator: QuartusSimulator):
        super().__init__(project_path, simulation_path, name, compiler)
        self.compiled = False
        self.timing_analyzer = timing_analyzer
        self.fmax = None
        self.simulator = simulator
        self.current_params = {}

    def prepare_hardware(self, params: dict) -> None:
        self.current_params = params
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
        logger.info(f"Building project at {self.project_path}")
        #self.compiler.compile_all(project_path=self.project_path)
        #self.fmax = self.timing_analyzer.get_fmax(project_path=self.project_path)
        logger.info(f"Device {self.name} fmax: {self.fmax} MHz")

    def run_simulation(self, output_dir: Path) -> pd.DataFrame:
        logger.info(f"Running simulation for {self.name} in {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)
        sim_args = {
            "ID": output_dir.name,         
            "DIR": output_dir.as_posix(),  
            #"G_SIZE": self.current_params.get("problem_size", 100), 
        }
        sim_work_dir = self.simulation_path / "simulation_files"
        script_path = sim_work_dir / "scripts" / "run.tcl"
        compiled_work_dir = sim_work_dir / "compiled_work"
        sim_work_dir.mkdir(parents=True, exist_ok=True)
        compiled_work_dir.mkdir(parents=True, exist_ok=True)
        script_path.parent.mkdir(parents=True, exist_ok=True)
        if not script_path.exists():
            logger.info(f"Generating run script at {script_path}")
            with open(script_path, "w") as f:
                f.write("onerror { quit -code 1 -f }\n") 
                f.write("onbreak { quit -code 1 -f }\n")
                f.write("run -all\n")
                f.write("quit -f")
        try:
            self.simulator.compile(project_path=self.project_path, simulation_path=self.simulation_path)
        except Exception as e:
            logger.error(f"Failed to compile simulation: {e}")
            return pd.DataFrame()    
        try:
            self.simulator.simulate(
                work_dir=sim_work_dir,
                tb_name="work.tb_cpu",
                script_path=script_path,
                generics=sim_args,
                compiled_lib_path=compiled_work_dir
            )
        except Exception as e:
            logger.error(f"Simulation execution failed: {e}")
            return pd.DataFrame()
        
        results_file = output_dir / "output.csv" 
        return self._parse_results(results_file)
    
    def _parse_results(self, results_path: Path) -> pd.DataFrame:
        if not results_path.exists():
            logger.error(f"Simulation output not found at {results_path}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(results_path)
            if df.empty:
                return df

            df["device"] = self.name
            for param_name, param_value in self.current_params.items():
                df[param_name] = param_value

            if self.fmax:
                df["fmax_mhz"] = self.fmax
                
                if "cycles" in df.columns:
                    df["exec_time_s"] = df["cycles"] / (self.fmax * 1_000_000)
                    df["exec_time_ns"] = df["cycles"] / (self.fmax)
            else:
                df["fmax_mhz"] = float("nan")
                df["exec_time_s"] = float("nan")
                df["exec_time_ns"] = float("nan")

            return df

        except Exception as e:
            logger.error(f"Error parsing dataframe: {e}")
            return pd.DataFrame()