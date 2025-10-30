import subprocess

class QuartusCompiler:
    def __init__(self, project_path: str, cpu: str, verbose: bool = False) -> None:
        self.project_path = project_path
        self.cpu = cpu
        self.verbose = verbose

    def synthetize(self) -> None:
        if self.verbose:
            result = subprocess.run(f"quartus_map {self.project_path}")
        else:
            result = subprocess.run(f"quartus_map {self.project_path}", 
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            print("Synthesis failed.")
            exit(result.returncode)
        else:
            print("Synthesis was successful!")


    def fit(self) -> None:
        if self.verbose:
            result = subprocess.run(f"quartus_fit {self.project_path}")
        else:
            result = subprocess.run(f"quartus_fit {self.project_path}", 
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            print("Fitting failed.")
            exit(result.returncode)
        else:
            print("Fitting was successful!")

    def assemble(self) -> None:
        if self.verbose:
            result = subprocess.run(f"quartus_asm {self.project_path}")
        else:
            result = subprocess.run(f"quartus_asm {self.project_path}", 
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            print("Assembling failed.")
            exit(result.returncode)
        else:
            print("Assembling was successful!")

    def timing(self) -> None:
        if self.verbose:
            result = subprocess.run(f"quartus_sta {self.project_path}")
        else:
            result = subprocess.run(f"quartus_sta {self.project_path}", 
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            print("Timing failed.")
            exit(result.returncode)
        else:
            print("Timing was successful!")

    def netlist(self) -> None:
        if self.verbose:
            result = subprocess.run(f"quartus_eda {self.project_path}")
        else:
            result = subprocess.run(f"quartus_eda {self.project_path}", 
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            print("Netlist creation failed.")
            exit(result.returncode)
        else:
            print("Netlist creation was successful!")

    def compile_all(self) -> None:
        if self.verbose:
            result = subprocess.run(f"quartus_sh --flow compile {self.project_path}")
        else:
            result = subprocess.run(f"quartus_sh --flow compile {self.project_path}", 
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            print("Compilation failed at some point.")
            exit(result.returncode)
        else:
            print("Compilation was successful!")
