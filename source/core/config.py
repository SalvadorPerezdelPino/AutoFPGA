from pathlib import Path
from typing import Dict, Any
import json

class ConfigurationError(Exception):
    pass

def load_config(path: str) -> Dict[str, Any]:
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_path, "r") as f:
            data = json.load(f)
            return data
    except json.JSONDecodeError as e:
        raise ConfigurationError(f"{config_path} is not a valid JSON.") from e
    except Exception as e:
        raise ConfigurationError(f"Unexpected error while reading configuration.") from e