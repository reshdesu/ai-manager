#!/usr/bin/env python3
"""
AI Context Manager Monitoring Website
HTTP REST API for monitoring real-time communication between AI agents
"""

import json
import time
import threading
from datetime import datetime
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory storage for monitoring data
monitoring_data = {
    "agents": {},
    "communications": [],
    "stats": {
        "total_communications": 0,
        "active_agents": 0,
        "last_update": None
    }
}

# HTML template for the monitoring dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Context Manager - Real-time Monitoring</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .stats { display: flex; gap: 20px; margin-bottom: 20px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex: 1; }
        .stat-number { font-size: 2em; font-weight: bold; color: #3498db; }
        .stat-label { color: #7f8c8d; margin-top: 5px; }
        .agents-section, .communications-section { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .agent-item { padding: 10px; border-bottom: 1px solid #ecf0f1; }
        .agent-item:last-child { border-bottom: none; }
        .communication-item { padding: 15px; border-bottom: 1px solid #ecf0f1; background: #f8f9fa; }
        .communication-item:last-child { border-bottom: none; }
        .timestamp { color: #95a5a6; font-size: 0.9em; }
        .status-online { color: #27ae60; font-weight: bold; }
        .status-offline { color: #e74c3c; font-weight: bold; }
        .refresh-btn { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
        .refresh-btn:hover { background: #2980b9; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI Context Manager - Real-time Monitoring</h1>
            <p>Monitor AI agent communications and system status</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="total-communications">{{ stats.total_communications }}</div>
                <div class="stat-label">Total Communications</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="active-agents">{{ stats.active_agents }}</div>
                <div class="stat-label">Active Agents</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="last-update">{{ stats.last_update }}</div>
                <div class="stat-label">Last Update</div>
            </div>
        </div>
        
        <div class="agents-section">
            <h2>Active AI Agents</h2>
            <div id="agents-list">
                {% for agent_id, agent in agents.items() %}
                <div class="agent-item">
                    <strong>{{ agent_id }}</strong> - 
                    <span class="status-{{ agent.status }}">{{ agent.status }}</span>
                    <div class="timestamp">Last seen: {{ agent.last_seen }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="communications-section">
            <h2>Recent Communications</h2>
            <button class="refresh-btn" onclick="refreshData()">Refresh</button>
            <div id="communications-list">
                {% for comm in communications[-10:] %}
                <div class="communication-item">
                    <strong>{{ comm.from_agent }} → {{ comm.to_agent }}</strong>
                    <div>{{ comm.message }}</div>
                    <div class="timestamp">{{ comm.timestamp }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <script>
        function refreshData() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-communications').textContent = data.stats.total_communications;
                    document.getElementById('active-agents').textContent = data.stats.active_agents;
                    document.getElementById('last-update').textContent = data.stats.last_update;
                });
            
            fetch('/api/agents')
                .then(response => response.json())
                .then(data => {
                    const agentsList = document.getElementById('agents-list');
                    agentsList.innerHTML = '';
                    for (const [agentId, agent] of Object.entries(data.agents)) {
                        const agentDiv = document.createElement('div');
                        agentDiv.className = 'agent-item';
                        agentDiv.innerHTML = `
                            <strong>${agentId}</strong> - 
                            <span class="status-${agent.status}">${agent.status}</span>
                            <div class="timestamp">Last seen: ${agent.last_seen}</div>
                        `;
                        agentsList.appendChild(agentDiv);
                    }
                });
            
            fetch('/api/communications')
                .then(response => response.json())
                .then(data => {
                    const commList = document.getElementById('communications-list');
                    commList.innerHTML = '';
                    data.communications.slice(-10).forEach(comm => {
                        const commDiv = document.createElement('div');
                        commDiv.className = 'communication-item';
                        commDiv.innerHTML = `
                            <strong>${comm.from_agent} → ${comm.to_agent}</strong>
                            <div>${comm.message}</div>
                            <div class="timestamp">${comm.timestamp}</div>
                        `;
                        commList.appendChild(commDiv);
                    });
                });
        }
        
        // Auto-refresh every 5 seconds
        setInterval(refreshData, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Serve the monitoring dashboard"""
    return render_template_string(DASHBOARD_TEMPLATE, 
                                agents=monitoring_data["agents"],
                                communications=monitoring_data["communications"],
                                stats=monitoring_data["stats"])

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    return jsonify(monitoring_data["stats"])

@app.route('/api/agents')
def get_agents():
    """Get all AI agents"""
    return jsonify(monitoring_data["agents"])

@app.route('/api/agents/<agent_id>')
def get_agent(agent_id):
    """Get specific agent information"""
    if agent_id in monitoring_data["agents"]:
        return jsonify(monitoring_data["agents"][agent_id])
    return jsonify({"error": "Agent not found"}), 404

@app.route('/api/communications')
def get_communications():
    """Get all communications"""
    return jsonify({"communications": monitoring_data["communications"]})

@app.route('/api/communications', methods=['POST'])
def add_communication():
    """Add a new communication"""
    data = request.get_json()
    
    communication = {
        "id": len(monitoring_data["communications"]) + 1,
        "from_agent": data.get("from_agent", "unknown"),
        "to_agent": data.get("to_agent", "unknown"),
        "message": data.get("message", ""),
        "timestamp": datetime.now().isoformat(),
        "type": data.get("type", "message")
    }
    
    monitoring_data["communications"].append(communication)
    monitoring_data["stats"]["total_communications"] += 1
    monitoring_data["stats"]["last_update"] = datetime.now().isoformat()
    
    return jsonify(communication), 201

@app.route('/api/agents/<agent_id>/status', methods=['POST'])
def update_agent_status(agent_id):
    """Update agent status"""
    data = request.get_json()
    
    if agent_id not in monitoring_data["agents"]:
        monitoring_data["agents"][agent_id] = {
            "id": agent_id,
            "status": "offline",
            "last_seen": None,
            "created_at": datetime.now().isoformat()
        }
    
    monitoring_data["agents"][agent_id]["status"] = data.get("status", "online")
    monitoring_data["agents"][agent_id]["last_seen"] = datetime.now().isoformat()
    
    # Update active agents count
    active_count = sum(1 for agent in monitoring_data["agents"].values() 
                      if agent["status"] == "online")
    monitoring_data["stats"]["active_agents"] = active_count
    monitoring_data["stats"]["last_update"] = datetime.now().isoformat()
    
    return jsonify(monitoring_data["agents"][agent_id])

def simulate_ai_activity():
    """Simulate AI agent activity for demonstration"""
    agents = ["ai-context-manager", "ai-responder", "monitoring-system"]
    
    while True:
        # Simulate agent status updates
        for agent_id in agents:
            status = "online" if time.time() % 10 < 8 else "offline"
            update_data = {"status": status}
            
            # Update agent status
            if agent_id not in monitoring_data["agents"]:
                monitoring_data["agents"][agent_id] = {
                    "id": agent_id,
                    "status": "offline",
                    "last_seen": None,
                    "created_at": datetime.now().isoformat()
                }
            
            monitoring_data["agents"][agent_id]["status"] = status
            monitoring_data["agents"][agent_id]["last_seen"] = datetime.now().isoformat()
        
        # Update active agents count
        active_count = sum(1 for agent in monitoring_data["agents"].values() 
                          if agent["status"] == "online")
        monitoring_data["stats"]["active_agents"] = active_count
        monitoring_data["stats"]["last_update"] = datetime.now().isoformat()
        
        # Simulate communications
        if time.time() % 15 < 5:  # Random communications
            from_agent = agents[0]
            to_agent = agents[1]
            messages = [
                "Processing context update",
                "Sending response to user",
                "Updating AI context files",
                "Monitoring system status",
                "Coordinating with other agents"
            ]
            
            communication = {
                "id": len(monitoring_data["communications"]) + 1,
                "from_agent": from_agent,
                "to_agent": to_agent,
                "message": messages[int(time.time()) % len(messages)],
                "timestamp": datetime.now().isoformat(),
                "type": "message"
            }
            
            monitoring_data["communications"].append(communication)
            monitoring_data["stats"]["total_communications"] += 1
        
        time.sleep(5)  # Update every 5 seconds

if __name__ == "__main__":
    import sys
    
    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    print(f"Starting AI Context Manager Monitoring Website on port {port}")
    print(f"Dashboard: http://localhost:{port}")
    print(f"API: http://localhost:{port}/api/")
    
    # Start simulation thread
    simulation_thread = threading.Thread(target=simulate_ai_activity, daemon=True)
    simulation_thread.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=port, debug=False)

