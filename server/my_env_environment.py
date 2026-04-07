# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
My Env Environment Implementation.

A simple test environment that echoes back messages sent to it.
Perfect for testing HTTP server infrastructure.
"""

"""
OpenOps: Production Incident Commander Environment

This environment simulates real-world production incidents where an AI agent
must act as an Incident Commander to investigate, mitigate, and resolve outages.
"""

from models import IncidentAction, IncidentObservation, IncidentState
from typing import Dict, List, Tuple


class MyEnvEnvironment:
    """
    Production incident management environment.
    
    The agent must:
    1. Investigate alerts and logs
    2. Identify root causes
    3. Execute correct mitigation actions
    4. Communicate with stakeholders
    5. Resolve incidents quickly to minimize revenue loss
    """
    
    # Map action IDs to human-readable names
    ACTION_NAMES = {
        0: "read_alerts",
        1: "inspect_logs_api",
        2: "inspect_logs_database",
        3: "inspect_logs_auth",
        4: "inspect_logs_frontend",
        5: "check_metrics_api",
        6: "check_metrics_database",
        7: "check_metrics_auth",
        8: "check_metrics_frontend",
        9: "restart_api",
        10: "restart_database",
        11: "restart_auth",
        12: "restart_frontend",
        13: "rollback_api",
        14: "rollback_database",
        15: "scale_api",
        16: "scale_database",
        17: "notify_team",
        18: "update_status_page",
        19: "send_user_communication",
        20: "resolve_incident"
    }
    
    def __init__(self):
        """Initialize environment."""
        self._reset_internal_state()
    
    def reset(self, **kwargs) -> IncidentObservation:
        """
        Reset environment to initial state.
        
        Args:
            **kwargs: Can include 'task_id' to select difficulty
        
        Returns:
            Initial observation
        """
        task_id = kwargs.get('task_id', 1)
        self.task_id = max(1, min(3, task_id))  # Clamp to 1-3
        
        self._reset_internal_state()
        self._init_task_scenario()
        
        return self._get_observation()
    
    def step(self, action: IncidentAction) -> IncidentObservation:
        """
        Execute one action in the environment.
        
        Args:
            action: The action to execute
            
        Returns:
            Observation with reward and done status
        """
        self.time_elapsed += 1
        reward = -0.05  # Time penalty creates urgency
        
        # Revenue loss and customer complaints increase over time
        self.revenue_loss += 500 + (100 * self.time_elapsed)
        if self.incident_active:
            self.customer_complaints += 5 + self.time_elapsed
        
        action_id = action.action_id
        
        # Process the action
        if action_id == 0:
            reward += self._action_read_alerts()
        elif 1 <= action_id <= 4:
            service = ["api", "database", "auth", "frontend"][action_id - 1]
            reward += self._action_inspect_logs(service)
        elif 5 <= action_id <= 8:
            service = ["api", "database", "auth", "frontend"][action_id - 5]
            reward += self._action_check_metrics(service)
        elif 9 <= action_id <= 12:
            service = ["api", "database", "auth", "frontend"][action_id - 9]
            reward += self._action_restart(service)
        elif action_id == 13:
            reward += self._action_rollback("api")
        elif action_id == 14:
            reward += self._action_rollback("database")
        elif action_id == 15:
            reward += self._action_scale("api")
        elif action_id == 16:
            reward += self._action_scale("database")
        elif action_id == 17:
            reward += self._action_notify_team()
        elif action_id == 18:
            reward += self._action_update_status()
        elif action_id == 19:
            reward += self._action_user_communication()
        elif action_id == 20:
            resolve_reward = self._action_resolve()
            reward += resolve_reward
        else:
            reward = -0.3  # Invalid action
        
        self.total_reward += reward
        
        # Build observation
        obs = self._get_observation()
        obs.reward = reward
        obs.done = (action_id == 20) or (self.time_elapsed >= 30)
        
        return obs
    
    @property
    def state(self) -> IncidentState:
        """Return complete environment state."""
        return IncidentState(
            task_id=self.task_id,
            incident_active=self.incident_active,
            incident_resolved=self.incident_resolved,
            root_cause=self.root_cause,
            services=self.services,
            steps_taken=self.time_elapsed,
            total_reward=self.total_reward
        )
    
    # ========== INTERNAL METHODS ==========
    
    def _reset_internal_state(self):
        """Reset all internal variables."""
        self.task_id = 1
        
        # Service health states (hidden from agent initially)
        self.services = {
            "api": {"status": "healthy", "load": 0.5, "error_rate": 0.01},
            "database": {"status": "healthy", "load": 0.3, "error_rate": 0.00},
            "auth": {"status": "healthy", "load": 0.2, "error_rate": 0.00},
            "frontend": {"status": "healthy", "load": 0.4, "error_rate": 0.01}
        }
        
        # Incident state
        self.incident_active = True
        self.incident_resolved = False
        self.root_cause = None
        self.time_elapsed = 0
        self.revenue_loss = 0.0
        self.customer_complaints = 0
        
        # Agent action tracking
        self.investigations = []
        self.mitigations = []
        self.communications = []
        
        # Communication flags
        self.teams_notified = False
        self.status_page_updated = False
        self.user_communication_sent = False
        
        # Observability
        self.logs = {
            "api": [],
            "database": [],
            "auth": [],
            "frontend": []
        }
        self.alerts = []
        self.logs_inspected = set()
        self.metrics_checked = set()
        self.alerts_read = False
        
        # Scoring
        self.total_reward = 0.0
        self.correct_solution = []
    
    def _init_task_scenario(self):
        """Initialize task-specific incident scenario."""
        if self.task_id == 1:
            # === TASK 1: Simple API Crash (Easy) ===
            self.root_cause = "api_crash"
            self.services["api"]["status"] = "down"
            self.services["api"]["error_rate"] = 1.0
            self.services["frontend"]["status"] = "degraded"
            
            self.alerts = [
                "CRITICAL: API service not responding",
                "WARNING: Frontend experiencing errors"
            ]
            self.logs["api"] = [
                "ERROR: Out of memory exception",
                "ERROR: Service crashed at 14:23:15",
                "FATAL: Cannot allocate memory"
            ]
            self.logs["frontend"] = [
                "WARNING: Cannot reach API service",
                "ERROR: Request timeout to API"
            ]
            
            self.correct_solution = ["inspect_logs_api", "restart_api"]
            
        elif self.task_id == 2:
            # === TASK 2: Bad Deployment (Medium) ===
            self.root_cause = "bad_deployment"
            self.services["database"]["status"] = "degraded"
            self.services["database"]["error_rate"] = 0.25
            self.services["api"]["status"] = "degraded"
            
            self.alerts = [
                "CRITICAL: Database query failures (25%)",
                "WARNING: Recent deployment v2.3 to database",
                "WARNING: API experiencing database timeouts"
            ]
            self.logs["database"] = [
                "ERROR: SQL syntax error - new query incompatible",
                "ERROR: Migration script failed on table users",
                "INFO: Deployment v2.3 completed 5 minutes ago"
            ]
            self.logs["api"] = [
                "ERROR: Database connection timeout",
                "WARNING: Retry attempts exhausted"
            ]
            
            self.correct_solution = ["inspect_logs_database", "rollback_database", "notify_team"]
            
        elif self.task_id == 3:
            # === TASK 3: Cascading Failure (Hard) ===
            self.root_cause = "database_overload_cascade"
            self.services["database"]["status"] = "slow"
            self.services["database"]["load"] = 0.95
            self.services["database"]["error_rate"] = 0.10
            self.services["api"]["status"] = "degraded"
            self.services["api"]["error_rate"] = 0.40
            self.customer_complaints = 150
            
            self.alerts = [
                "CRITICAL: Database CPU at 95%",
                "CRITICAL: API timeout rate 40%",
                "WARNING: Customer complaints spiking",
                "WARNING: Queue backlog increasing"
            ]
            self.logs["database"] = [
                "WARNING: Connection pool exhausted (500/500)",
                "WARNING: Slow query detected - avg 2.5s",
                "ERROR: Lock wait timeout exceeded",
                "INFO: Abnormal traffic pattern detected"
            ]
            self.logs["api"] = [
                "ERROR: Database timeout after 30s",
                "WARNING: Request queue backing up (10000 pending)",
                "ERROR: Circuit breaker triggered for database"
            ]
            
            self.correct_solution = [
                "inspect_logs_database",
                "scale_database",
                "inspect_logs_api",
                "restart_api",
                "notify_team",
                "update_status_page"
            ]
    
    def _get_observation(self) -> IncidentObservation:
        """Build the observation that the agent sees."""
        # Agent only sees service status for services they've checked
        service_status = {}
        for service in self.services:
            if service in self.metrics_checked or service in self.logs_inspected:
                service_status[service] = self.services[service]["status"]
            else:
                service_status[service] = "unknown"
        
        # Agent only sees logs for services they've inspected
        visible_logs = {}
        for service in self.services:
            if service in self.logs_inspected:
                visible_logs[service] = self.logs[service]
            else:
                visible_logs[service] = []
        
        return IncidentObservation(
            done=False,
            reward=0.0,
            active_alerts=self.alerts if self.alerts_read else ["[Call read_alerts to see alerts]"],
            service_status=service_status,
            recent_logs=visible_logs,
            metrics_summary={
                "total_requests": 10000 - (self.time_elapsed * 100),
                "avg_error_rate": sum(s["error_rate"] for s in self.services.values()) / 4,
                "avg_latency_ms": 100 + (self.time_elapsed * 50)
            },
            customer_complaints=self.customer_complaints,
            time_elapsed=self.time_elapsed,
            revenue_loss=self.revenue_loss,
            teams_notified=self.teams_notified,
            status_page_updated=self.status_page_updated,
            user_communication_sent=self.user_communication_sent
        )
    
    # ========== ACTION HANDLERS ==========
    
    def _action_read_alerts(self) -> float:
        """Read system alerts."""
        if self.alerts_read:
            return 0.0
        self.alerts_read = True
        self.investigations.append("read_alerts")
        return 0.1
    
    def _action_inspect_logs(self, service: str) -> float:
        """Inspect logs for a specific service."""
        if service in self.logs_inspected:
            return 0.0
        
        self.logs_inspected.add(service)
        self.investigations.append(f"inspect_logs_{service}")
        
        # Reward if investigating root cause service
        if self._is_root_cause_service(service):
            return 0.3
        return 0.05
    
    def _action_check_metrics(self, service: str) -> float:
        """Check metrics for a service."""
        if service in self.metrics_checked:
            return 0.0
        
        self.metrics_checked.add(service)
        self.investigations.append(f"check_metrics_{service}")
        
        if self._is_root_cause_service(service):
            return 0.2
        return 0.05
    
    def _action_restart(self, service: str) -> float:
        """Restart a service."""
        self.mitigations.append(f"restart_{service}")
        
        if f"restart_{service}" in self.correct_solution:
            self.services[service]["status"] = "healthy"
            self.services[service]["error_rate"] = 0.01
            return 0.8
        return -0.4  # Wrong service restart
    
    def _action_rollback(self, service: str) -> float:
        """Rollback a deployment."""
        self.mitigations.append(f"rollback_{service}")
        
        if f"rollback_{service}" in self.correct_solution:
            self.services[service]["status"] = "healthy"
            self.services[service]["error_rate"] = 0.00
            return 1.0
        return -0.5
    
    def _action_scale(self, service: str) -> float:
        """Scale up a service."""
        self.mitigations.append(f"scale_{service}")
        
        if f"scale_{service}" in self.correct_solution:
            self.services[service]["load"] = 0.5
            self.services[service]["status"] = "healthy"
            return 0.8
        return -0.3
    
    def _action_notify_team(self) -> float:
        """Notify engineering team."""
        if self.teams_notified:
            return 0.0
        
        self.teams_notified = True
        self.communications.append("notify_team")
        
        if "notify_team" in self.correct_solution:
            return 0.3
        return 0.1
    
    def _action_update_status(self) -> float:
        """Update public status page."""
        if self.status_page_updated:
            return 0.0
        
        self.status_page_updated = True
        self.communications.append("update_status_page")
        
        if "update_status_page" in self.correct_solution:
            return 0.3
        return 0.1
    
    def _action_user_communication(self) -> float:
        """Send user communication."""
        if self.user_communication_sent:
            return 0.0
        
        self.user_communication_sent = True
        self.communications.append("send_user_communication")
        return 0.1
    
    def _action_resolve(self) -> float:
        """Attempt to resolve incident."""
        if self._check_incident_resolved():
            self.incident_resolved = True
            self.incident_active = False
            
            # Big reward + time bonus
            base_reward = 3.0
            time_bonus = max(0, (30 - self.time_elapsed) * 0.1)
            return base_reward + time_bonus
        else:
            # Premature resolution
            return -1.5
    
    # ========== HELPER METHODS ==========
    
    def _is_root_cause_service(self, service: str) -> bool:
        """Check if service is related to root cause."""
        if self.task_id == 1:
            return service == "api"
        elif self.task_id == 2:
            return service == "database"
        elif self.task_id == 3:
            return service in ["database", "api"]
        return False
    
    def _check_incident_resolved(self) -> bool:
        """Check if incident is actually resolved."""
        if self.task_id == 1:
            return self.services["api"]["status"] == "healthy"
        elif self.task_id == 2:
            return self.services["database"]["status"] == "healthy"
        elif self.task_id == 3:
            return (
                self.services["database"]["load"] < 0.7 and
                self.services["api"]["status"] == "healthy"
            )
        return False