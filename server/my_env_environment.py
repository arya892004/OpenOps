from typing import Dict, Any
from openenv.core.environment import Environment


class MyEnvEnvironment(Environment):

    def __init__(self):
        self.state: Dict[str, Any] = {}

    # REQUIRED by OpenEnv
    def reset(self) -> Dict[str, Any]:
        print("RESET CALLED")
        self.state = {
            "status": "ready",
            "incident": None,
            "logs": []
        }
        return self.state

    # REQUIRED by OpenEnv evaluator
    async def reset_async(self) -> Dict[str, Any]:
        print("ASYNC RESET CALLED")
        return self.reset()

    # REQUIRED by OpenEnv
    def step(self, action: Dict[str, Any]) -> Dict[str, Any]:
        print("STEP CALLED:", action)

        incident = action.get("incident", "unknown")

        result = {
            "status": "resolved",
            "message": f"Incident '{incident}' handled"
        }

        self.state["incident"] = incident
        self.state["logs"].append(result)

        return result

    # REQUIRED by OpenEnv evaluator
    def close(self):
        print("ENV CLOSED")