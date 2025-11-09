import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class Plotter():
    def __init__(self):
        plt.style.use('ggplot')

    def plot_distribution(self, data, label="label", xlabel="xlabel", ylabel="ylabel", title="Title", bins=15):
        plt.figure(figsize=(7,5))
        plt.hist(data, bins=bins, alpha=0.6, label=label, edgecolor="black")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend()
        plt.show()

    def plot_variable(self, y, x=None, label="Variable", xlabel="X", ylabel="Y", title="Title"):
        if x is None:
            x = np.arange(len(y))

        plt.figure(figsize=(7,5))
        plt.plot(x, y, marker='o', linestyle='-', color='C0', label=label)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
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
