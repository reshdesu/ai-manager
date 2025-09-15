#!/bin/bash

# AI Manager System Startup Script
# Ensures proper startup order and dependency management

set -e  # Exit on any error

echo "🚀 Starting AI Manager System..."

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "agent.*\.py" || true
pkill -f "api_server" || true
pkill -f "monitoring_service" || true
sleep 2

# Set environment
export PYTHONPATH=.

# Start API Server first (critical dependency)
echo "📡 Starting API Server..."
PYTHONPATH=. uv run python3 src/services/api_server.py &
API_PID=$!
echo "API Server PID: $API_PID"

# Wait for API server to be ready
echo "⏳ Waiting for API server to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        echo "✅ API Server is ready!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 1
done

if ! curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "❌ API Server failed to start!"
    exit 1
fi

# Start AI Manager Agent
echo "🤖 Starting AI Manager Agent..."
PYTHONPATH=. uv run python3 src/agents/ai_context_manager_agent.py &
AI_MANAGER_PID=$!
echo "AI Manager PID: $AI_MANAGER_PID"
sleep 3

# Start Maya Agent
echo "🎮 Starting Maya Agent..."
PYTHONPATH=. uv run python3 src/agents/maya_agent.py &
MAYA_PID=$!
echo "Maya Agent PID: $MAYA_PID"
sleep 3

# Start Blaze Agent
echo "🔥 Starting Blaze Agent..."
PYTHONPATH=. uv run python3 src/agents/blaze_agent.py &
BLAZE_PID=$!
echo "Blaze Agent PID: $BLAZE_PID"
sleep 3

# Start Jugad Agent
echo "🛠️ Starting Jugad Agent..."
PYTHONPATH=. uv run python3 src/agents/jugad_agent.py &
JUGAD_PID=$!
echo "Jugad Agent PID: $JUGAD_PID"
sleep 3

# Start Monitoring Service
echo "📊 Starting Monitoring Service..."
PYTHONPATH=. uv run python3 src/services/monitoring_service.py &
MONITOR_PID=$!
echo "Monitoring Service PID: $MONITOR_PID"
sleep 3

# Verify all services are running
echo "🔍 Verifying all services..."
sleep 5

# Check API Server
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ API Server: Running"
else
    echo "❌ API Server: Failed"
fi

# Check Monitoring Service
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Monitoring Service: Running"
else
    echo "❌ Monitoring Service: Failed"
fi

# Check agents registration
echo "🤖 Checking agent registration..."
AGENTS=$(curl -s http://localhost:5000/api/agents | jq -r '.[].agent_id' 2>/dev/null || echo "")
if [ -n "$AGENTS" ]; then
    echo "✅ Agents registered: $(echo $AGENTS | wc -w)"
    echo "Registered agents: $AGENTS"
else
    echo "❌ No agents registered"
fi

echo ""
echo "🎉 AI Manager System started!"
echo "📊 Monitoring Dashboard: http://localhost:8000"
echo "🔗 API Server: http://localhost:5000"
echo ""
echo "Process IDs:"
echo "  API Server: $API_PID"
echo "  AI Manager: $AI_MANAGER_PID"
echo "  Maya Agent: $MAYA_PID"
echo "  Blaze Agent: $BLAZE_PID"
echo "  Jugad Agent: $JUGAD_PID"
echo "  Monitoring: $MONITOR_PID"
echo ""
echo "To stop all services: ./scripts/stop_all.sh"