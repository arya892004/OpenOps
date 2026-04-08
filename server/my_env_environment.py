from openenv import Environment
import asyncio

class MyEnvEnvironment(Environment):

    def __init__(self):
        super().__init__()
        self.state = {}

    # REQUIRED async reset
    async def reset_async(self):
        print("ASYNC RESET CALLED")
        await asyncio.sleep(0)
        return self.reset()

    # REQUIRED sync reset
    def reset(self):
        print("RESET CALLED")
        self.state = {
            "incident": "Database outage",
            "status": "investigating",
            "steps_taken": []
        }

        return {
            "observation": self.state,
            "info": {}
        }

    # REQUIRED step
    def step(self, action):
        print("STEP CALLED:", action)

        action_text = action.get("action", "").lower()

        if "restart" in action_text:
            self.state["status"] = "resolved"
            reward = 1
            done = True
        else:
            self.state["steps_taken"].append(action_text)
            reward = 0
            done = False

        return {
            "observation": self.state,
            "reward": reward,
            "done": done,
            "info": {}
        }

    # REQUIRED close
    def close(self):
        print("ENV CLOSED")
        self.state = {}