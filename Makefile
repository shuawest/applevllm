SHELL := /bin/bash

# Configuration
VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python
HF_CACHE := $(HOME)/.cache/huggingface

.PHONY: all setup test install start stop status clean help

all: setup

help:
	@echo "vLLM on Apple Silicon - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  make setup      - Install uv and create virtual environment with vLLM"
	@echo "  make install    - Generate LaunchAgent plists and install services"
	@echo "  make test       - Run pytest tests"
	@echo "  make start      - Start all vLLM services (via vllm-ctl)"
	@echo "  make stop       - Stop all vLLM services (via vllm-ctl)"
	@echo "  make status     - Show status of all services"
	@echo "  make clean      - Remove virtual environment"
	@echo ""
	@echo "For model management, use: ./vllm-ctl <command>"

setup:
	@echo "Setting up vLLM environment..."
	@chmod +x scripts/setup_env.sh
	@./scripts/setup_env.sh

install:
	@echo "Installing LaunchAgent services..."
	@./vllm-ctl install

start:
	@echo "Starting router service..."
	@./vllm-ctl start router

stop:
	@echo "Stopping all services..."
	@./vllm-ctl stop-all

status:
	@./vllm-ctl status

test:
	@echo "Running tests..."
	@source $(VENV_DIR)/bin/activate && uv pip install pytest && python -m pytest tests/

clean:
	@echo "Cleaning up..."
	@rm -rf $(VENV_DIR)
	@echo "Clean complete."
