#!/usr/bin/env python3
import uvicorn
import httpx
import asyncio
import subprocess
import os
import signal
import sys
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from contextlib import asynccontextmanager
from pathlib import Path
from model_defs import MODELS

# Configuration
LITELLM_PORT = 8080
ROUTER_PORT = 8000
LITELLM_HOST = "http://localhost"
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Global state for the subprocess
litellm_process = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global litellm_process
    print(f"Starting LiteLLM on port {LITELLM_PORT}...")
    
    # Ensure config exists
    config_path = PROJECT_ROOT / "router_config.yaml"
    if not config_path.exists():
        # Fallback generation? Or assume it exists.
        # Ideally we run generate_router_config.py first.
        subprocess.check_call([sys.executable, str(PROJECT_ROOT / "scripts/generate_router_config.py")])

    # Start LiteLLM
    cmd = [
        "litellm",
        "--config", str(config_path),
        "--port", str(LITELLM_PORT)
    ]
    
    # Use same environment
    env = os.environ.copy()
    
    litellm_process = subprocess.Popen(cmd, env=env)
    
    # wait a bit for it to start?
    await asyncio.sleep(2)
    
    yield
    
    # Shutdown
    print("Shutting down LiteLLM...")
    if litellm_process:
        litellm_process.terminate()
        try:
            litellm_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            litellm_process.kill()

app = FastAPI(lifespan=lifespan)
client = httpx.AsyncClient()

# Middleware to fix malformed Authorization headers BEFORE FastAPI sees them
@app.middleware("http")
async def fix_auth_header_middleware(request: Request, call_next):
    # Get the scope (ASGI spec)
    scope = request.scope
    
    # Filter headers at ASGI level
    if "headers" in scope:
        cleaned_headers = []
        for header_name, header_value in scope["headers"]:
            # Decode header name and value
            name = header_name.decode("latin1").lower()
            value = header_value.decode("latin1")
            
            # Skip malformed Authorization headers
            if name == "authorization":
                # Skip if empty or just "Bearer " with no token
                value_stripped = value.strip()
                if not value_stripped or value_stripped == "Bearer" or (value_stripped.startswith("Bearer ") and not value_stripped[7:].strip()):
                    continue
            
            # Keep all other headers
            cleaned_headers.append((header_name, header_value))
        
        scope["headers"] = cleaned_headers
    
    response = await call_next(request)
    return response

@app.get("/v1/models")
async def get_models():
    """Aggregates models from all running vLLM services."""
    tasks = []
    active_models = []
    
    async def fetch_model(name, config):
        port = config["port"]
        url = f"http://localhost:{port}/v1/models"
        try:
            resp = await client.get(url, timeout=0.5)
            if resp.status_code == 200:
                data = resp.json()
                # vLLM returns {"object": "list", "data": [...]}
                # We want to extract the model info and maybe enrich it
                for model in data.get("data", []):
                    # Override ID to match our service name if needed
                    # vLLM returns the full path usually.
                    # We want to return the service name (e.g. 'yi-1.5') so it matches what router expects?
                    # LiteLLM router expects 'yi-1.5'.
                    # But the User might want to see the real details.
                    # Let's just return what vLLM returns, but maybe alias the ID to the simple name 
                    # OR return both.
                    # Standard OpenAI client uses 'id' to call the model.
                    # If we return 'models/mlx-community...', the user has to use that?
                    # No, LiteLLM routes based on 'yi-1.5'.
                    # So we MUST return 'id': 'yi-1.5'.
                    
                    # Create a new entry
                    new_entry = model.copy()
                    new_entry["id"] = name # Force the friendly name
                    new_entry["backend_model"] = model["id"] # Keep original
                    new_entry["port"] = port
                    
                    # Add extra metadata from our defs
                    if "est_ram" in config:
                        new_entry["est_ram"] = config["est_ram"]
                    if "params" in config:
                        new_entry["params"] = config["params"]
                        
                    return new_entry
        except Exception:
            return None

    for name, config in MODELS.items():
        tasks.append(fetch_model(name, config))
        
    results = await asyncio.gather(*tasks)
    
    # Filter None
    data = [r for r in results if r is not None]
    
    return {
        "object": "list",
        "data": data
    }

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(path_name: str, request: Request):
    """Proxy everything else to LiteLLM."""
    url = f"{LITELLM_HOST}:{LITELLM_PORT}/{path_name}"
    
    # Read body before stream?
    content = await request.body()

    # Forward headers but strip Host and content-length
    # Also filter out malformed Authorization headers (empty or whitespace-only tokens)
    headers = {}
    for k, v in request.headers.items():
        if k.lower() in ("host", "content-length"):
            continue
        
        # Skip Authorization header if it's empty or just "Bearer" with no/empty token
        skip_header = False
        if k.lower() == "authorization":
            # Check if it's "Bearer " with no token or just whitespace
            if not v or not v.strip():
                skip_header = True
            # If it starts with "Bearer ", check if there's actually a token
            elif v.strip().startswith("Bearer "):
                token = v.strip()[7:].strip()  # Get everything after "Bearer "
                if not token:  # Empty token
                    skip_header = True
        
        if not skip_header:
            headers[k] = v
    
    try:
        rp_req = client.build_request(
            request.method,
            url,
            headers=headers,
            content=content,
        )
        
        rp_resp = await client.send(rp_req, stream=True)
        
        return StreamingResponse(
            rp_resp.aiter_bytes(),
            status_code=rp_resp.status_code,
            background=None
        )
    except (ValueError, httpx.InvalidURL) as e:
        # Handle header validation errors (like "Illegal header value")
        error_msg = str(e)
        if "header" in error_msg.lower():
            return JSONResponse({"error": f"Invalid request headers: {error_msg}"}, status_code=400)
        return JSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=502)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=ROUTER_PORT)
