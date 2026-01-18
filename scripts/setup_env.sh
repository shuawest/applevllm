#!/bin/bash
set -euo pipefail

# Configuration
VLLM_VERSION="0.13.0"
VENV_DIR=".venv"
PROJECT_ROOT="$(pwd)"
VENV_PATH="${PROJECT_ROOT}/${VENV_DIR}"
REPO_OWNER="vllm-project"
REPO_NAME="vllm-metal"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Ensure we are on Apple Silicon
if [[ $(uname -m) != "arm64" ]] || [[ $(uname -s) != "Darwin" ]]; then
    log_error "This script requires Apple Silicon (macOS arm64)."
    exit 1
fi

# Ensure uv is installed
if ! command -v uv &> /dev/null; then
    log_info "uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Add to path for this session
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create virtual environment with Python 3.12 (required for vllm-metal wheels)
if [[ ! -d "$VENV_DIR" ]]; then
    log_info "Creating virtual environment at $VENV_DIR with Python 3.12..."
    uv venv "$VENV_DIR" --python 3.12
fi

# Activate venv for subsequent commands (just for path resolution)
# We will use 'uv pip' with --python flag or just use the venv pip directly if preferred, 
# but uv manages it well.
log_info "Using virtual environment at $VENV_DIR"

# Install vLLM base
log_info "Installing vLLM base version $VLLM_VERSION..."
# We need to download the tarball to get requirements/cpu.txt specifically
# or just install the deps. The official script downloads the tarball. 
# Let's try to install directly if possible to avoid clutter, 
# but vllm often has specific build reqs. 
# sticking to official method of downloading tarball to be safe as per install.sh analysis.
WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT

cd "$WORK_DIR"
log_info "Downloading vLLM source for dependency resolution..."
curl -L -o "vllm-${VLLM_VERSION}.tar.gz" "https://github.com/vllm-project/vllm/releases/download/v${VLLM_VERSION}/vllm-${VLLM_VERSION}.tar.gz"
tar -xzf "vllm-${VLLM_VERSION}.tar.gz"
cd "vllm-${VLLM_VERSION}"

log_info "Installing dependencies..."
# Use uv pip install for speed
uv pip install --python "$VENV_PATH" -r requirements/cpu.txt
# Install vllm itself
uv pip install --python "$VENV_PATH" .

cd "$PROJECT_ROOT"

# Fetch and install vllm-metal
log_info "Fetching latest vllm-metal release..."
RELEASE_DATA=$(curl -fsSL "https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/releases/latest")
WHEEL_URL=$(echo "$RELEASE_DATA" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for asset in data.get('assets', []):
    if asset['name'].endswith('.whl'):
        print(asset['browser_download_url'])
        break
")

if [[ -z "$WHEEL_URL" ]]; then
    log_error "Could not find a .whl file in the latest release."
    exit 1
fi

log_info "Downloading and installing vllm-metal from $WHEEL_URL..."
uv pip install --python "$VENV_DIR" --upgrade "$WHEEL_URL"

log_info "Setup complete! Activate with: source $VENV_DIR/bin/activate"
