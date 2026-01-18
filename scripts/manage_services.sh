#!/bin/bash
set -e

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICES_DIR="${PROJECT_ROOT}/services"
LAUNCH_AGENTS_DIR="${HOME}/Library/LaunchAgents"

usage() {
    echo "Usage: $0 {install|start|stop|restart|status|logs} [model_name]"
    echo "Commands:"
    echo "  install       Generate plists and link them to ~/Library/LaunchAgents"
    echo "  start <name>  Start a specific model service"
    echo "  stop <name>   Stop a specific model service"
    echo "  stop-all      Stop all model services"
    echo "  restart <name> Restart a specific model service"
    echo "  status        Show status of all vllm services"
    echo "  logs <name>   Tail logs for a specific model"
    echo "  list          List available models"
    exit 1
}

get_plist_name() {
    local model=$1
    echo "com.jowest.vllm.${model}"
}

ensure_generated() {
    if [ ! -d "$SERVICES_DIR" ] || [ -z "$(ls -A "$SERVICES_DIR")" ]; then
        echo "Generating plist files..."
        python3 "${PROJECT_ROOT}/scripts/generate_plists.py"
    fi
}

cmd_install() {
    ensure_generated
    echo "Installing LaunchAgents..."
    mkdir -p "$LAUNCH_AGENTS_DIR"
    
    for plist in "${SERVICES_DIR}"/*.plist; do
        filename=$(basename "$plist")
        target="${LAUNCH_AGENTS_DIR}/${filename}"
        
        # Symlink if not exists
        if [ ! -L "$target" ]; then
            ln -s "$plist" "$target"
            echo "Linked $filename"
        else
            echo "Already linked: $filename"
        fi
        
        # Bootstrap (register) the service without starting it
        # We assume the user wants to start them manually to save RAM
        launchctl bootout gui/$(id -u)/${filename%.plist} 2>/dev/null || true
        launchctl bootstrap gui/$(id -u) "$target"
    done
    echo "Installation complete. Use '$0 start <model>' to run a model."
}

cmd_start() {
    local model=$1
    [ -z "$model" ] && usage
    
    local label=$(get_plist_name "$model")
    echo "Starting $label..."
    launchctl kickstart -k gui/$(id -u)/$label
    echo "Service started. Check logs with '$0 logs $model'"
}

cmd_stop() {
    local model=$1
    [ -z "$model" ] && usage
    
    local label=$(get_plist_name "$model")
    echo "Stopping $label..."
    launchctl kill SIGTERM gui/$(id -u)/$label
    echo "Service stopped."
}

cmd_restart() {
    cmd_stop "$1" || true
    sleep 2
    cmd_start "$1"
}

cmd_status() {
    # Ensure virtualenv is usable for the python script
    export PYTHONPATH="${PROJECT_ROOT}/scripts:${PYTHONPATH}"
    "${PROJECT_ROOT}/.venv/bin/python" "${PROJECT_ROOT}/scripts/status.py"
}

cmd_logs() {
    local model=$1
    [ -z "$model" ] && usage
    
    local log_file="${HOME}/Library/Logs/vllm/${model}.out.log"
    local err_file="${HOME}/Library/Logs/vllm/${model}.err.log"
    
    echo "Tailing logs for $model (Ctrl+C to exit)..."
    tail -f "$log_file" "$err_file"
}

cmd_list() {
    ensure_generated
    echo "Available Models:"
    for plist in "${SERVICES_DIR}"/*.plist; do
        basename "$plist" | sed 's/com.jowest.vllm.//g' | sed 's/.plist//g'
    done
}

cmd_stop_all() {
    echo "Stopping all services..."
    for plist in "${SERVICES_DIR}"/*.plist; do
        [ -e "$plist" ] || continue
        filename=$(basename "$plist")
        model=$(echo "$filename" | sed 's/com.jowest.vllm.//g' | sed 's/.plist//g')
        # Only stop if running? cmd_stop handles idcmpotency (kickstart -k or bootout?) 
        # Actually cmd_stop does 'launchctl kill SIGTERM'. If not running, it prints error?
        # Let's just call it.
        cmd_stop "$model" || true
    done
}

# Main dispatch
case "$1" in
    install) cmd_install ;;
    start)   cmd_start "$2" ;;
    stop)    cmd_stop "$2" ;;
    stop-all) cmd_stop_all ;;
    restart) cmd_restart "$2" ;;
    status)  cmd_status ;;
    logs)    cmd_logs "$2" ;;
    list)    cmd_list ;;
    list-raw) cmd_list | sed '1d' ;;
    *)       usage ;;
esac
