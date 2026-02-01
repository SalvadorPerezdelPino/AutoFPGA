from core.config import load_config
import logging

from experiment.runner import ExperimentRunner

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

config = load_config("./config/config.json")

verbose = True

runner = ExperimentRunner(config=config, verbose=verbose)

runner.run()