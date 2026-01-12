from dataclasses import dataclass
from typing import List, Dict, Any
from pathlib import Path
import itertools

@dataclass
class Task():
    id: str
    name: str
    device_name: str
    problem_name: str
    params: Dict[str, Any]
    output_dir: Path

class TaskBuilder():
    def __init__(self, context: Path):
        self.context = context
        
    def create_tasks(self, config: dict) -> List[Task]:
        tasks = []

        experiments = config.get("experiments", [])
        problems_config = config.get("problems", {})

        for exp_cfg in experiments:
            exp_tasks = self._generate_tasks_for_experiment(exp_cfg, problems_config)
            tasks.extend(exp_tasks)
        
        return tasks
    
    def _generate_tasks_for_experiment(self, exp_cfg: dict, problems_config: dict) -> List[Task]:
        generated = []
        exp_name = exp_cfg.get("name", "unnamed")
        problem_name = exp_cfg.get("problem")
        devices = exp_cfg.get("devices", [])
        sweep_vars = exp_cfg.get("sweep_vars", {})

        base_params = problems_config.get(problem_name, {}).copy()

        param_keys = []
        param_values_list = []

        for key, val in sweep_vars.items():
            param_keys.append(key)
            
            if isinstance(val, dict) and "start" in val:
                step = val.get("step", 1)
                r = range(val["start"], val["stop"] + 1, step) 
                param_values_list.append(list(r))
            elif isinstance(val, list):
                param_values_list.append(val)
            else:
                param_values_list.append([val])

        combinations = list(itertools.product(*param_values_list))

        run_counter = 0

        for values in combinations:
            current_sweep_params = dict(zip(param_keys, values))
            
            final_params = {**base_params, **current_sweep_params}
            
            for device in devices:
                run_id = f"{run_counter:04d}"
                # TODO: Choose correct task path
                task_dir = self.context / exp_name / device / run_id
                
                new_task = Task(
                    id=run_id,
                    name=exp_name,
                    device_name=device,
                    problem_name=problem_name,
                    params=final_params,
                    output_dir=task_dir
                )
                generated.append(new_task)
            
            run_counter += 1

        return generated