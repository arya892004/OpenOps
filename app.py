# Copyright (c) Meta Platforms, Inc.
"""
OpenOps Incident Commander — FastAPI Server Entry Point

OpenEnv's create_app() auto-generates these endpoints:
  GET  /health     → liveness check
  POST /reset      → start new episode
  POST /step       → take action
  GET  /state      → current internal state
"""

# Dual-import pattern (REQUIRED by OpenEnv)
try:
    from ..models import IncidentAction, IncidentObservation
except ImportError:
    from models import IncidentAction, IncidentObservation

try:
    from .my_env_environment import MyEnvEnvironment
except ImportError:
    from server.my_env_environment import MyEnvEnvironment

from openenv.core.env_server import create_app

# ✅ Pass the CLASS (not an instance) — create_app handles instantiation
app = create_app(
    MyEnvEnvironment,       # environment class
    IncidentAction,         # action type
    IncidentObservation,    # observation type
    env_name="openops-incident-commander",
)