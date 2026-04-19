from dataclasses import dataclass
from typing import List, Dict, Any, Union
from pathlib import Path
import itertools
import logging
import hashlib
import json
from problems.problem_factory import ProblemFactory

logger = logging.getLogger('Task')

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
    
    def _resolve_values(self, val: Union[Dict, List, Any]) -> List[Any]:
        if isinstance(val, dict) and "start" in val:
            step = val.get("step", 1)
            return list(range(val["start"], val["stop"] + 1, step))
        elif isinstance(val, list):
            return val
        else:
            return [val]
        
    def _params_seed(self, params: dict, base_seed: int, problem_name: str, run_index: int) -> int:
        problem_class = ProblemFactory._problems[problem_name]
        size_keys = problem_class.SWEEP_PARAMS
        structural = {k: params[k] for k in size_keys if k in params}
        structural["base_seed"] = base_seed
        structural["run_index"] = run_index
        digest = hashlib.md5(json.dumps(structural, sort_keys=True).encode()).hexdigest()
        return int(digest[:8], 16)
    
    def _generate_tasks_for_experiment(self, exp_cfg: dict, problems_config: dict) -> List[Task]:
        generated = []
        exp_name = exp_cfg.get("name", "unnamed")
        problem_name = exp_cfg.get("problem")
        devices = exp_cfg.get("devices", [])
        base_seed = exp_cfg.get("seed", None)
        n_instances = exp_cfg.get("n_instances", 1)

        base_params = problems_config.get(problem_name, {}).copy()

        sweep_vars = exp_cfg.get("sweep_vars", {})
        sweep_keys = list(sweep_vars.keys())
        sweep_values = [self._resolve_values(val) for val in sweep_vars.values()]
        
        sweep_combinations = []
        if sweep_vars:
            for combo in itertools.product(*sweep_values):
                sweep_combinations.append(dict(zip(sweep_keys, combo)))
        else:
            sweep_combinations = [{}]

        coupled_cfg = exp_cfg.get("coupled_vars", {})
        coupled_combinations = []
        
        if coupled_cfg and "keys" in coupled_cfg and "range" in coupled_cfg:
            target_keys = coupled_cfg["keys"]
            range_cfg = coupled_cfg["range"]
            
            values_list = self._resolve_values(range_cfg) 
            
            for val in values_list:
                param_dict = {k: val for k in target_keys}
                coupled_combinations.append(param_dict)
                
        else:
            coupled_combinations = [{}]

        run_counter = 0

        for s_params in sweep_combinations:
            for c_params in coupled_combinations:
                final_params = {**base_params, **s_params, **c_params}
                

                case_id = f"case_{run_counter:04d}"
                for device in devices:
                    for instance_index in range(n_instances):
                        instance_params = final_params.copy()
                        task_dir = self.context / "raw" / device / case_id / f"instance_{instance_index}"
                        if base_seed is not None:
                            instance_params["base_seed"] = base_seed
                            instance_params["seed"] = self._params_seed(
                                final_params, base_seed, problem_name, instance_index  # ← instance_index
                            )
                        new_task = Task(
                            id=f"{case_id}_i{instance_index}",
                            name=exp_name,
                            device_name=device,
                            problem_name=problem_name,
                            params=instance_params,
                            output_dir=task_dir
                        )
                        generated.append(new_task)
                
                run_counter += 1

        return generated