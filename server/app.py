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

# OpenOps Incident Commander - FastAPI Server + Demo UI

from fastapi.responses import HTMLResponse
from inference import run_task

# OpenEnv imports (do not change)
try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:
    raise ImportError(
        "openenv is required. Install dependencies with: uv sync"
    ) from e

try:
    from server.models import IncidentAction, IncidentObservation
    from server.my_env_environment import MyEnvEnvironment
except ModuleNotFoundError:
    from models import IncidentAction, IncidentObservation
    from server.my_env_environment import MyEnvEnvironment


# =========================================================
# CREATE OPENENV API (Hackathon requirement)
# =========================================================
app = create_app(
    MyEnvEnvironment,
    IncidentAction,
    IncidentObservation,
    env_name="my_env",
    max_concurrent_envs=1,
)

# =========================================================
# AGENT EXECUTION ENDPOINT (Hackathon demo endpoint)
# =========================================================
@app.get("/run-task/{task_id}")
def run_task_api(task_id: int):
    """
    Runs the autonomous incident agent.
    Used by the demo UI.
    """
    return run_task(task_id)


# =========================================================
# HOMEPAGE DEMO UI (What judges will see)
# =========================================================
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>OpenOps Incident Commander</title>
        <style>
            body {
                font-family: Arial;
                background:#0b1220;
                color:white;
                text-align:center;
                padding-top:60px;
            }
            .box{
                background:#111a2e;
                width:650px;
                margin:auto;
                padding:35px;
                border-radius:15px;
                box-shadow:0 0 25px rgba(0,0,0,0.5);
            }
            button{
                padding:14px 22px;
                margin:10px;
                font-size:16px;
                border:none;
                border-radius:8px;
                background:#4CAF50;
                color:white;
                cursor:pointer;
            }
            button:hover{background:#45a049;}
            pre{
                text-align:left;
                background:#000;
                padding:15px;
                border-radius:10px;
                max-height:300px;
                overflow:auto;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>🚨 OpenOps Incident Commander</h1>
            <p>Autonomous SRE Agent – Hackathon Demo</p>

            <button onclick="runTask(1)">Run Task 1 (API Crash)</button>
            <button onclick="runTask(2)">Run Task 2 (DB Failure)</button>
            <button onclick="runTask(3)">Run Task 3 (Memory Leak)</button>

            <h3>Agent Output</h3>
            <pre id="output">Click a task to run...</pre>
        </div>

        <script>
            async function runTask(task){
                document.getElementById("output").textContent="Running agent...";
                const res = await fetch("/run-task/" + task);
                const data = await res.json();
                document.getElementById("output").textContent =
                    JSON.stringify(data, null, 2);
            }
        </script>
    </body>
    </html>
    """