# Copyright (c) Meta Platforms, Inc.
"""
Pydantic models for OpenOps environment
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class IncidentAction(BaseModel):
    """
    Action taken by the agent.
    
    Represents a single action in the incident management workflow.
    """
    action_id: int = Field(..., ge=0, le=20, description="Action ID (0-20)")
    task_id: int = Field(default=1, ge=1, le=3, description="Task ID (1=easy, 2=medium, 3=hard)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "action_id": 0,
                "task_id": 1
            }
        }


class IncidentObservation(BaseModel):
    """
    Observation returned to agent after each step.
    
    Contains partial information about the system state (investigation reveals more).
    """
    active_alerts: List[str] = Field(
        default_factory=list,
        description="List of active system alerts"
    )
    service_status: Dict[str, str] = Field(
        default_factory=dict,
        description="Status of each service (healthy/degraded/down)"
    )
    recent_logs: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Logs from inspected services only"
    )
    metrics_summary: Dict[str, Dict[str, float]] = Field(
        default_factory=dict,
        description="Metrics for checked services (CPU, memory, latency)"
    )
    customer_complaints: int = Field(
        default=0,
        description="Number of customer complaints received"
    )
    time_elapsed: int = Field(
        default=0,
        description="Minutes since incident started"
    )
    revenue_loss: float = Field(
        default=0.0,
        description="Estimated revenue loss in USD"
    )
    teams_notified: bool = Field(
        default=False,
        description="Whether engineering team has been notified"
    )
    status_page_updated: bool = Field(
        default=False,
        description="Whether public status page has been updated"
    )
    reward: float = Field(
        default=0.0,
        description="Reward received for this step"
    )
    done: bool = Field(
        default=False,
        description="Whether episode is complete"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "active_alerts": ["CRITICAL: API service down"],
                "service_status": {
                    "api": "down",
                    "database": "healthy"
                },
                "recent_logs": {
                    "api": ["ERROR: Out of memory"]
                },
                "customer_complaints": 45,
                "time_elapsed": 5,
                "revenue_loss": 5000.0,
                "teams_notified": False,
                "status_page_updated": False,
                "reward": 0.05,
                "done": False
            }
        }


class IncidentState(BaseModel):
    """
    Internal environment state (hidden from agent).
    
    Contains ground truth about the incident for evaluation.
    """
    task_id: int = Field(..., ge=1, le=3, description="Task difficulty level")
    incident_type: str = Field(..., description="Type of incident")
    affected_services: List[str] = Field(
        default_factory=list,
        description="Services affected by the incident"
    )
    root_cause: str = Field(..., description="Root cause of the incident")
    service_status: Dict[str, str] = Field(
        default_factory=dict,
        description="Current status of all services"
    )
    correct_mitigation: List[str] = Field(
        default_factory=list,
        description="Correct mitigation actions for this incident"
    )
    revenue_loss: float = Field(
        default=0.0,
        description="Accumulated revenue loss"
    )
    customer_complaints: int = Field(
        default=0,
        description="Accumulated customer complaints"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": 1,
                "incident_type": "api_crash",
                "affected_services": ["api"],
                "root_cause": "out_of_memory",
                "service_status": {
                    "api": "down",
                    "database": "healthy",
                    "auth": "healthy",
                    "frontend": "degraded"
                },
                "correct_mitigation": ["restart_api"],
                "revenue_loss": 0.0,
                "customer_complaints": 0
            }
        }