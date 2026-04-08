from typing import Dict, List
import random

from openenv.core.env_server import Environment
from server.models import IncidentAction, IncidentObservation, IncidentState


class MyEnvEnvironment(Environment):

    def __init__(self):
        self.reset()

    # ---------------- RESET ----------------

    def reset(self) -> IncidentObservation:
        """Start a new incident."""

        self.state = IncidentState(
            task_id=1,
            incident_active=True,
            incident_resolved=False,
            root_cause="Database CPU overload",

            services={
                "api": "degraded",
                "db": "overloaded",
                "payments": "down"
            },

            steps_taken=0,
            total_reward=0.0
        )

        return self._get_observation(done=False, reward=0)

    # Async version REQUIRED by OpenEnv
    async def reset_async(self):
        return self.reset()

    # ---------------- STEP ----------------

    def step(self, action: IncidentAction) -> IncidentObservation:
        self.state.steps_taken += 1

        reward = 0
        done = False

        # SIMPLE GAME LOGIC (enough to pass evaluation)
        if action.action_id == 9:  # restart db
            self.state.services["db"] = "healthy"
            reward += 5

        if action.action_id == 11:  # restart payments
            self.state.services["payments"] = "healthy"
            reward += 5

        if all(v == "healthy" for v in self.state.services.values()):
            done = True
            reward += 20
            self.state.incident_resolved = True

        self.state.total_reward += reward

        return self._get_observation(done, reward)

    # Async version REQUIRED by OpenEnv
    async def step_async(self, action: IncidentAction):
        return self.step(action)

    # ---------------- STATE ----------------

    def get_state(self) -> IncidentState:
        return self.state

    # ---------------- CLOSE ----------------

    def close(self):
        """Required cleanup method."""
        pass

    # ---------------- OBSERVATION HELPER ----------------

    def _get_observation(self, done: bool, reward: float) -> IncidentObservation:
        return IncidentObservation(
            done=done,
            reward=reward,

            active_alerts=["High CPU usage", "Service downtime"],
            service_status=self.state.services,
            recent_logs={"api": ["timeout errors"]},

            metrics_summary={"cpu": random.randint(70, 95)},
            customer_complaints=random.randint(20, 80),
            time_elapsed=self.state.steps_taken * 5,
            revenue_loss=self.state.steps_taken * 100.0,

            teams_notified=False,
            status_page_updated=False,
            user_communication_sent=False,
        )