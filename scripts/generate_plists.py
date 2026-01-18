#!/usr/bin/env python3
import os
import plistlib
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(os.getcwd()).absolute()
VENV_PYTHON = PROJECT_ROOT / ".venv" / "bin" / "python"
HF_CLI = PROJECT_ROOT / ".venv" / "bin" / "hf"
SERVICES_DIR = PROJECT_ROOT / "services"
LOGS_DIR = Path.home() / "Library" / "Logs" / "vllm"

# Ensure directories exist
SERVICES_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Model Definitions
# Import shared model definitions
try:
    from model_defs import MODELS
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).parent))
    from model_defs import MODELS

def generate_plist(name, config):
    port = config["port"]
    repo_id = config["repo_id"]
    safe_name = repo_id.replace("/", "_")
    model_path = f"models/{safe_name}"
    
    label = f"com.jowest.vllm.{name}"
    plist_path = SERVICES_DIR / f"{label}.plist"
    
    # We use a bash wrapper to ensure environment is set up
    # This downloads the model if missing, then runs the server
    script_command = (
        f"source {PROJECT_ROOT}/.venv/bin/activate && "
        f"hf download {repo_id} --local-dir {model_path} && "
        f"python -m vllm.entrypoints.openai.api_server "
        f"--model {model_path} "
        f"--served-model-name {name} "
        f"--port {port} "
        f"--trust-remote-code"
    )

    plist_content = {
        "Label": label,
        "ProgramArguments": [
            "/bin/bash",
            "-l",
            "-c",
            script_command
        ],
        "WorkingDirectory": str(PROJECT_ROOT),
        "StandardOutPath": str(LOGS_DIR / f"{name}.out.log"),
        "StandardErrorPath": str(LOGS_DIR / f"{name}.err.log"),
        "RunAtLoad": False,
        "KeepAlive": False,
        "EnvironmentVariables": {
            "PATH": f"{PROJECT_ROOT}/.venv/bin:/usr/bin:/bin:/usr/sbin:/sbin",
            "HF_HUB_ENABLE_HF_TRANSFER": "1"
        }
    }

    with open(plist_path, 'wb') as f:
        plistlib.dump(plist_content, f)
    
    print(f"Generated {plist_path} (Port {port})")


def generate_router_plist():
    """Generates the plist for the LiteLLM router service."""
    label = "com.jowest.vllm.router"
    plist_path = SERVICES_DIR / f"{label}.plist"
    config_path = PROJECT_ROOT / "router_config.yaml"
    
    # Command to run litellm
    # We need to make sure we generate the config first
    script_command = (
        f"source {PROJECT_ROOT}/.venv/bin/activate && "
        f"python3 {PROJECT_ROOT}/scripts/federated_router.py"
    )

    plist_content = {
        "Label": label,
        "ProgramArguments": [
            "/bin/bash",
            "-l",
            "-c",
            script_command
        ],
        "WorkingDirectory": str(PROJECT_ROOT),
        "StandardOutPath": str(LOGS_DIR / "router.out.log"),
        "StandardErrorPath": str(LOGS_DIR / "router.err.log"),
        "RunAtLoad": False,
        "KeepAlive": False,
        "EnvironmentVariables": {
            "PATH": f"{PROJECT_ROOT}/.venv/bin:/usr/bin:/bin:/usr/sbin:/sbin",
             # Router needs to know where packages are if standard path isn't enough
        }
    }

    with open(plist_path, 'wb') as f:
        plistlib.dump(plist_content, f)
    print(f"Generated {plist_path} (Port 8000)")

def main():
    print(f"Generating LaunchAgents in {SERVICES_DIR}...")
    for name, config in MODELS.items():
        generate_plist(name, config)
    
    # Generate Router Service
    generate_router_plist()
    
    print("Done.")

if __name__ == "__main__":
    main()
