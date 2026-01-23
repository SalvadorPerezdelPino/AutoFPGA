import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

class Visualizer:
    PROBLEM_SIZE_MAP = {
        "alignment": "sequence_1_size", 
        "knapsack": "items"             
    }

    def __init__(self, df: pd.DataFrame):
        self.df = df
        sns.set_theme(style="whitegrid")
        plt.rcParams.update({'figure.figsize': (10, 6)})

    def plot_metric(self, problem_name: str, y_col: str, output_dir: Path, title: str = None):
        if self.df.empty:
            print("No data to plot.")
            return

        x_col = self.PROBLEM_SIZE_MAP.get(problem_name, "problem_id")
        
        data = self.df.dropna(subset=[x_col, y_col])

        if data.empty:
            print(f"No valid data for plotting {y_col} vs {x_col}")
            return

        plt.figure()
        
        sns.lineplot(
            data=data, 
            x=x_col, 
            y=y_col, 
            hue="device", 
            style="device", 
            markers=True, 
            dashes=False
        )

        plt.title(title or f"{y_col} vs {x_col} ({problem_name})")
        plt.xlabel(x_col.replace("_", " ").title())
        plt.ylabel(y_col.replace("_", " ").title())
        
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{problem_name}_{y_col}_comparison.png"
        plt.savefig(output_dir / filename, dpi=300)
        plt.close()
        print(f"Plot saved: {output_dir / filename}")

    def plot_performance_summary(self, problem_name: str, output_dir: Path):
        self.plot_metric(
            problem_name=problem_name,
            y_col="cycles",
            output_dir=output_dir,
            title="Performance Comparison: Cycles"
        )

        if "exec_time_s" in self.df.columns:
            self.plot_metric(
                problem_name=problem_name,
                y_col="exec_time_ns",
                output_dir=output_dir,
                title="Performance Comparison: Execution Time"
            )
        
        if "fmax_mhz" in self.df.columns:
            self.plot_metric(
                problem_name=problem_name,
                y_col="fmax_mhz",
                output_dir=output_dir,
                title="Device Max Frequency"
            )