import pandas as pd
import logging
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

logger = logging.getLogger('Visualizer')

METRICS = [
    ("cycles", "Cycles", "Scalability: Cycles vs Sequence Length"),
    ("exec_time_ns", "Execution Time (ns)", "Performance: Execution Time vs Sequence Length")
]

class Visualizer:
    def __init__(self, df: pd.DataFrame = None, baseline_device: str = None):
        self.baseline_device = baseline_device
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

    def plot_performance_summary(self, output_dir: Path):
        devices = self.df['device'].unique()

        for y_col, y_label, title in METRICS:
            if y_col not in self.df.columns:
                logger.warning(f"Column {y_col} not found, skipping")
                continue

            # Line
            self._plot_line(
                data=self.df,
                y_col=y_col, y_label=y_label,
                title=title,
                output_dir=output_dir / "line" / "combined",
                sharey=True
            )
            for device in devices:
                self._plot_line(
                    data=self.df[self.df['device'] == device],
                    y_col=y_col, y_label=y_label,
                    title=f"{title} — {device}",
                    output_dir=output_dir / "line" / device,
                    sharey=False
                )

            # Strip
            self._plot_strip(
                data=self.df,
                y_col=y_col, y_label=y_label,
                title=title,
                output_dir=output_dir / "strip" / "combined",
                sharey=True
            )
            for device in devices:
                self._plot_strip(
                    data=self.df[self.df['device'] == device],
                    y_col=y_col, y_label=y_label,
                    title=f"{title} — {device}",
                    output_dir=output_dir / "strip" / device,
                    sharey=False
                )

            # Box
            self._plot_box(
                data=self.df,
                y_col=y_col, y_label=y_label,
                title=title,
                output_dir=output_dir / "box" / "combined",
                sharey=True
            )
            for device in devices:
                self._plot_box(
                    data=self.df[self.df['device'] == device],
                    y_col=y_col, y_label=y_label,
                    title=f"{title} — {device}",
                    output_dir=output_dir / "box" / device,
                    sharey=False
                )

            for y_col, y_label, title in METRICS:
                if y_col not in self.df.columns:
                    continue
                self._plot_box_last_case(
                    data=self.df,
                    y_col=y_col,
                    y_label=y_label,
                    output_dir=output_dir
                )
            # Speedup
            self._plot_speedup(self.df, output_dir)

            # Bar grouped
            for y_col, y_label, title in METRICS:
                if y_col not in self.df.columns:
                    continue
                self._plot_bar_grouped(
                    data=self.df, y_col=y_col, y_label=y_label,
                    title=f"{title}",
                    output_dir=output_dir / "bar" / "combined",
                    sharey=True
                )
                for device in devices:
                    self._plot_bar_grouped(
                        data=self.df[self.df['device'] == device],
                        y_col=y_col, y_label=y_label,
                        title=f"{title} — {device}",
                        output_dir=output_dir / "bar" / device,
                        sharey=False
                    )

            # Scatter CPI
            self._plot_scatter_cpi(self.df, output_dir / "scatter_cpi" / "combined", sharey=True)
            for device in devices:
                self._plot_scatter_cpi(
                    self.df[self.df['device'] == device],
                    output_dir / "scatter_cpi" / device,
                    sharey=False
                )

            

    def _save(self, output_dir: Path, filename: str):
        output_dir.mkdir(parents=True, exist_ok=True)
        save_path = output_dir / filename
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Plot saved: {save_path}")

    def _plot_line(self, data, y_col, y_label, title, output_dir, sharey):
        data = data.dropna(subset=['plot_x', y_col])
        if data.empty:
            return

        plt.figure()
        ax = sns.lineplot(
            data=data, x='plot_x', y=y_col,
            hue='device' if sharey else None,
            style='device' if sharey else None,
            markers=True, dashes=False,
            linewidth=2.5, errorbar='sd'
        )

        grouped = data.groupby(
            ['device', 'plot_x'] if sharey else ['plot_x']
        )[y_col].mean().reset_index()

        min_gap = (data[y_col].max() - data[y_col].min()) * 0.05

        for x_val in grouped['plot_x'].unique():
            group = grouped[grouped['plot_x'] == x_val].sort_values(y_col)
            prev_y = None
            offset = 7

            for _, row in group.iterrows():
                y_val = row[y_col]

                if prev_y is not None and abs(y_val - prev_y) < min_gap:
                    offset += 8
                else:
                    offset = 7

                ax.annotate(
                    f"{y_val:g}",
                    xy=(row['plot_x'], y_val),
                    xytext=(0, offset),
                    textcoords='offset points',
                    ha='center', va='bottom',
                    fontsize=9, fontweight='semibold', color='black'
                )
                prev_y = y_val

        plt.title(title)
        plt.xlabel(self.x_label)
        plt.ylabel(y_label)
        self._save(output_dir, f"{self.problem_type}_{y_col}_line.png")

    def _plot_strip(self, data: pd.DataFrame, y_col: str, y_label: str, title: str, output_dir: Path, sharey: bool):
        data = data.dropna(subset=['plot_x', y_col])
        if data.empty:
            return

        plt.figure()
        sns.stripplot(
            data=data,
            x='plot_x', y=y_col,
            hue="device" if sharey else None,
            jitter=True,
            dodge=sharey,
            alpha=0.7,
            size=6
        )

        plt.title(title)
        plt.xlabel(self.x_label)
        plt.ylabel(y_label)
        self._save(output_dir, f"{self.problem_type}_{y_col}_strip.png")

    def _plot_box(self, data: pd.DataFrame, y_col: str, y_label: str, title: str, output_dir: Path, sharey: bool):
        data = data.dropna(subset=['plot_x', y_col])
        if data.empty:
            return

        plt.figure()
        sns.boxplot(
            data=data,
            x='plot_x', y=y_col,
            hue="device" if sharey else None,
            width=0.5,
            linewidth=1.5,
            flierprops={"marker": "o", "markersize": 4}
        )

        plt.title(title)
        plt.xlabel(self.x_label)
        plt.ylabel(y_label)
        self._save(output_dir, f"{self.problem_type}_{y_col}_box.png")
    
    def _plot_speedup(self, data: pd.DataFrame, output_dir: Path):
        if not self.baseline_device:
            logger.warning("No baseline_device defined, skipping speedup plot")
            return

        if self.baseline_device not in data['device'].unique():
            logger.warning(f"Baseline device '{self.baseline_device}' not found in data")
            return

        baseline = data[data['device'] == self.baseline_device].groupby('plot_x')['cycles'].mean()
        devices = [d for d in data['device'].unique() if d != self.baseline_device]

        plt.figure()
        ax = plt.gca()
        ax.set_yscale('log')

        ax.axhline(y=1.0, color='gray', linestyle='--', linewidth=1, alpha=0.7, label='baseline')

        for device in devices:
            device_data = data[data['device'] == device].groupby('plot_x')['cycles'].mean()
            speedup = baseline / device_data
            ax.plot(speedup.index, speedup.values, marker='o', linewidth=2.5, label=device)

        plt.title(f"Relative speedup (baseline: {self.baseline_device})")
        plt.xlabel(self.x_label)
        plt.ylabel(f"Speedup (× faster than {self.baseline_device})")
        plt.legend()
        self._save(output_dir / "speedup" / "combined", f"{self.problem_type}_speedup.png")

    def _plot_bar_grouped(self, data: pd.DataFrame, y_col: str, y_label: str, title: str, output_dir: Path, sharey: bool):
        data = data.dropna(subset=['plot_x', y_col])
        if data.empty:
            return

        grouped = data.groupby(['plot_x', 'device'])[y_col].mean().reset_index()

        plt.figure()
        sns.barplot(
            data=grouped,
            x='plot_x', y=y_col,
            hue='device' if sharey else None,
            palette='tab10' if sharey else None
        )

        plt.title(title)
        plt.xlabel(self.x_label)
        plt.ylabel(y_label)
        if sharey:
            plt.legend(title='device')
        self._save(output_dir, f"{self.problem_type}_{y_col}_bar.png")

    def _plot_scatter_cpi(self, data: pd.DataFrame, output_dir: Path, sharey: bool):
        if 'cpi' not in data.columns:
            logger.warning("Column cpi not found, skipping scatter CPI plot")
            return

        data = data.dropna(subset=['plot_x', 'cpi'])
        if data.empty:
            return

        plt.figure()
        sns.stripplot(  
            data=data,
            x='plot_x', y='cpi',
            hue='device' if sharey else None,
            jitter=True,
            dodge=sharey,
            alpha=0.6,
            size=5
        )

        plt.title("CPI vs Sequence Length")
        plt.xlabel(self.x_label)
        plt.ylabel("CPI")
        if sharey:
            plt.legend(title='device')
        self._save(output_dir, f"{self.problem_type}_cpi_scatter.png")

    def _plot_box_last_case(self, data: pd.DataFrame, y_col: str, y_label: str, output_dir: Path):
        if data.empty:
            return

        last_x = data['plot_x'].max()
        filtered = data[data['plot_x'] == last_x].dropna(subset=[y_col])

        if filtered.empty:
            return

        plt.figure()
        ax = sns.boxplot(
            data=filtered,
            x='device', y=y_col,
            palette='tab10',
            width=0.5,
            linewidth=1.5,
            flierprops={"marker": "o", "markersize": 4}
        )

        sns.stripplot(
            data=filtered,
            x='device', y=y_col,
            color='black',
            alpha=0.4,
            size=4,
            jitter=True,
            ax=ax
        )

        plt.title(f"Distribución de {y_label} — Tamaño {int(last_x)}")
        plt.xlabel("Device")
        plt.ylabel(y_label)
        self._save(output_dir / "box", f"{self.problem_type}_{y_col}_box_zoom.png")