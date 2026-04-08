import sys
import os

# 🔥 CRITICAL FIX — make /env importable on HuggingFace Spaces
sys.path.append(os.path.abspath("env"))

from fastapi import FastAPI
import gradio as gr

# now this import will ALWAYS work
from server.my_env_environment import MyEnvEnvironment
from models import IncidentAction

app = FastAPI()
env = MyEnvEnvironment()

# ---------------------------------------------------
# Health check (Spaces looks for this)
# ---------------------------------------------------
@app.get("/")
def root():
    return {"status": "OpenOps Incident Commander running"}

# ---------------------------------------------------
# OpenEnv required endpoints
# ---------------------------------------------------
@app.post("/reset")
def reset():
    obs = env.reset()
    return obs.model_dump()

@app.post("/step")
def step(action: IncidentAction):
    obs = env.step(action)
    return obs.model_dump()

# ---------------------------------------------------
# Optional Gradio UI (nice for demo)
# ---------------------------------------------------
def demo_reset():
    obs = env.reset()
    return str(obs)

def demo_step(action_id):
    action = IncidentAction(action_id=int(action_id))
    obs = env.step(action)
    return str(obs)

demo = gr.Interface(
    fn=demo_step,
    inputs=gr.Number(label="Action ID (try 10 to resolve)"),
    outputs=gr.Textbox(label="Environment Response"),
    title="🚨 OpenOps Incident Commander",
    description="Enter action 10 to resolve the incident.",
)

app = gr.mount_gradio_app(app, demo, path="/ui")