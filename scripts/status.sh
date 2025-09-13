#!/bin/bash
# AI Manager System Status Script

echo "📊 AI Manager Status"
echo "=========================="

# Check if services are running
echo "🌐 Backend API Server:"
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "  ✅ Running on port 5000"
    echo "  📈 Status: $(curl -s http://localhost:5000/health | jq -r '.status')"
else
    echo "  ❌ Not running"
fi

echo ""
echo "📊 Monitoring Website:"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "  ✅ Running on port 8000"
    echo "  📈 Status: $(curl -s http://localhost:8000/health | jq -r '.monitoring_website')"
else
    echo "  ❌ Not running"
fi

echo ""
echo "🤖 Registered Agents:"
agents=$(curl -s http://localhost:5000/api/agents 2>/dev/null)
if [ $? -eq 0 ] && [ "$agents" != "[]" ]; then
    echo "$agents" | jq -r '.[] | "  ✅ \(.id) - \(.status)"'
else
    echo "  ❌ No agents registered"
fi

echo ""
echo "📈 System Statistics:"
stats=$(curl -s http://localhost:5000/api/stats 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "$stats" | jq -r '"  📊 Active Agents: \(.active_agents)", "  📞 API Calls: \(.api_calls)", "  💬 Communications: \(.total_communications)"'
else
    echo "  ❌ Unable to get statistics"
fi

echo ""
echo "🔗 Access Points:"
echo "  📊 Monitoring: http://localhost:8000"
echo "  🔧 API: http://localhost:5000"
echo "  ❤️ Health: http://localhost:5000/health"
