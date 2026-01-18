#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path
from model_defs import MODELS

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
SERVICES_DIR = PROJECT_ROOT / "services"

def get_service_status(label):
    try:
        # Check launchctl list
        output = subprocess.check_output(f"launchctl list | grep {label} || true", shell=True).decode().strip()
        if not output:
            return "STOPPED", "-"
        
        parts = output.split()
        pid = parts[0]
        if pid == "-":
            return "STOPPED", "-"
        return "RUNNING", pid
    except:
        return "ERROR", "?"

def get_process_rss(pid):
    if pid == "-" or pid == "?":
        return "-"
    try:
        # The PID might be the bash wrapper. We want the python child (vLLM)
        # Check if current process is bash/sh
        cmd = subprocess.check_output(f"ps -p {pid} -o comm=", shell=True).decode().strip()
        target_pid = pid
        
        if "bash" in cmd or "sh" in cmd:
            # Find child
            try:
                children = subprocess.check_output(f"pgrep -P {pid}", shell=True).decode().split()
                if children:
                    # Assume the last child or the one consuming most memory
                    # For simplicity, take the last one (usually the python command in our script)
                    target_pid = children[-1]
            except subprocess.CalledProcessError:
                pass # No children found

        # Get RSS in KB
        output = subprocess.check_output(f"ps -p {target_pid} -o rss=", shell=True).decode().strip()
        if not output:
            return "-"
        rss_kb = int(output)
        
        # Convert to GB or MB
        if rss_kb > 1024 * 1024:
            return f"{rss_kb / (1024 * 1024):.1f} GB"
        else:
            return f"{rss_kb / 1024:.0f} MB"
    except:
        return "-"

def is_downloaded(repo_id):
    safe_name = repo_id.replace("/", "_")
    model_path = MODELS_DIR / safe_name
    # Check if directory exists and has config.json (heuristic)
    if model_path.exists() and (model_path / "config.json").exists():
        return "YES"
    return "NO"

def main():
    print(f"{'MODEL':<15} {'STATUS':<10} {'PORT':<6} {'RAM (Act/Est)':<20} {'PARAMS':<8} {'DOWNLOADED':<10}")
    print("-" * 80)
    
    # Sort models by name
    for name in sorted(MODELS.keys()):
        config = MODELS[name]
        label = f"com.jowest.vllm.{name}"
        
        status, pid = get_service_status(label)
        
        # Get actual RAM if running
        actual_ram = get_process_rss(pid)
        est_ram = config.get("est_ram", "?")
        ram_display = f"{actual_ram} / {est_ram}"
        
        # Check download status
        downloaded = is_downloaded(config["repo_id"])
        
        port = config["port"]
        params = config.get("params", "-")
        
        # Colorize status (if supported, but let's stick to plain text for now or simple ascii)
        # If running, maybe add *? No, user wants simple.
        
        print(f"{name:<15} {status:<10} {port:<6} {ram_display:<20} {params:<8} {downloaded:<10}")

    # Also show router?
    router_label = "com.jowest.vllm.router"
    r_status, r_pid = get_service_status(router_label)
    r_ram = get_process_rss(r_pid)
    print(f"{'router':<15} {r_status:<10} {'8000':<6} {f'{r_ram} / <100MB':<20} {'-':<8} {'YES':<10}")


if __name__ == "__main__":
    main()
