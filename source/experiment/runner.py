from experiment.task import TaskBuilder, Task
from hardware.drivers.driver_factory import DriverFactory
from hardware.quartus.compiler import QuartusCompiler
from hardware.quartus.timing import TimingAnalyzer
from problems.problem_factory import ProblemFactory
from hardware.quartus.simulator import QuartusSimulator
from serialization.serializer_factory import SerializerFactory
from analysis.result_manager import ResultManager
from analysis.visualizer import Visualizer
from pathlib import Path
import logging
import json
from datetime import datetime

logger = logging.getLogger('Runner')

class ExperimentRunner():
    def __init__(self, config: dict, verbose: bool = False, run_timestamp = None):
        self.config = config
        self.verbose = verbose
        self.run_timestamp = run_timestamp or datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.recover_path = None
        self.recovery_timestamp = None

    @classmethod
    def from_recovery(cls, recover_path: Path, verbose: bool = False, recovery_timestamp: str = None):
        metadata_path = recover_path / "metadata.json"
        if not metadata_path.exists():
            raise FileNotFoundError(f"No metadata.json found at {recover_path}")
        
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        config = metadata["config"]
        original_timestamp = metadata["timestamp"]

        instance = cls(config=config, verbose=verbose, run_timestamp=original_timestamp)
        instance.recover_path = recover_path
        instance.recovery_timestamp = recovery_timestamp
        return instance

    def _update_recovery_metadata(self, experiment_path: Path):
        metadata_path = experiment_path / "metadata.json"
        if not metadata_path.exists():
            return

        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        if "recovery_runs" not in metadata:
            metadata["recovery_runs"] = []

        metadata["recovery_runs"].append({
            "timestamp": self.recovery_timestamp,
        })

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

    def _write_metadata(self, experiment_path, experiment):
        metadata = {
            "timestamp": self.run_timestamp,
            "experiment": experiment["name"],
            "config": self.config,
        }
        with open(experiment_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

    def run(self):
        compiler = QuartusCompiler(verbose=self.verbose)
        timing_analyzer = TimingAnalyzer(verbose=self.verbose)
        simulator = QuartusSimulator(verbose=self.verbose)
        driver_factory = DriverFactory(self.config["devices"], compiler, timing_analyzer, simulator)
        #task_builder = TaskBuilder(Path(self.config["config"]["root_dir"]))
        root_dir = Path(self.config["config"]["root_dir"])

        for experiment in self.config["experiments"]:
            experiment_path = root_dir / experiment["name"] / self.run_timestamp
            experiment_path.mkdir(parents=True, exist_ok=True)

            if self.recover_path:
                self._update_recovery_metadata(experiment_path)
            else:
                self._write_metadata(experiment_path, experiment)

            task_builder = TaskBuilder(experiment_path)
            single_exp_config = {**self.config, "experiments": [experiment]} # To avoid duplicated tasks
            tasks = task_builder.create_tasks(single_exp_config)
            result_manager = ResultManager()


            for task in tasks:
                logger.info(f"Running {task.name} on {task.device_name}")
                driver = driver_factory.get(task.device_name)
                output_csv = task.output_dir / "output.csv"
                if output_csv.exists():
                    logger.info(f"Task {task.id} already completed, loading existing result")
                    driver.current_params = task.params
                    result = driver._parse_results(output_csv)
                    result_manager.add(result)
                    continue
                
                problem = ProblemFactory.get(task.problem_name, task.params)

                serializer = SerializerFactory.get(task.problem_name, task.params)
                logger.info(f"Generating inputs for task {task.id} in path {task.output_dir}")
                serializer.write(problem, task.output_dir)

                input_file_path = (task.output_dir / f"input.mem").resolve().as_posix()
                hw_params = task.params.copy()
                hw_params["input_file"] = input_file_path
                
                task.output_dir.mkdir(parents=True, exist_ok=True)
                with open(task.output_dir / "params.json", "w") as file:
                    json.dump({"params": task.params}, file, indent=2)

                driver.prepare_hardware(hw_params)
                result = driver.run_simulation(task.output_dir)

                result_manager.add(result)

            logger.info("Generating plots...")
            derived_path = experiment_path / "derived"
            result_manager.save(derived_path / "summary_results.csv")
            visualizer = Visualizer(result_manager.df)
            visualizer.plot_performance_summary(derived_path / "plots")