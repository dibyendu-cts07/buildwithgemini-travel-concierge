import subprocess
import os
import sys

CDIR = "/config/Desktop/Session1/travel-concierge"

# Kill old processes if running
os.system("pkill -f 'adk web' || true")
os.system("pkill -f 'frontend/main.py' || true")

# Start ADK agent playground on port 8000
p1 = subprocess.Popen(
    [
        f"{CDIR}/.venv/bin/adk",
        "web",
        CDIR,
        "--port",
        "8000",
        "--reload_agents",
        "--memory_service_uri=agentengine://1255508138501603328",
    ],
    cwd=CDIR,
    stdin=subprocess.DEVNULL,
    stdout=open("/tmp/agent_playground.log", "w"),
    stderr=subprocess.STDOUT,
    start_new_session=True,
)

# Start custom frontend proxy on port 8080
env = os.environ.copy()
env["AGENT_ENGINE_RESOURCE_NAME"] = "projects/819136569956/locations/us-east1/reasoningEngines/677921486291337216"
env["AGENT_DIRECTORY"] = "app"
env["PORT"] = "8080"

p2 = subprocess.Popen(
    [f"{CDIR}/.venv/bin/python", f"{CDIR}/frontend/main.py"],
    cwd=f"{CDIR}/frontend",
    env=env,
    stdin=subprocess.DEVNULL,
    stdout=open("/tmp/frontend_proxy.log", "w"),
    stderr=subprocess.STDOUT,
    start_new_session=True,
)

print(f"Successfully launched Playground (PID {p1.pid}) and Frontend Proxy (PID {p2.pid})")
