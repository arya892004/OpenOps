from fastapi import FastAPI
import gradio as gr

# 🔥 IMPORTANT: OpenEnv server
from openenv.core.env_server.http_server import create_http_env_app

# 🔥 Your environment
from server.my_env_environment import MyEnvEnvironment


# ---------------------------------------------------
# 1) Create environment instance
# ---------------------------------------------------
env = MyEnvEnvironment()

# ---------------------------------------------------
# 2) Create OpenEnv HTTP app (this exposes /reset /step)
# ---------------------------------------------------
openenv_app = create_http_env_app(env)

# ---------------------------------------------------
# 3) Create main FastAPI app
# ---------------------------------------------------
app = FastAPI()

# Mount OpenEnv API at root
app.mount("/", openenv_app)


# ---------------------------------------------------
# 4) Gradio UI (mounted at /ui)
# ---------------------------------------------------
def demo_fn(text):
    return f"OpenOps UI working ✅ : {text}"

demo = gr.Interface(
    fn=demo_fn,
    inputs="text",
    outputs="text",
    title="OpenOps Incident Commander"
)

app = gr.mount_gradio_app(app, demo, path="/ui")