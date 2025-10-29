from knapsack import *
from compiler import *
from experiment import *
import argparse

cpus = ["monocycle", "multicycle", "pipeline"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automatizador de test de la mochila")
    parser.add_argument("--cpu", type=str, default="multicycle")
    parser.add_argument("--compile", action="store_true")
    parser.add_argument("--sweep_items", action="store_true")
    parser.add_argument("--sweep_capacity", action="store_true")
    parser.add_argument("--graph", action="store_true")
    parser.add_argument("--config", default="../config/config.json")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print("Error: No existe archivo de configuración")
        exit()

    if args.cpu not in cpus:
        print(f"CPU no en la lista: {cpus}")
        exit()

    with open(args.config, "r") as file:
        data = json.load(file)
        project_path = data[args.cpu]["paths"]["quartus_project"]

    if args.compile or args.all:
        compiler = QuartusCompiler(project_path=project_path, cpu=args.cpu, verbose=args.verbose)
        compiler.compile_all()
        #compile_full_project(args.cpu)

    manager = ExperimentManager(args.cpu, args.config, args.verbose)

    if args.sweep_items or args.all:
        manager.sweep("items")
        
    if args.sweep_capacity or args.all:
        manager.sweep("capacity")

    if args.graph or args.all:
        plot_comparison()
        plot_box()
        #plot_gaussian_distribution(f"../data/monocycle/outputs/monocycle_c20_n30.csv")


