# vLLM on Apple Silicon Automation

This project provides a robust, automated harness to run [vLLM](https://github.com/vllm-project/vllm) on Apple Silicon (M1/M2/M3) devices using the [vllm-metal](https://github.com/vllm-project/vllm-metal) plugin.

## Prerequisites
- macOS on Apple Silicon (arm64)
- Internet connection (for downloading wheels and models)
- `curl`

## Quick Start

1.  **Setup Environment**
    ```bash
    make setup
    ```
    This will:
    - Check your environment.
    - Install `uv` (fast Python package manager) if missing.
    - Create a virtual environment (`.venv`).
    - Build/Install vLLM base and the `vllm-metal` plugin.

2.  **Download a Model**
    ```bash
    make download-model MODEL=facebook/opt-125m
    ```
    *Defaults to `facebook/opt-125m`. You can specify any HF model.*

3.  **Run vLLM**
    ```bash
    make run MODEL=facebook/opt-125m
    ```
    The server will start at `http://localhost:8000`.

4.  **Test Installation**
    ```bash
    make test
    ```

## Models Guide (Mac Metal)
**Status**: 
- ✅ **Standard (Float16)**: Works great.
- ⚠️ **Quantized (AWQ)**: Currently unstable/broken on `vllm-metal` 0.1.0. **Avoid AWQ models for now.**

**Recommended Models (for 9-10GB available RAM):**
- **Tiny**: `HuggingFaceTB/SmolLM2-135M-Instruct`
- **Small**: `Qwen/Qwen2.5-1.5B-Instruct`
- **Medium**: `Qwen/Qwen2.5-3B-Instruct` (~6GB VRAM, should fit)

> [!WARNING]
> Larger models (7B, 14B, 32B) require significantly more RAM (14GB+ for 7B FP16). To run them, you must free up system memory or wait for working 4-bit quantization support.

```bash
make run MODEL=Qwen/Qwen2.5-3B-Instruct
```

## High RAM Models (Reboot Required)
If you reboot and have **25GB+ free RAM** (out of 36GB), you can try these standard (non-quantized) models. AWQ is avoided due to current instability.

- **DeepSeek R1 Distill 7B**: `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B` (~15GB VRAM)
- **Qwen 2.5 7B**: `Qwen/Qwen2.5-7B-Instruct` (~15GB VRAM)
- **Qwen 2.5 14B**: `Qwen/Qwen2.5-14B-Instruct` (~29GB VRAM - **Very Tight**)

```bash
# Recommended for 36GB Mac
make run MODEL=Qwen/Qwen2.5-7B-Instruct

# Experimental (May OOM if OS uses >6GB)
make run MODEL=Qwen/Qwen2.5-14B-Instruct
```

## Experimental Quantization
We are testing support for specific quantization formats. Currently, pre-quantized MLX models (via `mlx-community`) are the recommended approach.

```bash
# Test MLX 4-bit Quantization (Qwen 1.5B)
make test-mlx
```

## Customization
- **Makefile**: Variables like `VENV_DIR`, `MODEL`, and `HF_CACHE` can be overridden.
- **scripts/setup_env.sh**: Contains the core installation logic.

## Service Management (LaunchAgents)
You can run models as background services (LaunchAgents), allowing them to start/stop independently on dedicated ports.

### Setup
```bash
./vllm-ctl install
```

### Usage
```bash
# Start a model (e.g., Command R on port 8001)
./vllm-ctl start command-r

# Start the Router (Port 8000)
./vllm-ctl start router

# Check status of all models
./vllm-ctl status

# Stop a model
./vllm-ctl stop command-r

# View logs
./vllm-ctl logs command-r
```

### Shell Autocomplete
To enable tab completion for commands and models:
```bash
source scripts/vllm-completion.bash
```
(Add this line to your `~/.zshrc` or `~/.bashrc` to make it permanent.)

### Available Services
For a full list of models, ports, and memory requirements, see [MODELS.md](MODELS.md).

| Model | Port | Type |
| :--- | :--- | :--- |
| `router` | 8000 | 🔀 OpenAI Router |
| `command-r` | 8001 | 💬 Chat |
| `yi-1.5` | 8002 | 💬 Chat |
| ... and more (see [MODELS.md](MODELS.md)) | | |

## OpenAI Router (Port 8000)
A `router` service is available on port 8000. It is an OpenAI-compatible endpoint that federates all other models.
- **Base URL**: `http://localhost:8000/v1`
- **API Key**: `EMPTY`
- **Model Usage**: You can request any model by its name (e.g., `model="phi-4"`) and the router will forward the request to the correct port.

**Example**:
```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi-4",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Notes
- Docker is **not supported** for GPU acceleration on Mac Metal. This setup runs natively using a virtual environment.
- Large models require significant RAM. M1/M2/M3 Max/Ultra chips are recommended for 7B+ models.
