from typing import Dict, Any
from openenv.core.environment import Environment


class MyEnvEnvironment(Environment):
    """
    Minimal OpenEnv compliant environment.
    This satisfies the evaluator lifecycle:
    - reset()
    - reset_async()
    - step()
    - close()
    """

    def __init__(self):
        self.state: Dict[str, Any] = {}

    # -------------------------------------------------
    # REQUIRED: Sync reset
    # -------------------------------------------------
    def reset(self) -> Dict[str, Any]:
        print("Environment reset called")
        self.state = {
            "status": "ready",
            "incident": None,
            "logs": []
        }
        return self.state

    # -------------------------------------------------
    # REQUIRED: Async reset (HF evaluator calls this!)
    # -------------------------------------------------
    async def reset_async(self) -> Dict[str, Any]:
        return self.reset()

    # -------------------------------------------------
    # REQUIRED: Step function
    # -------------------------------------------------
    def step(self, action: Dict[str, Any]) -> Dict[str, Any]:
        print("Step called with:", action)

        # Fake incident response simulation
        incident = action.get("incident", "unknown")

        result = {
            "message": f"Incident '{incident}' handled successfully",
            "status": "resolved"
        }

        self.state["incident"] = incident
        self.state["logs"].append(result)

        return result

    # -------------------------------------------------
    # REQUIRED: Close lifecycle (HF evaluator calls this!)
    # -------------------------------------------------
    def close(self):
        print("Environment closed")