# Model Definitions
# Shared between generate_plists.py and generate_router_config.py

MODELS = {
    "command-r": {
        "repo_id": "mlx-community/c4ai-command-r-v01-4bit",
        "port": 8001,
        "est_ram": "19 GB",
        "params": "35B"
    },
    "yi-1.5": {
        "repo_id": "mlx-community/Yi-1.5-34B-Chat-4bit",
        "port": 8002,
        "est_ram": "19 GB",
        "params": "34B"
    },
    "mixtral": {
        "repo_id": "mlx-community/Mixtral-8x7B-Instruct-v0.1-4bit",
        "port": 8004,
        "est_ram": "26 GB",
        "params": "8x7B"
    },
    "codestral": {
        "repo_id": "mlx-community/Codestral-22B-v0.1-4bit",
        "port": 8005,
        "est_ram": "14 GB",
        "params": "22B"
    },
    "yi-coder": {
        "repo_id": "mlx-community/Yi-Coder-34B-Chat-4bit",
        "port": 8006,
        "est_ram": "19 GB",
        "params": "34B"
    },
    "starcoder2": {
        "repo_id": "mlx-community/starcoder2-15b-4bit",
        "port": 8007,
        "est_ram": "10 GB",
        "params": "15B"
    },
    "phi-4": {
        "repo_id": "mlx-community/phi-4-4bit",
        "port": 8008,
        "est_ram": "9 GB",
        "params": "14B"
    },
    "qwen-2.5": {
        "repo_id": "mlx-community/Qwen2.5-32B-Instruct-4bit",
        "port": 8009,
        "est_ram": "18 GB",
        "params": "32B"
    },
    "smollm2-135m": {
        "repo_id": "mlx-community/SmolLM2-135M-Instruct",
        "port": 8010,
        "est_ram": "200 MB",
        "params": "135M"
    },
    "qwen-0.5": {
        "repo_id": "mlx-community/Qwen2.5-0.5B-Instruct-4bit",
        "port": 8011,
        "est_ram": "400 MB",
        "params": "0.5B"
    },
    "qwen-1.5": {
        "repo_id": "mlx-community/Qwen2.5-1.5B-Instruct-4bit",
        "port": 8012,
        "est_ram": "1 GB",
        "params": "1.5B"
    },
    "llama-3.2-1b": {
        "repo_id": "mlx-community/Llama-3.2-1B-Instruct-4bit",
        "port": 8013,
        "est_ram": "800 MB",
        "params": "1B"
    },
    "llama-3.2-3b": {
        "repo_id": "mlx-community/Llama-3.2-3B-Instruct-4bit",
        "port": 8014,
        "est_ram": "2 GB",
        "params": "3B"
    },
    # Vision Models (VLMs) - Experimental vLLM support
    "llava-1.5-7b": {
        "repo_id": "mlx-community/llava-1.5-7b-4bit",
        "port": 8015,
        "est_ram": "4 GB",
        "params": "7B"
    },
    "llava-qwen-0.5b": {
        "repo_id": "mlx-community/llava-interleave-qwen-0.5b-4bit",
        "port": 8016,
        "est_ram": "300 MB",
        "params": "0.5B"
    },
    # Math & Reasoning Models
    "qwq-32b": {
        "repo_id": "mlx-community/QwQ-32B-Preview-4bit",
        "port": 8017,
        "est_ram": "17 GB",
        "params": "32B"
    },
    "qwen-math-1.5b": {
        "repo_id": "mlx-community/Qwen2.5-Math-1.5B-Instruct-4bit",
        "port": 8018,
        "est_ram": "1 GB",
        "params": "1.5B"
    },
    "deepseek-r1-1.5b": {
        "repo_id": "mlx-community/DeepSeek-R1-Distill-Qwen-1.5B-4bit",
        "port": 8019,
        "est_ram": "1 GB",
        "params": "1.5B"
    }
}
