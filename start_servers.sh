#!/usr/bin/env bash
set -e

# Terminate any stale server processes
pkill -f "adk web" || true
pkill -f "frontend/main.py" || true
sleep 1

CDIR="/config/Desktop/Session1/travel-concierge"

# Start ADK agent playground on port 8000
nohup "${CDIR}/.venv/bin/adk" web "${CDIR}" --port 8000 --reload_agents --memory_service_uri=agentengine://1255508138501603328 < /dev/null > /tmp/agent_playground.log 2>&1 &

# Start custom frontend proxy on port 8080
nohup env AGENT_ENGINE_RESOURCE_NAME="projects/819136569956/locations/us-east1/reasoningEngines/677921486291337216" AGENT_DIRECTORY="app" PORT=8080 "${CDIR}/.venv/bin/python" "${CDIR}/frontend/main.py" < /dev/null > /tmp/frontend_proxy.log 2>&1 &

echo "Servers started in detached background processes."
