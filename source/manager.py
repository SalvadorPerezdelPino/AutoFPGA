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
from itertools import product
import matplotlib.pyplot as plt

PROBLEM_CLASSES = {
    "knapsack": KnapsackProblem,
    "alignment": AlignmentProblem
}

PROBLEM_SIZE_MAP = {
    "alignment": ("sequence_1_size", "sequence_2_size"),
    "knapsack": ("capacity", "items")
}
class ExperimentManager:
    def __init__(self, config_file: str, verbose):
        with open(config_file, "r") as file:
            self.config = json.load(file)
        self.instances: int = self.config["experiments"]["instances"]
        self.seed: int = self.config["experiments"]["seed"]
        if self.seed is None:
            self.seed = int(datetime.now().timestamp())
        self.verbose: bool = verbose
        self.current_experiment_dir: Path = None
        self.compiler = QuartusCompiler(config_file=config_file, verbose=self.verbose)

    def compile(self):
        self.compiler.compile_all()
        
    def get_problem_class(self, problem_name):
        if problem_name not in PROBLEM_CLASSES:
            print(f"Unknown problem: {problem_name}")
            exit(1)
        return PROBLEM_CLASSES[problem_name]

    def get_single_subdir(self, params):
        var_keys = [k for k in params if k not in ("devices", "problem_name", "output_dir", "sweep", "seed", "gap_penalty", "mismatch_penalty", "alphabet", "match_score", "instances")]
        var_part = "_".join(f"{k}{params[k]}" for k in var_keys)

        date_part = datetime.now().strftime("%Y%m%d-%H%M%S")
        subdir = f"{var_part}_{date_part}"
        #print(f"Subdir: {subdir}")
        return subdir
    
    def update_fmax_script(self, device) -> None:
        project_path = Path(self.config["devices"][device]["quartus_project_path"])
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
        #print(wlf_path)
        if self.verbose:
            result = subprocess.run(["vsim", "-voptargs=+acc=npr", "-L", "altera_mf_ver", "-c", "work.tb_cpu", f"+ID={id}", f"+DIR={dir}", "-wlf", wlf_path, "-do", "../scripts/run.tcl"], cwd=f"../data/{device}/simulation/compiled/")
        else:
            result = subprocess.run(["vsim", "-voptargs=+acc=npr", "-L", "altera_mf_ver", "-c", "work.tb_cpu", f"+ID={id}", f"+DIR={dir}", "-wlf", wlf_path, "-do", "../scripts/run.tcl"], cwd=f"../data/{device}/simulation/compiled/", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


    def generate_problem_combinations(self, base_params, sweep_config, problem_class):
        if not sweep_config:
            return [base_params]

        sweep_keys = [k for k in sweep_config if k in getattr(problem_class, "SWEEP_PARAMS", [])]
        if not sweep_keys:
            return [base_params]

        sweep_values = []
        for key in sweep_keys:
            cfg = sweep_config[key]
            start = cfg.get("start", base_params.get(key, 0))
            stop = cfg.get("stop", base_params.get(key, start))
            step = cfg.get("step", 1)
            values = list(range(start, stop + 1, step))
            sweep_values.append(values)

        combinations = []
        for combo in product(*sweep_values):
            new_params = base_params.copy()
            for k, v in zip(sweep_keys, combo):
                new_params[k] = v
            combinations.append(new_params)

        return combinations

    def compute_problem_size(self, row):
        size_a, size_b = PROBLEM_SIZE_MAP[row["problem"]]
        return row[size_a] * row[size_b]

    def run_experiment(self):
        graph = True
        exp_to_graph = []
        for problem_name in self.config["experiments"]["problems_to_experiment"]:
            ProblemClass = self.get_problem_class(problem_name=problem_name)
            base_problem_params = self.config["problems"][problem_name]

            sweep_config = self.config["experiments"].get("sweep", {})
            param_combinations = self.generate_problem_combinations(base_problem_params, sweep_config, ProblemClass)

            for params in param_combinations:
                problem = ProblemClass(params)
                subdir = self.get_single_subdir(params)

                for device in self.config["experiments"]["devices_to_experiment"]:
                    random.seed(self.seed)
                    print(f"[{device.upper()}]")
                    self.current_experiment_dir = Path(self.config["experiments"]["data_dir"]) / device / "experiments" / problem_name / self.config["experiments"]["type"] / subdir
                    fmax = self.get_max_frequency(device)
                    self.build_simulation(device)
                    
                    for instance in range(1, self.instances+1):
                        instance_dir = self.current_experiment_dir / f"instance_{instance}"
                        problem.update_id(instance)
                        problem.run(instance_dir)
                        print(f"Simulating instance {instance} of {self.instances}")
                        self.run_simulation(device, instance, instance_dir.absolute().as_posix().replace('\\', '/'))
                        try:
                            with open(instance_dir / "error.log") as file:
                                message = file.readline()
                                if "CORRECT" not in message:
                                    print(f"Error: {message}")
                                    return
                        except:
                            print("Error while simulating, probably file not created in testbench")
                            return

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
                    summary_df.drop(columns=["test_id"], axis=1, inplace=True)
                    for key, value in params.items():
                        summary_df[key] = value
                    summary_df["device"] = device
                    summary_df["fmax"] = fmax
                    summary_df["exec_time"] = (summary_df["cycles"] / summary_df["fmax"]).round(4)
                    summary_df["problem"] = problem_name
                    summary_df["problem_size"] = summary_df.apply(self.compute_problem_size, axis=1)
                    exp_to_graph.append(summary_df)

                    #json_data = {
                    #    "datetime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    #    "seed": self.seed,
                    #    "instances": self.instances,
                    #    "problem": problem.to_dict()
                    #}
                    #with open(self.current_experiment_dir / "info.json", "w+") as file:
                    #    file.write(json.dumps(json_data, indent=4))
        print("Experiment has finished successfully!")

        if graph == True:
            general_df = pd.concat(exp_to_graph, ignore_index=True)
            print(general_df)
            general_df.to_csv(self.current_experiment_dir / "general.csv", index=False, sep=';', decimal=',')
            plt.figure()

            for device in general_df["device"].unique():
                df_dev = general_df[general_df["device"] == device]

                mean_df = (
                    df_dev
                    .groupby("problem_size")["exec_time"]
                    .mean()
                    .reset_index()
                    .sort_values("problem_size")
                )

                plt.plot(
                    mean_df["problem_size"],
                    mean_df["exec_time"],
                    marker="o",
                    label=device
                )

            plt.xlabel("Problem size")
            plt.ylabel("Mean execution time (s)")
            plt.title("Execution time growth")
            plt.legend()
            plt.grid(True)

            plt.show()
            plt.savefig(self.current_experiment_dir / "figure.png")
            plt.close()

            plt.figure()

            for device in general_df["device"].unique():
                df_dev = general_df[general_df["device"] == device]

                mean_df = (
                    df_dev
                    .groupby("problem_size")["cycles"]
                    .mean()
                    .reset_index()
                    .sort_values("problem_size")
                )

                plt.plot(
                    mean_df["problem_size"],
                    mean_df["cycles"],
                    marker="o",
                    label=device
                )

            plt.xlabel("Problem size")
            plt.ylabel("Mean cycles")
            plt.title("Cycles growth")
            plt.legend()
            plt.grid(True)

            plt.show()
            plt.savefig(self.current_experiment_dir / "figure2.png")
            plt.close()

            plt.figure()

            devices = general_df["device"].unique()
            data = [
                general_df[general_df["device"] == dev]["exec_time"]
                for dev in devices
            ]

            plt.boxplot(data, labels=devices)
            plt.ylabel("Execution time (s)")
            plt.title("Execution time distribution per device")

            plt.show()
            plt.savefig(self.current_experiment_dir / "figure3.png")
            plt.close()






