import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class Plotter():
    def __init__(self):
        self.df = None

    def load_csv(self, path):
        self.df = pd.read_csv(path, sep=';', decimal=',')

    def plot_distribution(self, data, label="label", xlabel="xlabel", ylabel="ylabel", title="Title", bins=15):
        plt.figure(figsize=(7,5))
        plt.style.use('ggplot')
        plt.hist(data, bins=bins, alpha=0.6, label=label, edgecolor="black")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend()
        plt.show()

    def plot_distribution_df(self, column, label=None, xlabel=None, ylabel=None, title=None, bins=15):
        if self.df is None:
            print("No DataFrame loaded")
            return

        data = self.df[column]

        plt.figure(figsize=(7,5))
        plt.style.use('ggplot')
        plt.hist(data, bins=bins, alpha=0.6, label=label or column, edgecolor="black")
        plt.xlabel(xlabel or column)
        plt.ylabel(ylabel)
        plt.title(title or f"{column} distribution")
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_variable(self, y, x=None, label="Variable", xlabel="X", ylabel="Y", title="Title"):
        if x is None:
            x = np.arange(len(y))

        plt.figure(figsize=(7,5))
        plt.style.use('ggplot')
        plt.plot(x, y, marker='o', linestyle='-', color='C0', label=label)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_variable_df(self, y_column, x_column=None, label=None, xlabel=None, ylabel=None, title=None):
        if self.df is None:
            print("No DataFrame loaded")
            return

        y = self.df[y_column]
        x = self.df[x_column] if x_column else np.arange(len(y))

        plt.figure(figsize=(7,5))
        plt.style.use('ggplot')
        plt.plot(x, y, marker='o', linestyle='-', color='C0', label=label or y_column)
        plt.xlabel(xlabel or (x_column or "Index"))
        plt.ylabel(ylabel or y_column)
        plt.title(title or f"{y_column} vs {x_column or 'Index'}")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend()
        plt.tight_layout()
        plt.show()


    def plot_boxplot(self, data, labels=None, title=None, width=0.8, ylabel="Value"):
        base_color = "C1"
        if not data:
            print("No data to graph")
            return

        positions = np.arange(1, len(data) + 1)

        fig, ax = plt.subplots(figsize=(7, 5))

        ax.boxplot(data,
                positions=positions,
                widths=width,
                patch_artist=True,
                showmeans=True,
                meanprops={"marker": "D", "markerfacecolor": "red", "markeredgecolor": "black"},
                medianprops={"color": "red", "linewidth": 1.2},
                boxprops={"facecolor": base_color, "edgecolor": "white", "linewidth": 0.8},
                whiskerprops={"color": "black", "linewidth": 1.2},
                capprops={"color": "black", "linewidth": 1.2})

        if labels:
            ax.set_xticks(positions)
            ax.set_xticklabels(labels, rotation=15, ha="right")
        else:
            ax.set_xticks(positions)
            ax.set_xticklabels([f"Dist {i+1}" for i in range(len(data))])

        if title:
            ax.set_title(title, fontsize=12, fontweight='bold')

        ax.set_ylabel(ylabel)
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        plt.tight_layout()
        plt.show()

    def plot_boxplot_df(self, columns, labels=None, title=None, width=0.8, ylabel="Value"):
        if self.df is None:
            print("No DataFrame loaded")
            return

        data = [self.df[col] for col in columns]
        self.plot_boxplot(data, labels=labels or columns, title=title, width=width, ylabel=ylabel)