from core.config import load_config
import logging
import argparse
from experiment.runner import ExperimentRunner
from analysis.visualizer import Visualizer
from analysis.result_manager import ResultManager
from pathlib import Path
import os

parser = argparse.ArgumentParser(prog="AutoFPGA", description="Automatic experiments for FPGA")
parser.add_argument('-c', '--config', default="./config/config.json")
parser.add_argument('-r', '--recover') # TODO: TBD
parser.add_argument('-v', '--verbose', action='store_true') 
parser.add_argument('-e', '--experiment', action='store_true')
parser.add_argument('-l', '--logging', default="./logging/latest.log")
parser.add_argument('-p', '--plot')
parser.add_argument('--csv')
args = parser.parse_args()

logger = logging.getLogger('AutoFPGA')
os.makedirs(os.path.dirname(args.logging), exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    filename=args.logging,
    filemode='w',
    format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
    )

logger.info("Program started!")
logger.debug(f"Config file is {args.config}")
config = load_config(args.config)

if args.experiment:
    runner = ExperimentRunner(config=config, verbose=args.verbose)
    runner.run()
elif args.plot is not None:
    visualizer = Visualizer()
    visualizer.set_df_from_csv(args.plot)
    visualizer.plot_performance_summary(Path("./data/plots/"))
elif args.csv is not None:
    result_manager = ResultManager()
    result_manager.recover_csv(Path(args.csv), Path("./data/recovery.csv"))