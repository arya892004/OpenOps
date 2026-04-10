from server.my_env_environment import MyEnvEnvironment
from models import IncidentAction
from graders import get_grader

env = MyEnvEnvironment()
obs = env.reset(task_id=1)
print("Initial observation:", obs.active_alerts)

# Take some actions
obs = env.step(IncidentAction(action_id=0, task_id=1))  # read_alerts
print("After read_alerts:", obs.reward)

obs = env.step(IncidentAction(action_id=1, task_id=1))  # inspect_logs_api
print("After inspect_logs:", obs.reward)

obs = env.step(IncidentAction(action_id=9, task_id=1))  # restart_api
print("After restart:", obs.reward)

obs = env.step(IncidentAction(action_id=20, task_id=1))  # resolve
print("After resolve:", obs.reward, obs.done)

grader = get_grader(1)
score = grader(env)
print("Final score:", score)