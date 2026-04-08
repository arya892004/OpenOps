# Copyright (c) Meta Platforms, Inc.
"""
OpenOps Incident Commander — Environment Server Logic
"""

# Dual-import pattern (REQUIRED by OpenEnv):
# - Relative imports work when running in-repo (PYTHONPATH=src:envs)
# - Bare imports work inside Docker / HuggingFace Spaces (PYTHONPATH=/app/env)
try:
    from ..models import IncidentAction, IncidentObservation, IncidentState
except ImportError:
    from models import IncidentAction, IncidentObservation, IncidentState

from openenv.core.env_server import Environment


# Action ID → human label map (for logging / reward shaping)
ACTION_MAP = {
    0:  "investigate_logs",
    1:  "notify_oncall_team",
    2:  "update_status_page",
    3:  "rollback_deploy",
    4:  "restart_service",
    5:  "scale_up_replicas",
    6:  "flush_cache",
    7:  "enable_circuit_breaker",
    8:  "send_customer_comms",
    9:  "escalate_to_senior",
    10: "confirm_resolution",
}

# Per-action partial rewards (shaping signal for the agent)
ACTION_REWARDS = {
    0:  0.05,   # investigate — small signal
    1:  0.10,   # notify team
    2:  0.10,   # update status page
    3:  0.20,   # rollback — meaningful
    4:  0.20,   # restart service
    5:  0.10,   # scale up
    6:  0.10,   # flush cache
    7:  0.15,   # circuit breaker
    8:  0.10,   # customer comms
    9:  0.05,   # escalate
    10: 1.00,   # RESOLVE — full reward
}


class MyEnvEnvironment(Environment):
    """
    Incident Commander RL environment.

    The agent must navigate a production outage by taking remediation
    actions in the correct order. Resolving the incident (action_id=10)
    gives full reward=1.0 and ends the episode.
    """

    def __init__(self):
        self._state = IncidentState()

    # ------------------------------------------------------------------
    # REQUIRED: state must be a @property returning a State subclass
    # ------------------------------------------------------------------
    @property
    def state(self) -> IncidentState:
        return self._state

    # ------------------------------------------------------------------
    # REQUIRED: reset() → returns Observation, no reward needed here
    # ------------------------------------------------------------------
    def reset(self) -> IncidentObservation:
        print("[ENV] reset() called")

        self._state = IncidentState(
            task_id=1,
            incident_active=True,
            incident_resolved=False,
            root_cause=None,
            services={
                "database": "down",
                "api": "degraded",
                "frontend": "ok",
                "cache": "ok"
            },
            steps_taken=0,
            total_reward=0.0,
            teams_notified=False,
            status_page_updated=False,
            user_communication_sent=False,
        )

        return IncidentObservation(
            active_alerts=[
                "CRITICAL: DB_CONNECTION_POOL_EXHAUSTED",
                "WARNING: API_ERROR_RATE_85PCT",
                "WARNING: P99_LATENCY_9500MS",
            ],
            service_status={
                "database": "down",
                "api": "degraded",
                "frontend": "ok",
                "cache": "ok"
            },
            recent_logs={
                "database": [
                    "ERROR: Connection refused on port 5432",
                    "ERROR: Max connections (100) reached",
                    "WARN:  Query timeout after 30s x 50 times",
                ],
                "api": [
                    "ERROR: upstream connect error",
                    "ERROR: 500 Internal Server Error x 842",
                ]
            },
            metrics_summary={
                "error_rate":    0.85,
                "latency_p99":   9500.0,
                "cpu_usage":     0.45,
                "memory_usage":  0.60,
                "db_connections": 100.0,
            },
            customer_complaints=12,
            time_elapsed=0,
            revenue_loss=0.0,
            teams_notified=False,
            status_page_updated=False,
            user_communication_sent=False,
            # reward and done come from Observation base class
            reward=0.0,
            done=False,
        )

    # ------------------------------------------------------------------
    # REQUIRED: step() → returns Observation (with reward + done inside)
    # ------------------------------------------------------------------
    def step(self, action: IncidentAction) -> IncidentObservation:
        action_id = action.action_id
        action_label = ACTION_MAP.get(action_id, f"unknown_action_{action_id}")
        print(f"[ENV] step() called — action_id={action_id} ({action_label})")

        self._state.steps_taken += 1

        # ---- Apply side-effects of each action to internal state ----
        if action_id == 1:
            self._state.teams_notified = True
        elif action_id == 2:
            self._state.status_page_updated = True
        elif action_id == 8:
            self._state.user_communication_sent = True
        elif action_id in (3, 4):
            # Rollback / restart starts fixing the database
            self._state.services["database"] = "recovering"
        elif action_id == 5:
            self._state.services["api"] = "recovering"

        # ---- Determine reward and done ----
        reward = ACTION_REWARDS.get(action_id, 0.0)
        done = False

        if action_id == 10:
            # Full resolution — episode ends
            self._state.incident_resolved = True
            self._state.incident_active = False
            self._state.root_cause = "Database connection pool exhausted due to slow query spike"
            self._state.services = {
                "database": "ok",
                "api":      "ok",
                "frontend": "ok",
                "cache":    "ok"
            }
            done = True

        self._state.total_reward += reward

        # ---- Build and return observation ----
        resolved = self._state.incident_resolved
        elapsed = self._state.steps_taken * 5  # 5 min per step

        return IncidentObservation(
            active_alerts=[] if resolved else [
                "CRITICAL: DB_CONNECTION_POOL_EXHAUSTED",
                "WARNING: API_ERROR_RATE_85PCT",
            ],
            service_status=dict(self._state.services),
            recent_logs={} if resolved else {
                "database": ["ERROR: Connection refused on port 5432"],
                "api":      ["ERROR: 500 Internal Server Error"],
            },
            metrics_summary={
                "error_rate":    0.0 if resolved else 0.85,
                "latency_p99":   120.0 if resolved else 9500.0,
                "cpu_usage":     0.30 if resolved else 0.45,
                "memory_usage":  0.40 if resolved else 0.60,
                "db_connections": 12.0 if resolved else 100.0,
            },
            customer_complaints=0 if resolved else max(0, 12 - self._state.steps_taken),
            time_elapsed=elapsed,
            revenue_loss=0.0 if resolved else elapsed * 120.0,  # $120/min
            teams_notified=self._state.teams_notified,
            status_page_updated=self._state.status_page_updated,
            user_communication_sent=self._state.user_communication_sent,
            reward=reward,
            done=done,
        )

    # ------------------------------------------------------------------
    # REQUIRED: close()
    # ------------------------------------------------------------------
    def close(self):
        print("[ENV] close() called")
        self._state = IncidentState()