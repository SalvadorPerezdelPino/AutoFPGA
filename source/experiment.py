from knapsack import *
import subprocess
import pandas as pd
import re
import json
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

class ExperimentManager:
    def __init__(self, cpu: str, config_path: str, verbose: bool = False):
        self.cpu = cpu
        self.verbose = verbose

        try:
            with open(config_path, "r", encoding="utf-8") as file:
                self.config = json.load(file)
        except FileNotFoundError:
            print("El archivo de configuración no se ha encontrado.")
        except IOError:
            print("Error al intentar leer el archivo.")

        if cpu not in self.config:
            raise ValueError(f"CPU {cpu} no encontrada en {config_path}")
        
        self.paths = self.config[cpu].get("paths", {})
        self.project_path = self.paths.get("quartus_project", {})
        self.items_cfg = self.config[cpu].get("items", {})
        self.capacity_cfg = self.config[cpu].get("capacity", {})
        self.instances = int(self.config[cpu].get("instances", -1))

        self.seed = int(self.config.get("seed", -1))
        if self.seed == -1:
            self.seed = int(datetime.now().microsecond)

        random.seed(self.seed)
        self.experiments_root = f"../data/{cpu}/experiments/"

    def generate_problem_files(self, iteration: int, capacity: int, items: int) -> None:
        ks = Knapsack()
        ks.generate_problem(capacity=capacity, items=items)
        ks.write_problem_file(os.path.join(self.paths.get("inputs"), f"input{iteration}.mem"))
        ks.write_solution_file(os.path.join(self.paths.get("solutions"), f"solution{iteration}.mem"))

    def update_fmax_script(self, script_path: str, fmax_path: str) -> None:
        try:
            with open(script_path, "w+") as file:
                file.write(f"project_open {self.project_path}\n")
                file.write("create_timing_netlist\n")
                file.write("read_sdc\n")
                file.write("update_timing_netlist\n")
                file.write(f"report_clock_fmax_summary -file {fmax_path}\n")
                file.write("project_close\n")
        except FileNotFoundError:
            print("No se encontró el fichero")
        except IOError:
            print("Error al abrir el fichero")

    def get_max_frequency(self, fmax_path: str, script_path: str) -> float:
        self.update_fmax_script(fmax_path=fmax_path, script_path=script_path)
        print("Obteniendo frecuencia máxima")

        if self.verbose:
            subprocess.run(f"quartus_sta -t ../data/{self.cpu}/simulation/scripts/get_fmax.tcl")
        else:
            subprocess.run(f"quartus_sta -t ../data/{self.cpu}/simulation/scripts/get_fmax.tcl", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        with open(fmax_path, "r") as file:
            text = file.read()
        
        frequencies = re.findall(r'(\d+\.\d+)\s*MHz', text)
        if not frequencies:
            raise ValueError("No se ha encontrado frecuencia máxima")
        
        try:
            fmax = float(frequencies[1])
        except Exception as e:
            print(f"Error: {e}")

        print(f"Frecuencia máxima: {fmax} MHz")
        return fmax
    
    def build_simulation(self):
        if self.verbose:
            subprocess.run(f"vsim -c -do ../scripts/compile.tcl", cwd=f"../data/{self.cpu}/simulation/compiled/")
        else:
            subprocess.run(f"vsim -c -do ../scripts/compile.tcl", cwd=f"../data/{self.cpu}/simulation/compiled/", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def run_simulation(self):
        print("Simulando")
        if self.verbose:
            subprocess.run(["vsim", "-c", "work.tb_cpu", "-do", "run -all; quit -f"], cwd=f"../data/{self.cpu}/simulation/compiled/")
        else:
            subprocess.run(["vsim", "-c", "work.tb_cpu",  "-do", "run -all; quit -f"], cwd=f"../data/{self.cpu}/simulation/compiled/", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Simulación realizada")

    def prepare_average_csv(self, experiment_file: str, dataframe_row: list, columns_to_average):
        avg_dataframe = pd.DataFrame(dataframe_row, columns=["capacity", "items", "fmax", "execution_time"] + columns_to_average)
        avg_dataframe.to_csv(experiment_file, index=False, sep=";", decimal=",")
    
    def get_sweep_dict(self, sweep_type: str, fixed: int, start: int, end: int, step: int) -> dict:
        if sweep_type == "items":
            info = {
                "timestamp": datetime.now().isoformat(),
                "cpu": self.cpu,
                "type": f"sweep_items",
                "capacity": fixed,
                "items": {
                    "min": start,
                    "max": end,
                    "step": step
                },
                "seed": self.seed
            }
        elif sweep_type == "capacity":
            info = {
                "timestamp": datetime.now().isoformat(),
                "cpu": self.cpu,
                "type": f"sweep_capacity",
                "capacity": {
                    "min": start,
                    "max": end,
                    "step": step
                },
                "items": fixed,
                "seed": self.seed
            }

        return info

    def generate_experiment_json(self, info: dict, info_path: str):
        with open(info_path, "w+") as file:
            file.write(json.dumps(info, indent=4))

    def sweep(self, variable_to_sweep: str):
        csv_path = self.paths.get("csv")

        if variable_to_sweep == "items":
            fixed = self.capacity_cfg.get("constant", -1)
            start = self.items_cfg.get("min", -1)
            end = self.items_cfg.get("max", -1)
            step = self.items_cfg.get("step", -1)
            experiment_directory = f"../data/{self.cpu}/experiments/sweep_{variable_to_sweep}/c{fixed}_n{start}_{end}/"
        elif variable_to_sweep == "capacity":
            fixed = self.items_cfg.get("constant", -1)
            start = self.capacity_cfg.get("min", -1)
            end = self.capacity_cfg.get("max", -1)
            step = self.capacity_cfg.get("step", -1)
            experiment_directory = f"../data/{self.cpu}/experiments/sweep_{variable_to_sweep}/c{start}_{end}_n{fixed}/"
        
        info = self.get_sweep_dict(variable_to_sweep, fixed, start, end, step)

        if not os.path.exists(experiment_directory):
                os.makedirs(experiment_directory)

        self.generate_experiment_json(info=info, info_path=experiment_directory + "info.json")

        # Prepare max frequency for dataframe
        fmax_path = experiment_directory + f"fmax.dat"
        fmax_path = os.path.abspath(fmax_path)
        fmax_path = fmax_path.replace('\\', '/')
        script_path = f"../data/{self.cpu}/simulation/scripts/get_fmax.tcl"
        fmax = self.get_max_frequency(fmax_path=fmax_path, script_path=script_path)
        
        self.build_simulation()
        print(f"[{self.cpu.upper()}]")
        dataframe_row = []

        if variable_to_sweep == "items":
            for items in range(start, end + 1, step):
                print(f"[C:{fixed} N:{items}]")

                for iteration in range(self.instances):
                    self.generate_problem_files(iteration=iteration, capacity=fixed, items=items)
                
                self.run_simulation()

                current_simulation_file = experiment_directory + f"c{fixed}_n{items}.csv"
                os.replace(csv_path, current_simulation_file)
                dataframe = pd.read_csv(current_simulation_file, sep=';', decimal=',')
                columns_to_average = ["cycles", "instructions", "cpi", "memory_reads", "memory_writes"]
                averages = dataframe[columns_to_average].mean().to_list()
                fmax = float(fmax) # MHz
                row = [fixed, items, fmax, (1.0/fmax) * averages[0]] + averages
                dataframe_row.append(row)

        elif variable_to_sweep == "capacity":
            for capacity in range(start, end + 1, step):
                print(f"[C:{capacity} N:{fixed}]")

                for iteration in range(self.instances):
                    self.generate_problem_files(iteration=iteration, capacity=capacity, items=fixed)
                
                self.run_simulation()

                current_simulation_file = experiment_directory + f"c{capacity}_n{fixed}.csv"
                os.replace(csv_path, current_simulation_file)
                dataframe = pd.read_csv(current_simulation_file, sep=';', decimal=',')
                columns_to_average = ["cycles", "instructions", "cpi", "memory_reads", "memory_writes"]
                averages = dataframe[columns_to_average].mean().to_list()
                fmax = float(fmax) # MHz
                row = [capacity, fixed, fmax, (1.0/fmax) * averages[0]] + averages
                dataframe_row.append(row)
        
        result_file = experiment_directory + f"average.csv"
        self.prepare_average_csv(result_file, dataframe_row, columns_to_average)

def plot_gaussian_distribution(csv_path: str, column="cycles", bins=25):
    # Load data
    df = pd.read_csv(csv_path, sep=';', decimal=',')
    data = df[column].dropna()

    # Get mean and standard deviation
    mean = data.mean()
    std = data.std()
    #print(f"Media de {column}: {mean:.2f}")
    #print(f"Desviación típica de {column}: {std:.2f}")

    # Create range for theorical curve
    x = np.linspace(data.min(), data.max(), 200)
    pdf = norm.pdf(x, mean, std)

    # Figure
    plt.figure(figsize=(8, 5))
    plt.style.use("seaborn-v0_8-whitegrid")

    # Normalized histogram
    plt.hist(data, bins=bins, density=True, alpha=0.6, color="#4C72B0", edgecolor="white", label="Datos reales")

    # Gaussian curve
    #plt.plot(x, pdf, "r--", linewidth=2, label="Ajuste gaussiano")

    # Mean, std and CV textbox
    plt.axvline(mean, color="black", linestyle="--", linewidth=1)
    plt.text(mean, max(pdf)*0.9, f"Media = {mean:.2f}\nσ = {std:.2f}\nCV = {std/mean:.3f}", 
            ha="center", va="top", fontsize=10, bbox=dict(facecolor="white", alpha=0.7))

    # Title and labels
    plt.title(f"Distribución de {column}", fontsize=14, weight="bold")
    plt.xlabel(column, fontsize=12)
    plt.ylabel("Densidad de probabilidad", fontsize=12)
    plt.legend()
    plt.tight_layout()
    plt.show()

def box_data(csv_path: str, column="cycles"):
    df = pd.read_csv(csv_path, sep=';', decimal=',')
    data = df[column].dropna()

    plt.boxplot(data, vert=True, patch_artist=True, boxprops=dict(facecolor="#4C72B0", alpha=0.5))
    plt.title(f"Distribución de {column}", fontsize=14, weight="bold")
    plt.ylabel(column)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

def plot_box(cpu="monocycle"):
    plt.subplot(2,2,1)
    box_data(f"../data/{cpu}/outputs/{cpu}_c20_n10.csv")
    plt.subplot(2,2,2)
    box_data(f"../data/{cpu}/outputs/{cpu}_c20_n15.csv")
    plt.subplot(2,2,3)
    box_data(f"../data/{cpu}/outputs/{cpu}_c20_n20.csv")
    plt.subplot(2,2,4)
    box_data(f"../data/{cpu}/outputs/{cpu}_c20_n25.csv")
    
    plt.show()
    

def compare_cpus(cpus: list, xlabel:str, ylabel:str):
    for cpu in cpus:
        df = pd.read_csv(f"../data/{cpu}/average.csv", sep=";", decimal=",")
        plt.plot(df[xlabel], df[ylabel], label=cpu)
    plt.legend()
    plt.grid(True)
    #plt.tight_layout()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

def plot_comparison():
    plt.subplot(2,2,1)
    compare_cpus(["monocycle", "multicycle", "pipeline"], "items", "cycles")
    plt.subplot(2,2,2)
    compare_cpus(["monocycle", "multicycle", "pipeline"], "items", "execution_time")
    plt.subplot(2,2,3)
    compare_cpus(["monocycle", "multicycle", "pipeline"], "items", "memory_reads")
    plt.subplot(2,2,4)
    compare_cpus(["monocycle", "multicycle", "pipeline"], "items", "memory_writes")    
    plt.show()