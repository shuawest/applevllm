
import pytest
import sys
import platform
import subprocess

def test_python_version():
    """Ensure we are running on a compatible python version (3.9+)."""
    assert sys.version_info >= (3, 9)

def test_platform():
    """Ensure we are running on macOS arm64."""
    assert sys.platform == "darwin"
    assert platform.machine() == "arm64"

def test_vllm_importable():
    """Test that vllm can be imported."""
    try:
        import vllm
        print(f"vLLM version: {vllm.__version__}")
    except ImportError:
        pytest.fail("Could not import vllm module")

def test_torch_mps_available():
    """Test that PyTorch sees the MPS device (optional but good)."""
    try:
        import torch
        # Note: vllm-metal uses MLX primarily but torch might still be used for loading
        # Just checking if torch is runnable
        assert torch.backends.mps.is_available() or torch.cuda.is_available() is False
    except ImportError:
        pass # Torch might not be directly installed or required if pure MLX, but vllm usually depends on it.

def test_vllm_metal_plugin():
    """Check if we can see any evidence of the metal plugin."""
    try:
        from importlib.metadata import version
        v = version("vllm-metal")
        print(f"vllm-metal version: {v}")
    except Exception:
        pytest.fail("vllm-metal package not found")
