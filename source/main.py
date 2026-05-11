from core.config import load_config
import logging
import argparse
from experiment.runner import ExperimentRunner
from analysis.visualizer import Visualizer
from analysis.result_manager import ResultManager
from pathlib import Path
from datetime import datetime
import os

parser = argparse.ArgumentParser(prog="AutoFPGA", description="Automatic experiments for FPGA")
parser.add_argument('-c', '--config', default="./config/config.json")
parser.add_argument('-r', '--recover')
parser.add_argument('-v', '--verbose', action='store_true') 
parser.add_argument('-e', '--experiment', action='store_true')
parser.add_argument('-l', '--logging', default="./logging/latest.log")
parser.add_argument('-p', '--plot')
parser.add_argument('--csv')
parser.add_argument('--baseline', default=None)
args = parser.parse_args()

start_timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
log_path = Path(args.logging).parent / f"{start_timestamp}.log"
os.makedirs(log_path.parent, exist_ok=True)

logger = logging.getLogger('AutoFPGA')
logging.basicConfig(
    level=logging.DEBUG,
    filename=log_path,
    filemode='w',
    format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
    )

logger.info("Program started!")
logger.debug(f"Config file is {args.config}")
config = load_config(args.config)

if args.experiment:
    runner = ExperimentRunner(
        config=config,
        verbose=args.verbose,
        run_timestamp=start_timestamp
    )
    runner.run()
elif args.recover is not None:
    runner = ExperimentRunner.from_recovery(
        recover_path=Path(args.recover),
        verbose=args.verbose,
        recovery_timestamp=start_timestamp
    )
    runner.run()
elif args.plot is not None:
    csv_path = Path(args.plot)
    plots_dir = csv_path.parent / "plots"
    visualizer = Visualizer(baseline_device=args.baseline)
    visualizer.set_df_from_csv(args.plot)
    visualizer.plot_performance_summary(plots_dir)
elif args.csv is not None:
    result_manager = ResultManager()
    result_manager.recover_csv(Path(args.csv), Path("./data/recovery.csv"))