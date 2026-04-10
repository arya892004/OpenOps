# Copyright (c) Meta Platforms, Inc.

"""
Pydantic models for OpenOps Incident Commander Environment
Submission-safe version
"""

from openenv.core.env_server import Action, Observation, State
from pydantic import Field
from typing import Dict, List, Optional


# =========================================================
# ACTION MODEL
# =========================================================

class IncidentAction(Action):
    """
    Actions available to the incident commander.
    """

    action_id: int = Field(
        default=0,
        description="Action index (0-20)"
    )

    task_id: int = Field(
        default=1,
        description="Task difficulty (1=easy, 2=medium, 3=hard)"
    )


# =========================================================
# OBSERVATION MODEL
# =========================================================

class IncidentObservation(Observation):
    """
    What the agent observes about the incident.
    """

    active_alerts: List[str]
    service_status: Dict[str, str]
    recent_logs: Dict[str, List[str]]

    metrics_summary: Dict[str, float]
    customer_complaints: int
    time_elapsed: int
    revenue_loss: float

    teams_notified: bool
    status_page_updated: bool
    user_communication_sent: bool


# =========================================================
# STATE MODEL (FULL INTERNAL STATE)
# =========================================================

class IncidentState(State):
    """
    Full internal state of the environment.
    """

    task_id: int
    incident_active: bool
    incident_resolved: bool

    # 🔥 CRITICAL FIX — must allow None during reset
    root_cause: Optional[str] = None

    services: Dict
    steps_taken: int
    total_reward: float