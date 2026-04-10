"""
OpenOps Production Incident Management Environment
Simulates real-world production incidents where agents must investigate, mitigate, and resolve issues
"""

from typing import Dict, List, Any, Optional
from openenv.core import Environment
from models import IncidentAction, IncidentObservation, IncidentState


class MyEnvEnvironment(Environment):
    """
    Production incident management environment.
    
    Simulates 3 types of incidents:
    - Task 1 (Easy): Simple API crash requiring restart
    - Task 2 (Medium): Bad deployment requiring rollback
    - Task 3 (Hard): Cascading database overload requiring multi-step resolution
    """
    
    # Action definitions
    ACTION_NAMES = {
        # Investigation actions (0-8)
        0: "read_alerts",
        1: "inspect_logs_api",
        2: "inspect_logs_database",
        3: "inspect_logs_auth",
        4: "inspect_logs_frontend",
        5: "check_metrics_api",
        6: "check_metrics_database",
        7: "check_metrics_auth",
        8: "check_metrics_frontend",
        
        # Mitigation actions (9-16)
        9: "restart_api",
        10: "restart_database",
        11: "restart_auth",
        12: "restart_frontend",
        13: "rollback_api",
        14: "rollback_database",
        15: "scale_api",
        16: "scale_database",
        
        # Communication actions (17-19)
        17: "notify_team",
        18: "update_status_page",
        19: "send_user_communication",
        
        # Resolution (20)
        20: "resolve_incident"
    }
    
    def __init__(self):
        """Initialize the environment."""
        super().__init__()
        self.task_id = 1
        self.time_elapsed = 0
        self.max_steps = 30
        self.total_reward = 0.0
        
        # State tracking
        self.incident_resolved = False
        self.alerts_read = False
        self.logs_inspected = set()
        self.metrics_checked = set()
        self.services_restarted = set()
        self.services_rolled_back = set()
        self.services_scaled = set()
        self.teams_notified = False
        self.status_page_updated = False
        self.users_communicated = False
        
        # Internal state
        self._state = None
    
    @property
    def state(self) -> IncidentState:
        """
        Return current environment state.
        Required by BaseEnvironment abstract class.
        """
        return self._state
    
    @state.setter
    def state(self, value: IncidentState):
        """Set the environment state."""
        self._state = value
        
    def reset(self, task_id: int = 1) -> IncidentObservation:
        """
        Reset environment for a specific task.
        
        Args:
            task_id: Task difficulty (1=easy, 2=medium, 3=hard)
            
        Returns:
            Initial observation
        """
        self.task_id = task_id
        self.time_elapsed = 0
        self.total_reward = 0.0
        
        # Reset tracking
        self.incident_resolved = False
        self.alerts_read = False
        self.logs_inspected = set()
        self.metrics_checked = set()
        self.services_restarted = set()
        self.services_rolled_back = set()
        self.services_scaled = set()
        self.teams_notified = False
        self.status_page_updated = False
        self.users_communicated = False
        
        # Initialize state based on task
        self._state = self._init_task_state(task_id)
        
        # Return initial observation
        return self._get_observation()
    
    def _init_task_state(self, task_id: int) -> IncidentState:
        """Initialize task-specific state."""
        
        if task_id == 1:
            # Task 1: Simple API crash (OOM)
            return IncidentState(
                task_id=task_id,
                incident_type="api_crash",
                affected_services=["api"],
                root_cause="out_of_memory",
                service_status={
                    "api": "down",
                    "database": "healthy",
                    "auth": "healthy",
                    "frontend": "degraded"
                },
                correct_mitigation=["restart_api"],
                revenue_loss=0.0,
                customer_complaints=0
            )
        
        elif task_id == 2:
            # Task 2: Bad deployment (database)
            return IncidentState(
                task_id=task_id,
                incident_type="bad_deployment",
                affected_services=["database", "api"],
                root_cause="bad_migration",
                service_status={
                    "api": "degraded",
                    "database": "degraded",
                    "auth": "healthy",
                    "frontend": "degraded"
                },
                correct_mitigation=["rollback_database"],
                revenue_loss=0.0,
                customer_complaints=0
            )
        
        else:  # task_id == 3
            # Task 3: Cascading failure (database overload)
            return IncidentState(
                task_id=task_id,
                incident_type="cascading_failure",
                affected_services=["database", "api"],
                root_cause="database_overload",
                service_status={
                    "api": "degraded",
                    "database": "degraded",
                    "auth": "healthy",
                    "frontend": "degraded"
                },
                correct_mitigation=["scale_database", "restart_api"],
                revenue_loss=0.0,
                customer_complaints=0
            )
    
    def step(self, action: IncidentAction) -> IncidentObservation:
        """
        Execute an action and return observation.
        
        Args:
            action: Action to execute
            
        Returns:
            Observation after action execution
        """
        self.time_elapsed += 1
        reward = 0.0
        done = False
        
        # Time penalty
        reward -= 0.05
        
        # Revenue loss increases over time
        self._state.revenue_loss += 1000 * self.time_elapsed
        self._state.customer_complaints += self.time_elapsed // 3
        
        # Execute action
        action_name = self.ACTION_NAMES.get(action.action_id, "unknown")
        
        # Investigation actions
        if action.action_id == 0:  # read_alerts
            if not self.alerts_read:
                self.alerts_read = True
                reward += 0.05
            
        elif 1 <= action.action_id <= 4:  # inspect_logs
            service = ["api", "database", "auth", "frontend"][action.action_id - 1]
            if service not in self.logs_inspected:
                self.logs_inspected.add(service)
                if service in self._state.affected_services:
                    reward += 0.25  # Bonus for inspecting affected service
                else:
                    reward += 0.05
        
        elif 5 <= action.action_id <= 8:  # check_metrics
            service = ["api", "database", "auth", "frontend"][action.action_id - 5]
            if service not in self.metrics_checked:
                self.metrics_checked.add(service)
                reward += 0.05
        
        # Mitigation actions
        elif 9 <= action.action_id <= 12:  # restart services
            service = ["api", "database", "auth", "frontend"][action.action_id - 9]
            if service not in self.services_restarted:
                self.services_restarted.add(service)
                
                # Check if restart is correct mitigation
                if "restart_" + service in self._state.correct_mitigation:
                    reward += 0.75
                    self._state.service_status[service] = "healthy"
                elif service in self._state.affected_services:
                    # Restarting affected service (but not the solution)
                    reward -= 0.5
                else:
                    reward -= 0.1
        
        elif 13 <= action.action_id <= 14:  # rollback (API or Database)
            service = ["api", "database"][action.action_id - 13]
            if service not in self.services_rolled_back:
                self.services_rolled_back.add(service)
                
                # Check if rollback is correct
                if "rollback_" + service in self._state.correct_mitigation:
                    reward += 1.0
                    self._state.service_status[service] = "healthy"
                    if service == "database":
                        self._state.service_status["api"] = "healthy"  # Fixes downstream
                else:
                    reward -= 0.3
        
        elif 15 <= action.action_id <= 16:  # scale (API or Database)
            service = ["api", "database"][action.action_id - 15]
            if service not in self.services_scaled:
                self.services_scaled.add(service)
                
                # Check if scaling is correct
                if "scale_" + service in self._state.correct_mitigation:
                    reward += 0.75
                    self._state.service_status[service] = "healthy"
                else:
                    reward -= 0.2
        
        # Communication actions
        elif action.action_id == 17:  # notify_team
            if not self.teams_notified:
                self.teams_notified = True
                reward += 0.25
        
        elif action.action_id == 18:  # update_status_page
            if not self.status_page_updated:
                self.status_page_updated = True
                reward += 0.25
        
        elif action.action_id == 19:  # send_user_communication
            if not self.users_communicated:
                self.users_communicated = True
                reward += 0.15
        
        # Resolution
        elif action.action_id == 20:  # resolve_incident
            # Check if all services are healthy
            all_healthy = all(
                status == "healthy" 
                for service, status in self._state.service_status.items()
                if service in self._state.affected_services
            )
            
            if all_healthy:
                self.incident_resolved = True
                # Big reward for resolution
                reward += 3.0
                # Time bonus (faster = better)
                time_bonus = max(0, (30 - self.time_elapsed) * 0.01)
                reward += time_bonus
                done = True
            else:
                # Penalty for premature resolution
                reward -= 1.0
                done = True
        
        # Update total reward
        self.total_reward += reward
        
        # Check timeout
        if self.time_elapsed >= self.max_steps:
            done = True
        
        # Return observation
        obs = self._get_observation()
        obs.reward = reward
        obs.done = done
        
        return obs
    
    def _get_observation(self) -> IncidentObservation:
        """Generate current observation."""
        
        # Build alerts
        active_alerts = []
        if not self.alerts_read:
            active_alerts = ["[Call read_alerts to see alerts]"]
        else:
            if self._state.task_id == 1:
                active_alerts = [
                    "🚨 CRITICAL: API service down - no response",
                    "⚠️  HIGH: Frontend experiencing errors",
                    "📊 Customer complaints spiking"
                ]
            elif self._state.task_id == 2:
                active_alerts = [
                    "🚨 CRITICAL: Database queries failing",
                    "⚠️  HIGH: API returning 500 errors",
                    "📊 Recent deployment detected"
                ]
            else:  # task_id == 3
                active_alerts = [
                    "🚨 CRITICAL: Database CPU at 95%",
                    "🚨 CRITICAL: API timeout rate high",
                    "⚠️  HIGH: Connection pool exhausted",
                    "📊 Cascading failure detected"
                ]
        
        # Build logs (only for inspected services)
        recent_logs = {}
        for service in self.logs_inspected:
            if self._state.task_id == 1 and service == "api":
                recent_logs["api"] = [
                    "ERROR: Out of memory - process killed",
                    "INFO: Last request before crash at 14:32:15"
                ]
            elif self._state.task_id == 2 and service == "database":
                recent_logs["database"] = [
                    "ERROR: Syntax error in migration v2.3.1",
                    "ERROR: Incompatible schema changes detected"
                ]
            elif self._state.task_id == 2 and service == "api":
                recent_logs["api"] = [
                    "ERROR: Database query timeout",
                    "ERROR: 500 Internal Server Error"
                ]
            elif self._state.task_id == 3 and service == "database":
                recent_logs["database"] = [
                    "WARN: Connection pool exhausted (95% utilization)",
                    "ERROR: Slow query detected (>10s)",
                    "WARN: CPU usage at 95%"
                ]
            elif self._state.task_id == 3 and service == "api":
                recent_logs["api"] = [
                    "ERROR: Database connection timeout",
                    "ERROR: Request timeout (30s exceeded)"
                ]
        
        # Build metrics summary
        metrics_summary = {}
        for service in self.metrics_checked:
            if service in self._state.affected_services:
                metrics_summary[service] = {
                    "cpu": 85.0 if service == "database" else 45.0,
                    "memory": 92.0 if service == "api" else 60.0,
                    "latency": 5000.0 if service in ["api", "database"] else 100.0
                }
        
        return IncidentObservation(
            active_alerts=active_alerts,
            service_status=self._state.service_status.copy(),
            recent_logs=recent_logs,
            metrics_summary=metrics_summary,
            customer_complaints=self._state.customer_complaints,
            time_elapsed=self.time_elapsed,
            revenue_loss=self._state.revenue_loss,
            teams_notified=self.teams_notified,
            status_page_updated=self.status_page_updated,
            reward=0.0,
            done=False
        )
    
    def render(self):
        """Render current state (optional for debugging)."""
        print(f"\n{'='*60}")
        print(f"Task {self.task_id} - Step {self.time_elapsed}")
        print(f"{'='*60}")
        print(f"Service Status: {self._state.service_status}")
        print(f"Revenue Loss: ${self._state.revenue_loss:,.0f}")
        print(f"Complaints: {self._state.customer_complaints}")
        print(f"Incident Resolved: {self.incident_resolved}")
        print(f"Total Reward: {self.total_reward:.2f}")
        print(f"{'='*60}\n")