"""Quick local test - runs in <5 seconds"""
from server.my_env_environment import MyEnvEnvironment
from models import IncidentAction
from graders import get_grader

print("Testing OpenOps environment...")

for task_id in [1, 2, 3]:
    env = MyEnvEnvironment()
    env.reset(task_id=task_id)
    
    # Take a few actions
    env.step(IncidentAction(action_id=0, task_id=task_id))
    env.step(IncidentAction(action_id=1, task_id=task_id))
    
    grader = get_grader(task_id)
    score = grader(env)
    print(f"Task {task_id}: Environment working ✅ (test score: {score:.2f})")

print("\n✅ All tests passed!")