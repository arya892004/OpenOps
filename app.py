from fastapi import FastAPI
import gradio as gr

# OpenEnv server
from openenv.core.env_server.http_server import create_http_env_app

# Your environment
from server.my_env_environment import MyEnvEnvironment

# ---------------------------------------------------
# 1️⃣ Create FastAPI app
# ---------------------------------------------------
app = FastAPI(title="OpenOps Incident Commander")

# ---------------------------------------------------
# 2️⃣ Register OpenEnv HTTP server
# This exposes the REQUIRED endpoints:
# /reset
# /step
# /state
# ---------------------------------------------------
env = MyEnvEnvironment()
openenv_app = create_http_env_app(env)

app.mount("/env", openenv_app)

# Root redirect (validator sometimes hits "/")
@app.get("/")
def root():
    return {"message": "OpenOps Environment Running 🚀"}


# ---------------------------------------------------
# 3️⃣ Simple Gradio UI (for humans, not validator)
# Will run at /ui
# ---------------------------------------------------
def run_demo():
    return "OpenOps Incident Commander is running ✅"

demo = gr.Interface(
    fn=run_demo,
    inputs=[],
    outputs="text",
    title="OpenOps Incident Commander",
    description="Environment is live and ready for validation.",
)

app = gr.mount_gradio_app(app, demo, path="/ui")