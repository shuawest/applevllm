# vLLM on Apple Silicon

Production-ready system for running multiple vLLM models on Apple Silicon with automatic service management and OpenAI-compatible routing.

## Features

- 🚀 **Federated Router**: Single OpenAI-compatible endpoint (`localhost:8000`) for all models
- 📊 **Dynamic Model Discovery**: `/v1/models` endpoint aggregates metadata from running services
- 🔧 **Service Management**: macOS Launch Agents for background model services
- 💻 **Apple Silicon Optimized**: Uses MLX 4-bit quantized models for efficiency
- 🎯 **Simple CLI**:`./vllm-ctl` for all model operations

## Quick Start

### 1. Setup Environment
```bash
make setup
```
This installs `uv`, creates `.venv`, and installs vLLM with `vllm-metal` plugin.

### 2. Install Services
```bash
./vllm-ctl install
```
Generates LaunchAgent plists for all models and the router.

### 3. Start the Router
```bash
./vllm-ctl start router
```
The federated router starts on http://localhost:8000

### 4. Start Models
```bash
# Start a tiny model (uses only ~500MB RAM)
./vllm-ctl start smollm2-135m

# Check what's running
./vllm-ctl status
```

## Usage

### Service Management
```bash
# View all models and their status
./vllm-ctl status

# Start a specific model
./vllm-ctl start llama-3.2-3b

# Stop a model
./vllm-ctl stop llama-3.2-3b

# Stop everything
./vllm-ctl stop-all

# View logs
./vllm-ctl logs smollm2-135m

# Restart the router
./vllm-ctl restart router
```

### Using the API
```bash
# List available models (only shows running ones)
curl http://localhost:8000/v1/models

# Chat completion
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "smollm2-135m",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100
  }'
```

### Shell Autocomplete
Enable tab completion for commands and models:
```bash
source scripts/vllm-completion.bash
```
Add to your `~/.zshrc` to make it permanent.

## Models

See [MODELS.md](MODELS.md) for the complete list of supported models, ports, and memory requirements.

### Model Categories
- **⚡ Tiny** (100-400MB): SmolLM2-135M, Qwen-0.5B
- **🚀 Small** (1-2GB): Qwen-1.5B, Llama-3.2-1B/3B
- **💬 Chat** (14-26GB): Command-R, Yi-1.5, Gemma-2, Mixtral
- **💻 Code** (10-19GB): Codestral, Yi-Coder, StarCoder2

All models use MLX 4-bit quantization for optimal performance on Apple Silicon.

## Architecture

### Federated Router (Port 8000)
- **Frontend**: `scripts/federated_router.py` (FastAPI)
- **Backend**: LiteLLM (Port 8080)
- **Dynamic `/v1/models`**: Queries all running vLLM services and aggregates metadata
- **Transparent Proxying**: All other requests routed to LiteLLM

### Individual Models (Ports 8001-8014)
Each model runs as a separate vLLM server:
- Managed by macOS LaunchAgents
- Auto-downloads from HuggingFace on first start
- Logs to `~/Library/Logs/vllm/`

## Requirements

- **macOS**: Apple Silicon (M1/M2/M3/M4)
- **RAM**: Minimum 16GB (36GB recommended for large models)
- **Internet**: For downloading models

## Advanced

### Makefile Targets
```bash
make help          # Show all available targets
make setup         # Install dependencies
make install       # Install LaunchAgent services
make start         # Start router
make stop          # Stop all services
make status        # Show service status
make test          # Run pytest tests
make clean         # Remove virtual environment
```

### Development
```bash
# Run tests
make test

# Regenerate service plists
.venv/bin/python scripts/generate_plists.py

# Regenerate router config
.venv/bin/python scripts/generate_router_config.py
```

## Troubleshooting

### Models Won't Start
Check logs: `./vllm-ctl logs <model-name>`

### Port Conflicts
Stop all services: `./vllm-ctl stop-all`

### Memory Issues
Start smaller models first (`smollm2-135m`, `qwen-0.5`) and check RAM with `./vllm-ctl status`

## License

See individual component licenses:
- vLLM: Apache 2.0
- LiteLLM: MIT
- Models: See HuggingFace model cards
