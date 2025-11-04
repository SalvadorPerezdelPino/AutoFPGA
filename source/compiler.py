import subprocess
import json
from pathlib import Path

class QuartusCompiler:
    def __init__(self, config_file: str, verbose: bool = False) -> None:
        with open(config_file, "r") as file:
            self.config = json.load(file)

        self.targets = self.config.get("devices", {})
        self.verbose = verbose

    def synthetize(self) -> None:
        for device in self.targets:
            project_dir = Path(f"../../FPGA/DE10/{device}/synthesis")
            qpf_files = list(project_dir.glob("*.qpf"))
            project_path = qpf_files[0]
            if self.verbose:
                result = subprocess.run(f"quartus_map {project_path}")
            else:
                result = subprocess.run(f"quartus_map {project_path}", 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode != 0:
                print("Synthesis failed.")
                exit(result.returncode)
            else:
                print("Synthesis was successful!")


    def fit(self) -> None:
        for device in self.targets:
            project_dir = Path(f"../../FPGA/DE10/{device}/synthesis")
            qpf_files = list(project_dir.glob("*.qpf"))
            project_path = qpf_files[0]
            if self.verbose:
                result = subprocess.run(f"quartus_fit {project_path}")
            else:
                result = subprocess.run(f"quartus_fit {project_path}", 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode != 0:
                print("Fitting failed.")
                exit(result.returncode)
            else:
                print("Fitting was successful!")

    def assemble(self) -> None:
        for device in self.targets:
            project_dir = Path(f"../../FPGA/DE10/{device}/synthesis")
            qpf_files = list(project_dir.glob("*.qpf"))
            project_path = qpf_files[0]
            if self.verbose:
                result = subprocess.run(f"quartus_asm {project_path}")
            else:
                result = subprocess.run(f"quartus_asm {project_path}", 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode != 0:
                print("Assembling failed.")
                exit(result.returncode)
            else:
                print("Assembling was successful!")

    def timing(self) -> None:
        for device in self.targets:
            project_dir = Path(f"../../FPGA/DE10/{device}/synthesis")
            qpf_files = list(project_dir.glob("*.qpf"))
            project_path = qpf_files[0]
            if self.verbose:
                result = subprocess.run(f"quartus_sta {project_path}")
            else:
                result = subprocess.run(f"quartus_sta {project_path}", 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode != 0:
                print("Timing failed.")
                exit(result.returncode)
            else:
                print("Timing was successful!")

    def netlist(self) -> None:
        for device in self.targets:
            project_dir = Path(f"../../FPGA/DE10/{device}/synthesis")
            qpf_files = list(project_dir.glob("*.qpf"))
            project_path = qpf_files[0]
            if self.verbose:
                result = subprocess.run(f"quartus_eda {project_path}")
            else:
                result = subprocess.run(f"quartus_eda {project_path}", 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode != 0:
                print("Netlist creation failed.")
                exit(result.returncode)
            else:
                print("Netlist creation was successful!")

    def compile_all(self) -> None:
        for device in self.targets:
            project_dir = Path(f"../../FPGA/DE10/{device}/synthesis")
            qpf_files = list(project_dir.glob("*.qpf"))
            project_path = qpf_files[0]
            if self.verbose:
                result = subprocess.run(f"quartus_sh --flow compile {project_path}")
            else:
                result = subprocess.run(f"quartus_sh --flow compile {project_path}", 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode != 0:
                print("Compilation failed at some point.")
                exit(result.returncode)
            else:
                print("Compilation was successful!")
