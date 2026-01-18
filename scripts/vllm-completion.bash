#!/bin/bash

_vllm_ctl_complete() {
    local cur prev opts models
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # List of main commands
    opts="install start stop stop-all restart status logs list"
    
    # Get model list dynamically
    # Expects vllm-ctl to be in the path or relative
    # We look for the management script relative to this completion script if needed,
    # or assume vllm-ctl logic. 
    # Best way: assume vllm-ctl is what's being completed.
    
    # Try to find the list-raw command
    # We assume 'vllm-ctl' is in the current directory or path
    # If the user sourced this, they probably are in the repo or added it to path.
    # We can try to call the vllm-ctl command itself if it's the 0th arg.
    
    local cmd="${COMP_WORDS[0]}"
    
    case "${prev}" in
        start|stop|restart|logs)
            # Complete model names
            if [ -x "$cmd" ]; then
                # If ./vllm-ctl is executable
                models=$($cmd list-raw 2>/dev/null)
            else
                # Fallback purely parsing if we can locate the plist dir? 
                # Let's verify if we can run the command.
                # If command is not found/runnable, we can't complete models easily without hardcoding logic.
                # Assuming standard usage: ./vllm-ctl
                 models=$($cmd list-raw 2>/dev/null)
            fi
            
            COMPREPLY=( $(compgen -W "${models}" -- ${cur}) )
            return 0
            ;;
        *)
            ;;
    esac

    # Complete commands if we aren't waiting for a model arg
    # (Simplified: if prev is the command itself)
    if [[ "${prev}" == "${cmd}" ]] || [[ "${prev}" == */vllm-ctl ]]; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi
}

complete -F _vllm_ctl_complete vllm-ctl
