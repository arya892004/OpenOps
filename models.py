# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Data models for the My Env Environment.

The my_env environment is a simple test environment that echoes back messages.
"""


"""
Pydantic models for OpenOps Incident Commander Environment
"""

from openenv.core.env_server import Action, Observation, State
from pydantic import Field
from typing import Dict, List, Optional


class IncidentAction(Action):
    """
    Actions available to the incident commander.
    
    Action IDs:
    0-4: Investigation (read_alerts, inspect_logs_*)
    5-8: Metrics checking
    9-12: Service restarts
    13-14: Rollbacks
    15-16: Scaling
    17-19: Communication
    20: Resolution
    """
    action_id: int = Field(description="Action index (0-20)")
    task_id: int = Field(default=1, description="Task difficulty (1=easy, 2=medium, 3=hard)")


class IncidentObservation(Observation):
    """
    What the agent observes about the incident.
    """
    # Inherited: done (bool), reward (Optional[float])
    
    active_alerts: List[str] = Field(description="Current system alerts")
    service_status: Dict[str, str] = Field(description="Status of each service")
    recent_logs: Dict[str, List[str]] = Field(description="Logs from inspected services")
    
    metrics_summary: Dict[str, float] = Field(description="Aggregated metrics")
    customer_complaints: int = Field(description="Number of angry customers")
    time_elapsed: int = Field(description="Minutes since incident started")
    revenue_loss: float = Field(description="Revenue lost in USD")
    
    teams_notified: bool = Field(description="Has team been alerted?")
    status_page_updated: bool = Field(description="Has status page been updated?")
    user_communication_sent: bool = Field(description="Have users been notified?")


class IncidentState(State):
    """
    Full internal state of the environment (not all visible to agent).
    """
    task_id: int = Field(description="Current task")
    incident_active: bool = Field(description="Is there an ongoing incident?")
    incident_resolved: bool = Field(description="Has it been resolved?")
    root_cause: str = Field(description="What caused the incident")
    
    services: Dict = Field(description="Full service health states")
    steps_taken: int = Field(description="Number of actions executed")
    total_reward: float = Field(description="Cumulative reward")