#!/usr/bin/env python3
import yaml
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_ROOT / "router_config.yaml"

# Model Definitions (Must match generate_plists.py)
try:
    from model_defs import MODELS
except ImportError:
    # If running from script dir directly
    try:
        from scripts.model_defs import MODELS
    except ImportError:
        # Fallback for when running from root without package structure
        import sys
        sys.path.append(str(Path(__file__).parent))
        from model_defs import MODELS

def generate_config():
    model_list = []
    
    for name, config in MODELS.items():
        # define the model routing
        model_entry = {
            "model_name": name,
            "litellm_params": {
                "model": f"openai/{name}", # 'openai/' prefix tells litellm to use openai client
                "api_base": f"http://0.0.0.0:{config['port']}/v1",
                "api_key": "EMPTY"
            }
        }
        model_list.append(model_entry)
        
    config_data = {
        "model_list": model_list,
        "router_settings": {
            "num_retries": 3,
            "timeout": 600
        }
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        yaml.dump(config_data, f, sort_keys=False)
    
    print(f"Generated {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_config()
