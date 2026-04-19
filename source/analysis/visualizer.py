import pandas as pd
import logging
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

logger = logging.getLogger('Visualizer')

class Visualizer:
    def __init__(self, df: pd.DataFrame = None):
        if df is not None:
            self.df = df.copy()
            self._calculate_axis()

        sns.set_theme(style="whitegrid")
        plt.rcParams.update({'figure.figsize': (10, 6)})
        

    def set_df_from_csv(self, csv: str):
        path = Path(csv)
        df = pd.read_csv(path, decimal=',', sep=';')
        self.df = df.copy()
        self._calculate_axis()

    def _calculate_axis(self):
        if 'sequence_1_size' in self.df.columns:
            self.df['plot_x'] = self.df['sequence_1_size']
            self.x_label = "Sequence Length (N)" 
            self.problem_type = "alignment"
            
        elif 'items' in self.df.columns:
            self.df['plot_x'] = self.df['items']
            self.x_label = "Number of Items"
            self.problem_type = "knapsack"
        
        else:
            self.df['plot_x'] = self.df.index
            self.x_label = "Test Instance ID"
            self.problem_type = "unknown"

    def plot_metric(self, y_col: str, output_dir: Path, title: str = None):
        if self.df.empty:
            logger.warning("No data to plot.")
            return

        data = self.df.dropna(subset=['plot_x', y_col])

        if data.empty:
            logger.warning(f"No valid data for plotting {y_col}")
            return

        plt.figure()
        
        ax = sns.lineplot(
            data=data, 
            x='plot_x', 
            y=y_col, 
            hue="device", 
            style="device", 
            markers=True, 
            dashes=False,
            linewidth=2.5 
        )

        grouped = data.groupby(['device', 'plot_x'])[y_col].mean().reset_index()

        for _, row in grouped.iterrows():
            ax.annotate(
                f"{row[y_col]:g}",
                xy=(row['plot_x'], row[y_col]),
                xytext=(0, 7),
                textcoords='offset points',
                ha='center',
                va='bottom',
                fontsize=9,
                fontweight='semibold',
                color='black'
            )

        final_title = title or f"{y_col} vs {self.x_label}"
        plt.title(final_title)
        plt.xlabel(self.x_label)
        plt.ylabel(y_col.replace("_", " ").title())
        
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{self.problem_type}_{y_col}_vs_length.png"
        save_path = output_dir / filename
        
        plt.savefig(save_path, dpi=300)
        plt.close()
        logger.info(f"Plot saved: {save_path}")

    def plot_performance_summary(self, output_dir: Path):
        self.plot_metric(
            y_col="cycles",
            output_dir=output_dir,
            title="Scalability: Cycles vs Sequence Length"
        )

        if "exec_time_ns" in self.df.columns:
            self.plot_metric(
                y_col="exec_time_ns",
                output_dir=output_dir,
                title="Performance: Execution Time vs Sequence Length"
            )