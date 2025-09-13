#!/bin/bash
# AI Manager System Startup Script
# This script automatically starts all AI Manager services with proper environment

set -e  # Exit on any error

echo "🚀 Starting AI Manager..."

# Source bashrc to get environment variables (including ANTHROPIC_API_KEY)
echo "📋 Loading environment variables..."
source ~/.bashrc

# Verify ANTHROPIC_API_KEY is available
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ERROR: ANTHROPIC_API_KEY not found in environment"
    echo "   Please add it to your ~/.bashrc file"
    exit 1
fi

echo "✅ ANTHROPIC_API_KEY loaded (length: ${#ANTHROPIC_API_KEY})"

# Change to project directory
cd /home/yamnik/Projects/ai-manager

# Function to start a service in background
start_service() {
    local service_name="$1"
    local command="$2"
    
    echo "🔄 Starting $service_name..."
    eval "$command" &
    local pid=$!
    echo "✅ $service_name started (PID: $pid)"
    sleep 2  # Give service time to start
}

# Start services in order
echo "🌐 Starting Backend API Server..."
start_service "Backend API" "uv run python3 src/services/api_server.py"

echo "📊 Starting Monitoring Website..."
start_service "Monitoring Website" "uv run python3 src/services/monitoring_service.py"

echo "🤖 Starting AI Agents..."
start_service "Blaze Agent" "uv run python3 -m src.agents.blaze_agent"
start_service "Maya Agent" "uv run python3 -m src.agents.maya_agent"
start_service "AI Manager Agent" "uv run python3 -m src.agents.ai_context_manager_agent"

# Wait a moment for all services to register
echo "⏳ Waiting for services to register..."
sleep 5

# Check system status
echo "🔍 Checking system status..."
echo "Backend API: $(curl -s http://localhost:5000/health | jq -r '.status' 2>/dev/null || echo 'Not responding')"
echo "Monitoring Website: $(curl -s http://localhost:8000/health | jq -r '.monitoring_website' 2>/dev/null || echo 'Not responding')"

# Show registered agents
echo "🤖 Registered Agents:"
curl -s http://localhost:5000/api/agents | jq -r '.[].id' 2>/dev/null || echo "No agents registered yet"

echo ""
echo "🎉 AI Manager Started!"
echo "📊 Monitoring Website: http://localhost:8000"
echo "🔧 Backend API: http://localhost:5000"
echo ""
echo "💡 To stop all services, run: ./scripts/stop.sh"
echo "💡 To check status, run: ./scripts/status.sh"