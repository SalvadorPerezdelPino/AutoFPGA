from compiler import *
from experiment import *
import os
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automatizador de test de la mochila")
    parser.add_argument("--compile", action="store_true")
    parser.add_argument("--config", default="../config/config.json")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print("Error: config file not found.")
        exit(1)

    manager = ExperimentManager(config_file=args.config, verbose=args.verbose)

    if args.compile or args.all:
        manager.compile()

    manager.run_single(manager.config)



