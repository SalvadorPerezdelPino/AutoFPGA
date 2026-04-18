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

logger = logging.getLogger('Runner')

class ExperimentRunner():
    def __init__(self, config: dict, verbose: bool = False):
        self.config = config
        self.verbose = verbose

    def run(self):
        compiler = QuartusCompiler(verbose=self.verbose)
        timing_analyzer = TimingAnalyzer(verbose=self.verbose)
        simulator = QuartusSimulator(verbose=self.verbose)
        driver_factory = DriverFactory(self.config["devices"], compiler, timing_analyzer, simulator)
        task_builder = TaskBuilder(Path(self.config["config"]["root_dir"]))
        tasks = task_builder.create_tasks(self.config)
        result_manager = ResultManager()

        for task in tasks:
            logger.info(f"Running {task.name} on {task.device_name}")
            driver = driver_factory.get(task.device_name)
            problem = ProblemFactory.get(task.problem_name, task.params)

            serializer = SerializerFactory.get(task.problem_name, task.params)
            logger.info(f"Generating inputs for task {task.id} in path {task.output_dir}")
            serializer.write(problem, task.output_dir)

            input_file_path = (task.output_dir / f"input.mem").resolve().as_posix()
            hw_params = task.params.copy()
            hw_params["input_file"] = input_file_path
            driver.prepare_hardware(hw_params)
            result = driver.run_simulation(task.output_dir)

            result_manager.add(result)

        experiment_path = Path(self.config["config"]["root_dir"]) / self.config["experiments"][0]["name"]
        summary_path = experiment_path / "summary_results.csv"
        result_manager.save(summary_path)

        logger.info("Generating plots...")
        master_df = result_manager.df
        visualizer = Visualizer(master_df)

        plots_dir = experiment_path / "plots"

        visualizer.plot_performance_summary(plots_dir)