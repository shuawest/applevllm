# Supported Models & Service Reference

This document lists the models optimized for Apple Silicon (MLX 4-bit) supported by our service management scripts.

## Overview
These models are pre-quantized (4-bit) to fit within the Unified Memory of a 36GB+ Mac. They are managed as LaunchAgents on specific ports to allow simultaneous (or switched) access without checking port conflicts.

## Model Reference Table

| Service Name | Port | Model / HF Repo | Est. Memory (4-bit) | Type | Context | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `router` | 8000 | `litellm` (Router) | **<100 MB** | 🔀 Router | - | OpenAI-compatible router federating all models. |
| `smollm2-135m`| 8010 | `mlx-community/SmolLM2-135M-Instruct-4bit` | **<200 MB** | ⚡ Tiny | 8k | Extremely fast, good for basic tasks. |
| `qwen-0.5` | 8011 | `mlx-community/Qwen2.5-0.5B-Instruct-4bit` | **~400 MB** | ⚡ Tiny | 32k | Surprisingly capable for its size. |
| `qwen-1.5` | 8012 | `mlx-community/Qwen2.5-1.5B-Instruct-4bit` | **~1 GB** | 🚀 Small | 32k | Great balance of speed and smarts. |
| `llama-3.2-1b`| 8013 | `mlx-community/Llama-3.2-1B-Instruct-4bit` | **~800 MB** | 🚀 Small | 128k | Llama 3.2 text-only edge model. |
| `llama-3.2-3b`| 8014 | `mlx-community/Llama-3.2-3B-Instruct-4bit` | **~2 GB** | 🚀 Small | 128k | Strong edge model, instruction tuned. |
| `command-r` | 8001 | `mlx-community/c4ai-command-r-v01-4bit` | **~19 GB** | 💬 Chat | 128k | Excellent for RAG and tool use. Strong reasoning. |
| `yi-1.5` | 8002 | `mlx-community/Yi-1.5-34B-Chat-4bit` | **~19 GB** | 💬 Chat | 32k | Balanced, high-quality, creative chat model. |
| `mixtral` | 8004 | `mlx-community/Mixtral-8x7B-Instruct-v0.1-4bit` | **~26 GB** | 💬 Chat | 32k | Mixture of Experts (MoE). High throughput, tight fit on 36GB. |
| `codestral` | 8005 | `mlx-community/Codestral-22B-v0.1-4bit` | **~14 GB** | 💻 Code | 32k | Mistral's dedicated coding model. Python/SQL specialist. |
| `yi-coder` | 8006 | `mlx-community/Yi-Coder-34B-Chat-4bit` | **~19 GB** | 💻 Code | 128k | Powerful coding model with long context support. |
| `starcoder2` | 8007 | `mlx-community/starcoder2-15b-4bit` | **~9 GB** | 💻 Code | 16k | Code completion specialist. Fast and lightweight. |
| `phi-4` | 8008 | `mlx-community/phi-4-4bit` | **~9 GB** | 🧠 Logic | 16k | Microsoft's reasoning model. Exceptionally smart for <15B. |
| `qwen-2.5` | 8009 | `mlx-community/Qwen2.5-32B-Instruct-4bit` | **~18 GB** | 🧠 Logic | 128k | Strong math and logic capabilities. |
| `llava-1.5-7b`| 8015 | `mlx-community/llava-1.5-7b-4bit` | **~4 GB** | 🖼️ Vision | 4k | Vision-language model. Image understanding. ⚠️ Experimental |
| `llava-qwen-0.5b`| 8016 | `mlx-community/llava-interleave-qwen-0.5b-4bit` | **~300 MB** | 🖼️ Vision | 32k | Tiny vision model for testing. ⚠️ Experimental |
| `qwq-32b` | 8017 | `mlx-community/QwQ-32B-Preview-4bit` | **~17 GB** | 🧮 Math | 32k | Advanced reasoning and math specialist. |
| `qwen-math-1.5b`| 8018 | `mlx-community/Qwen2.5-Math-1.5B-Instruct-4bit` | **~1 GB** | 🧮 Math | 32k | Compact math solver. |
| `deepseek-r1-1.5b`| 8019 | `mlx-community/DeepSeek-R1-Distill-Qwen-1.5B-4bit` | **~1 GB** | 🧠 Reasoning | 32k | Distilled reasoning model. |

## Categories

- **⚡ Tiny** (135M-500M params): Ultra-fast, minimal RAM, great for simple tasks
- **🚀 Small** (1B-3B params): Balanced speed and capability for everyday use
- **💬 Chat** (27B-35B params): Large general-purpose conversational models
- **💻 Code** (15B-34B params): Programming, code generation, technical tasks
- **🧠 Logic/Reasoning** (14B-32B params): Math, reasoning, complex problem-solving
- **🖼️ Vision** (0.5B-7B params): Image understanding (⚠️ Experimental vLLM support)
- **🧮 Math** (1.5B-32B params): Mathematical reasoning and problem solving
- **🔀 Router** (Port 8000): Federates all models via OpenAI API

## Notes on Memory
*   **Est. Memory**: Approximate RAM usage for the model weights + minimal KV cache.
*   **36GB RAM Limits**:
    *   Models >20GB (Mixtral) are "tight fits". Close other apps.
    *   Models ~19GB (Command R, Yi) allow for modest multitasking.
    *   Models <15GB (Codestral, Phi-4) run comfortably alongside other apps.
*   **Context Window**: Increasing the context window (feeding large documents) will increase RAM usage significantly.

## Usage
To install and start a service:
```bash
./vllm-ctl install
./vllm-ctl start <service_name>
```

Example:
```bash
# Start the Logic model (Phi-4)
./vllm-ctl start phi-4
```
