#!/bin/bash
# AI Manager System Stop Script

echo "🛑 Stopping AI Manager..."

# Stop all AI Manager processes
echo "🔄 Stopping AI agents..."
pkill -f "src.agents" || echo "No agent processes found"

echo "🔄 Stopping services..."
pkill -f "api_server" || echo "No API server process found"
pkill -f "monitoring_service" || echo "No monitoring service process found"

# Wait for processes to stop
sleep 3

echo "✅ AI Manager stopped"
echo "💡 To start again, run: ./scripts/start.sh"
