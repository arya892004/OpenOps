# Copyright (c) Meta Platforms, Inc.
"""
Pydantic models for OpenOps Incident Commander Environment
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any
from openenv.core.env_server import Action, Observation, State


# =========================================================
# ACTION MODEL
# =========================================================

@dataclass
class IncidentAction(Action):
    """
    Actions available to the incident commander.
    action_id reference:
      0  = investigate logs
      1  = notify on-call team
      2  = update status page
      3  = rollback last deploy
      4  = restart service
      5  = scale up replicas
      6  = flush cache
      7  = enable circuit breaker
      8  = send customer comms
      9  = escalate to senior engineer
      10 = confirm resolution & close incident
    """
    action_id: int = 0
    task_id: int = 1   # 1=easy, 2=medium, 3=hard


# =========================================================
# OBSERVATION MODEL
# =========================================================

@dataclass
class IncidentObservation(Observation):
    """
    What the agent observes about the incident.
    NOTE: reward and done are inherited from Observation base class.
    """
    active_alerts: List[str] = field(default_factory=list)
    service_status: Dict[str, str] = field(default_factory=dict)
    recent_logs: Dict[str, List[str]] = field(default_factory=dict)
    metrics_summary: Dict[str, float] = field(default_factory=dict)
    customer_complaints: int = 0
    time_elapsed: int = 0
    revenue_loss: float = 0.0
    teams_notified: bool = False
    status_page_updated: bool = False
    user_communication_sent: bool = False


# =========================================================
# STATE MODEL (FULL INTERNAL STATE)
# =========================================================

@dataclass
class IncidentState(State):
    """
    Full internal state of the environment.
    """
    task_id: int = 1
    incident_active: bool = True
    incident_resolved: bool = False
    root_cause: Optional[str] = None
    services: Dict = field(default_factory=lambda: {
        "database": "down",
        "api": "degraded",
        "frontend": "ok",
        "cache": "ok"
    })
    steps_taken: int = 0
    total_reward: float = 0.0
    teams_notified: bool = False
    status_page_updated: bool = False
    user_communication_sent: bool = False