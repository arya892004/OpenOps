# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
FastAPI application for the My Env Environment.

This module creates an HTTP server that exposes the MyEnvironment
over HTTP and WebSocket endpoints, compatible with EnvClient.

Endpoints:
    - POST /reset: Reset the environment
    - POST /step: Execute an action
    - GET /state: Get current environment state
    - GET /schema: Get action/observation schemas
    - WS /ws: WebSocket endpoint for persistent sessions

Usage:
    # Development (with auto-reload):
    uvicorn server.app:app --reload --host 0.0.0.0 --port 8000

    # Production:
    uvicorn server.app:app --host 0.0.0.0 --port 8000 --workers 4

    # Or run directly:
    python -m server.app
"""

from server.my_env_environment import MyEnvEnvironment
import requests
from fastapi import FastAPI
import gradio as gr

# OpenEnv server creator
try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:
    raise ImportError(
        "openenv is required. Install with:\n\n    uv sync\n"
    ) from e

# Local imports (supports both docker + local run)
try:
    from server.models import IncidentAction, IncidentObservation
    from server.my_env_environment import MyEnvEnvironment
except ModuleNotFoundError:
    from models import IncidentAction, IncidentObservation
    from my_env_environment import MyEnvEnvironment


# ---------------------------------------------------
# Create OpenEnv FastAPI App
# ---------------------------------------------------

app: FastAPI = create_app(
    MyEnvEnvironment,
    IncidentAction,
    IncidentObservation,
    env_name="my_env",
    max_concurrent_envs=1,
)


# ---------------------------------------------------
# Root Route (kept simple for submission health check)
# ---------------------------------------------------

@app.get("/")
def home():
    return {
        "project": "OpenOps Incident Commander",
        "status": "running",
        "openenv_endpoints": [
            "/reset",
            "/step",
            "/state",
            "/schema",
            "/ws",
        ],
        "gradio_ui": "/ui"
    }


# ===================================================
#                GRADIO UI SECTION
# ===================================================
# 


def call_reset():
    try:
        r = requests.post("http://localhost:8000/reset", timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def call_step(action_text):
    try:
        r = requests.post(
            "http://localhost:8000/step",
            json={"action": action_text},
            timeout=15,
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def gradio_reset():
    return call_reset()


def gradio_step(action):
    return call_step(action)


with gr.Blocks(title="OpenOps Incident Commander") as demo:
    gr.Markdown("# 🚨 OpenOps Incident Commander")
    gr.Markdown("Interact with your OpenEnv agent visually")

    with gr.Row():
        reset_btn = gr.Button("🔄 Reset Environment")

    reset_output = gr.JSON(label="Reset Response")

    reset_btn.click(fn=gradio_reset, outputs=reset_output)

    gr.Markdown("## ▶️ Send Action")

    action_input = gr.Textbox(
        label="Action",
        placeholder="Type an action for the agent...",
    )

    step_btn = gr.Button("Run Step")
    step_output = gr.JSON(label="Step Response")

    step_btn.click(
        fn=gradio_step,
        inputs=action_input,
        outputs=step_output,
    )


# 🔥 Mount Gradio safely at /ui
app = gr.mount_gradio_app(app, demo, path="/ui")


# ---------------------------------------------------
# Run via python -m server.app
# ---------------------------------------------------

def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    main(port=args.port)