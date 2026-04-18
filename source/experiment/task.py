from dataclasses import dataclass
from typing import List, Dict, Any, Union
from pathlib import Path
import itertools
import logging
import hashlib
import json

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
        
    def _params_seed(self, params: dict) -> int:
        structural = {k: v for k, v in params.items() if k != "input_file"}
        digest = hashlib.md5(json.dumps(structural, sort_keys=True).encode()).hexdigest()
        return int(digest[:8], 16)
    
    def _generate_tasks_for_experiment(self, exp_cfg: dict, problems_config: dict) -> List[Task]:
        generated = []
        exp_name = exp_cfg.get("name", "unnamed")
        problem_name = exp_cfg.get("problem")
        devices = exp_cfg.get("devices", [])
        base_seed = exp_cfg.get("seed", None)

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
                
                if base_seed is not None:
                    final_params["seed"] = self._params_seed(final_params)

                for device in devices:
                    run_id = f"{run_counter:04d}"
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