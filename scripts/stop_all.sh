#!/bin/bash

# AI Manager System Stop Script
# Cleanly stops all services

echo "🛑 Stopping AI Manager System..."

# Stop all services
echo "🧹 Stopping all services..."
pkill -f "agent.*\.py" || true
pkill -f "api_server" || true
pkill -f "monitoring_service" || true

# Wait for processes to stop
sleep 3

# Force kill if still running
echo "💀 Force stopping any remaining processes..."
pkill -9 -f "agent.*\.py" || true
pkill -9 -f "api_server" || true
pkill -9 -f "monitoring_service" || true

echo "✅ All services stopped!"