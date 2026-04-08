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

# Copyright (c) Meta Platforms, Inc.

from fastapi import FastAPI
import gradio as gr

try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:
    raise ImportError("openenv is required. Run: uv sync") from e

try:
    from server.models import IncidentAction, IncidentObservation
    from server.my_env_environment import MyEnvEnvironment
except ModuleNotFoundError:
    from models import IncidentAction, IncidentObservation
    from my_env_environment import MyEnvEnvironment


# =========================================================
# 1️⃣ Create OpenEnv API (THIS MUST BE ROOT)
# =========================================================

app = create_app(
    MyEnvEnvironment,
    IncidentAction,
    IncidentObservation,
    env_name="my_env",
    max_concurrent_envs=1,
)

# =========================================================
# 2️⃣ Root info page (HF Space landing)
# =========================================================

@app.get("/")
def root():
    return {
        "message": "OpenOps Incident Commander API",
        "ui": "/ui",
        "docs": "/docs",
        "health": "ok"
    }

# =========================================================
# 3️⃣ Gradio UI
# =========================================================

def run_demo(action_id, task_id):
    return f"Action {action_id} submitted for task {task_id}"

demo = gr.Interface(
    fn=run_demo,
    inputs=[
        gr.Slider(0, 20, step=1, label="Action ID"),
        gr.Slider(1, 3, step=1, label="Task ID"),
    ],
    outputs="text",
    title="🚨 OpenOps Incident Commander",
    description="Test the environment manually",
)

# 🔥 IMPORTANT — mount on /ui NOT /
app = gr.mount_gradio_app(app, demo, path="/ui")

# =========================================================
# Local run
# =========================================================

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()

