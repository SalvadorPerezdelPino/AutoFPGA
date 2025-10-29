import json
import subprocess

class QuartusCompiler:
    def __init__(self, project_path: str, cpu: str, verbose: bool = False) -> None:
        self.project_path = project_path
        self.cpu = cpu
        self.verbose = verbose

    def synthetize(self) -> None:
        if self.verbose:
            subprocess.run(f"quartus_map {self.project_path}")
        else:
            subprocess.run(f"quartus_map {self.project_path}", 
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def fit(self) -> None:
        if self.verbose:
            subprocess.run(f"quartus_fit {self.project_path}")
        else:
            subprocess.run(f"quartus_fit {self.project_path}", 
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def assemble(self) -> None:
        if self.verbose:
            subprocess.run(f"quartus_asm {self.project_path}")
        else:
            subprocess.run(f"quartus_asm {self.project_path}", 
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def timing(self) -> None:
        if self.verbose:
            subprocess.run(f"quartus_sta {self.project_path}")
        else:
            subprocess.run(f"quartus_sta {self.project_path}", 
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def netlist(self) -> None:
        if self.verbose:
            subprocess.run(f"quartus_eda {self.project_path}")
        else:
            subprocess.run(f"quartus_eda {self.project_path}", 
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def compile_all(self) -> None:
        if self.verbose:
            subprocess.run(f"quartus_sh --flow compile {self.project_path}")
        else:
            subprocess.run(f"quartus_sh --flow compile {self.project_path}", 
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
