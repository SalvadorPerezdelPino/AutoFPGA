from problems.knapsack import KnapsackProblem
from problems.alignment import AlignmentProblem
import json
from pathlib import Path
from datetime import datetime
import subprocess
import re
import pandas as pd
from compiler import QuartusCompiler
import random

PROBLEM_CLASSES = {
    "knapsack": KnapsackProblem,
    "alignment": AlignmentProblem
}

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

class ExperimentManager:
    def __init__(self, config_file: str, verbose):
        with open(config_file, "r") as file:
            self.config = json.load(file)
        self.problem_name: str = self.config.get("problem_name")
        self.instances: int = self.config.get("instances", 1)
        self.seed: int = self.config.get("seed", None)
        if self.seed is None:
            self.seed = int(datetime.now().timestamp())
        self.verbose: bool = verbose
        self.current_experiment_dir: Path = None
        self.compiler = QuartusCompiler(config_file=config_file, verbose=self.verbose)

    def compile(self):
        self.compiler.compile_all()
        
    def get_problem_class(self):
        if self.problem_name not in PROBLEM_CLASSES:
            print(f"Unknown problem: {self.problem_name}")
            exit(1)
        return PROBLEM_CLASSES[self.problem_name]

    def get_single_subdir(self, params):
        var_keys = [k for k in params if k not in ("devices", "problem_name", "output_dir", "sweep", "seed", "gap_penalty", "mismatch_penalty", "alphabet", "match_score", "instances")]
        var_part = "_".join(f"{k}{params[k]}" for k in var_keys)

        date_part = datetime.now().strftime("%Y%m%d-%H%M%S")
        subdir = f"{var_part}_{date_part}"
        print(f"Subdir: {subdir}")
        return subdir
    
    def update_fmax_script(self, device) -> None:
        project_dir = Path(f"../../FPGA/DE10/{device}/synthesis").absolute()
        qpf_files = list(project_dir.glob("*.qpf"))
        project_path = qpf_files[0]
        project_path = project_path.as_posix().replace('\\', '/')
        fmax_path = Path(self.current_experiment_dir) / "fmax.txt"
        fmax_path = fmax_path.absolute().as_posix().replace('\\', '/')
        script_path = Path(f"../data/{device}/simulation/scripts/get_fmax.tcl").absolute()

        with open(script_path, "w+") as file:
            file.write(f"project_open {project_path}\n")
            file.write("create_timing_netlist\n")
            file.write("read_sdc\n")
            file.write("update_timing_netlist\n")
            file.write(f"report_clock_fmax_summary -file {fmax_path}\n")
            file.write("project_close\n")

    def get_max_frequency(self, device) -> float:
        self.update_fmax_script(device)
        print("Getting maximum frequency...")
        fmax_path = Path(self.current_experiment_dir) / "fmax.txt"
        if self.verbose:
            result = subprocess.run(f"quartus_sta -t ../data/{device}/simulation/scripts/get_fmax.tcl")
        else:
            result = subprocess.run(f"quartus_sta -t ../data/{device}/simulation/scripts/get_fmax.tcl", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if result.returncode != 0:
            print("Error")
            exit(1)

        with open(fmax_path, "r") as file:
            text = file.read()
        
        frequencies = re.findall(r'(\d+\.\d+)\s*MHz', text)
        if not frequencies:
            raise ValueError("Max frequency not found")
        
        try:
            fmax = float(frequencies[1])
        except Exception as e:
            print(f"Error: {e}")

        print(f"Max frequency: {fmax} MHz")
        return fmax
    
    def build_simulation(self, device):
        #TODO: Improve path with Path()
        print("Compiling simulation")
        if self.verbose:
            subprocess.run(f"vsim -c -do ../scripts/compile.tcl", cwd=f"../data/{device}/simulation/compiled/")
        else:
            subprocess.run(f"vsim -c -do ../scripts/compile.tcl", cwd=f"../data/{device}/simulation/compiled/", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Simulation has been compiled")
        print("")
    
    def run_simulation(self, device, id, dir):
        #TODO: Improve path with Path()
        wlf_path = dir + "/sim.wlf"
        print(wlf_path)
        if self.verbose:
            result = subprocess.run(["vsim", "-voptargs=+acc=npr", "-L", "altera_mf_ver", "-c", "work.tb_cpu", f"+ID={id}", f"+DIR={dir}", "-wlf", wlf_path, "-do", "../scripts/run.tcl"], cwd=f"../data/{device}/simulation/compiled/")
        else:
            result = subprocess.run(["vsim", "-voptargs=+acc=npr", "-L", "altera_mf_ver", "-c", "work.tb_cpu", f"+ID={id}", f"+DIR={dir}", "-wlf", wlf_path, "-do", "../scripts/run.tcl"], cwd=f"../data/{device}/simulation/compiled/", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if result.returncode != 0:
            print("Error while simulating.")
        else:
            print("Simulation was successful!")
        print("") # Line break

    def run_single(self, params: dict):
        ProblemClass = self.get_problem_class()
        problem = ProblemClass(params)
        subdir = self.get_single_subdir(params)
        devices = params.get("devices", {})

        for device in devices:
            random.seed(self.seed)
            print(f"[{device.upper()}]")
            self.current_experiment_dir = DATA_DIR / device / "experiments" / self.problem_name / "single" / subdir
            self.get_max_frequency(device)
            self.build_simulation(device)
            
            for instance in range(1, self.instances+1):
                instance_dir = self.current_experiment_dir / f"instance_{instance}"
                problem.update_id(instance)
                problem.run(instance_dir)
                print(f"Simulating instance {instance} of {self.instances}")
                self.run_simulation(device, instance, instance_dir.absolute().as_posix().replace('\\', '/'))

            # Create summary.csv
            first_instance_dir = self.current_experiment_dir / "instance_1"
            first_csv = list(first_instance_dir.absolute().glob("*.csv"))
            summary_df = pd.read_csv(first_csv[0], sep=';', decimal=',')
            summary_csv_path = self.current_experiment_dir / "summary.csv"
            summary_csv_path = summary_csv_path.absolute()

            if self.instances > 1:
                for instance in range(2, self.instances+1):
                    instance_dir = self.current_experiment_dir / f"instance_{instance}"
                    instance_csv = list(instance_dir.absolute().glob("*.csv"))
                    instance_df = pd.read_csv(instance_csv[0], header=0, sep=';', decimal=',')
                    summary_df = pd.concat([summary_df, instance_df], ignore_index=True)

            summary_df.to_csv(summary_csv_path, index=False, sep=';', decimal=',')
            avg_csv_path = self.current_experiment_dir / "average.csv"
            # Create average.csv
            summary_df.drop(columns=["test_id", "expected_solution", "hw_solution"], axis=1, inplace=True)
            summary_df_mean = summary_df.mean()
            avg_df = pd.DataFrame([summary_df_mean])
            avg_df = avg_df.round(4)
            avg_df.to_csv(avg_csv_path, index=False, sep=';', decimal=',')

            json_data = {
                "datetime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "seed": self.seed,
                "instances": self.instances,
                "problem": problem.to_dict()
            }

            with open(self.current_experiment_dir / "info.json", "w+") as file:
                file.write(json.dumps(json_data, indent=4))

    def sweep(self, params: dict):
        pass
