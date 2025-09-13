#!/usr/bin/env python3
"""
Monitoring Website for AI Communication System
Runs on port 8000 - connects to backend API on port 5000
"""

import requests
import logging
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitoringWebsite:
    """Monitoring website for AI communication system (port 8000)"""
    
    def __init__(self, backend_url="http://localhost:5000"):
        self.app = Flask(__name__)
        CORS(self.app)
        self.backend_url = backend_url
        
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup Flask routes"""
        
        # Main dashboard
        @self.app.route('/')
        def dashboard():
            return render_template_string(self._get_dashboard_html())
            
        # Proxy endpoints to backend
        @self.app.route('/api/stats')
        def get_stats():
            try:
                response = requests.get(f"{self.backend_url}/api/stats", timeout=5)
                return jsonify(response.json())
            except Exception as e:
                logger.error(f"Failed to get stats from backend: {e}")
                return jsonify({"error": "Backend unavailable"}), 503
                
        @self.app.route('/api/agents')
        def get_agents():
            try:
                response = requests.get(f"{self.backend_url}/api/agents", timeout=5)
                return jsonify(response.json())
            except Exception as e:
                logger.error(f"Failed to get agents from backend: {e}")
                return jsonify({"error": "Backend unavailable"}), 503
                
        @self.app.route('/api/communications')
        def get_communications():
            try:
                response = requests.get(f"{self.backend_url}/api/communications", timeout=5)
                return jsonify(response.json())
            except Exception as e:
                logger.error(f"Failed to get communications from backend: {e}")
                return jsonify({"error": "Backend unavailable"}), 503
                
        # Claude interface endpoints
        @self.app.route('/api/claude/request', methods=['POST'])
        def claude_request():
            try:
                response = requests.post(f"{self.backend_url}/api/claude/request", 
                                       json=request.get_json(), timeout=30)
                return jsonify(response.json())
            except Exception as e:
                logger.error(f"Failed to send Claude request to backend: {e}")
                return jsonify({"error": "Backend unavailable"}), 503
                
        @self.app.route('/api/nlp/analyze', methods=['POST'])
        def nlp_analyze():
            try:
                response = requests.post(f"{self.backend_url}/api/nlp/analyze", 
                                      json=request.get_json(), timeout=10)
                return jsonify(response.json())
            except Exception as e:
                logger.error(f"Failed to send NLP request to backend: {e}")
                return jsonify({"error": "Backend unavailable"}), 503
                
        # Health check
        @self.app.route('/health')
        def health_check():
            try:
                response = requests.get(f"{self.backend_url}/health", timeout=5)
                backend_health = response.json()
                return jsonify({
                    "monitoring_website": "healthy",
                    "backend_connection": "connected",
                    "backend_health": backend_health,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    "monitoring_website": "healthy",
                    "backend_connection": "disconnected",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }), 503
        
    def _get_dashboard_html(self):
        """Get the monitoring dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Communication System Monitor</title>
    <style>
        body {
            font-family: 'Courier New', 'Monaco', 'Consolas', monospace;
            margin: 0;
            padding: 0;
            background: #000000;
            color: #ffffff;
            font-size: 14px;
            line-height: 1.2;
        }
        .terminal {
            padding: 20px;
            width: 100%;
            margin-top: 50px;
        }
        .prompt {
            color: #ffffff;
            margin-bottom: 10px;
        }
        .prompt::before {
            content: "$ ";
            color: #ffffff;
        }
        .output {
            color: #ffffff;
            margin-bottom: 20px;
            white-space: pre-wrap;
        }
        .section {
            margin-bottom: 20px;
            border-bottom: 1px solid #dda0dd;
            padding-bottom: 15px;
        }
        .section-title {
            color: #ffffff;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-bottom: 20px;
        }
        .stat {
            background: #111111;
            padding: 8px;
            border: 1px solid #dda0dd;
            font-family: 'Courier New', 'Monaco', 'Consolas', monospace;
        }
        .stat-label {
            color: #888888;
            font-size: 12px;
        }
        .stat-value {
            color: #ffffff;
            font-weight: bold;
            font-size: 16px;
        }
        .agents-list {
            background: #111111;
            padding: 10px;
            border: 1px solid #dda0dd;
            margin-bottom: 20px;
        }
        .agent {
            margin-bottom: 8px;
            padding: 5px;
            border-left: 2px solid #dda0dd;
            padding-left: 10px;
        }
        .agent-name {
            color: #ffffff;
            font-weight: bold;
        }
        .agent-status {
            color: #888888;
            font-size: 12px;
        }
        .agent-status.online {
            color: #ffffff;
        }
        .agent-status.offline {
            color: #ff0000;
        }
        .communications {
            background: #111111;
            padding: 15px;
            border: 1px solid #dda0dd;
            height: calc(100vh - 120px);
            overflow-y: auto;
            font-family: 'Courier New', 'Monaco', 'Consolas', monospace;
        }
        .comm-item {
            margin-bottom: 8px;
            padding: 5px;
            border-left: 2px solid #dda0dd;
            padding-left: 10px;
        }
        .comm-item.ai-manager {
            border-left-color: #00ff00;
        }
        .comm-item.blaze-agent {
            border-left-color: #ff6b35;
        }
        .comm-item.maya-agent {
            border-left-color: #20b2aa;
        }
        .comm-item.unknown-agent {
            border-left-color: #888888;
        }
        .comm-timestamp {
            color: #888888;
            font-size: 11px;
        }
        .comm-sender {
            color: #ffffff;
            font-weight: bold;
        }
        .comm-message {
            color: #ffffff;
            margin-top: 2px;
        }
        .form-section {
            background: #111111;
            padding: 15px;
            border: 1px solid #dda0dd;
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 10px;
        }
        .form-group label {
            color: #ffffff;
            display: block;
            margin-bottom: 3px;
            font-size: 12px;
        }
        .form-group input, .form-group textarea, .form-group select {
            width: 100%;
            padding: 5px;
            background: #000000;
            color: #ffffff;
            border: 1px solid #dda0dd;
            font-family: 'Courier New', 'Monaco', 'Consolas', monospace;
            font-size: 14px;
        }
        .form-group textarea {
            height: 80px;
            resize: vertical;
        }
        button {
            background: #000000;
            color: #ffffff;
            border: 1px solid #dda0dd;
            padding: 8px 15px;
            font-family: 'Courier New', 'Monaco', 'Consolas', monospace;
            font-size: 14px;
            cursor: pointer;
        }
        button:hover {
            background: #111111;
        }
        .error {
            color: #ff0000;
            background: #2a0000;
            padding: 8px;
            border: 1px solid #ff0000;
            margin: 10px 0;
        }
        .success {
            color: #ffffff;
            background: #002a00;
            padding: 8px;
            border: 1px solid #00ff00;
            margin: 10px 0;
        }
        .refresh-indicator {
            color: #888888;
            font-size: 10px;
            text-align: left;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #dda0dd;
        }
        .topbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: #000000;
            border-bottom: 1px solid #dda0dd;
            padding: 10px 20px;
            font-family: 'Courier New', 'Monaco', 'Consolas', monospace;
            font-size: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 1000;
            min-height: 30px;
        }
        .topbar-left {
            flex: 0 0 auto;
            display: flex;
            align-items: center;
            gap: 30px;
        }
        .topbar-right {
            flex: 0 0 auto;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 30px;
            min-width: 300px;
        }
        .sidebar-toggle {
            background: #000000;
            color: #ffffff;
            border: 1px solid #dda0dd;
            padding: 8px 15px;
            font-family: 'Courier New', 'Monaco', 'Consolas', monospace;
            font-size: 12px;
            cursor: pointer;
            border-radius: 3px;
            transition: all 0.2s ease;
        }
        .sidebar-toggle:hover {
            border-color: #8a2be2;
        }
        .sidebar-toggle:active {
            background: #222222;
        }
        .sidebar {
            position: fixed;
            top: 50px;
            right: -320px;
            width: 300px;
            height: calc(100vh - 50px);
            background: #111111;
            border-left: 1px solid #dda0dd;
            transition: right 0.3s ease-in-out, visibility 0.3s ease-in-out, opacity 0.3s ease-in-out;
            z-index: 999;
            overflow-y: auto;
            padding: 20px;
            box-shadow: -2px 0 10px rgba(0, 0, 0, 0.5);
            visibility: hidden;
            opacity: 0;
        }
        .sidebar.open {
            right: 0;
            visibility: visible;
            opacity: 1;
        }
        .sidebar-content {
            font-family: 'Courier New', 'Monaco', 'Consolas', monospace;
            font-size: 12px;
        }
        .sidebar-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #dda0dd;
        }
        .sidebar-close {
            background: transparent;
            color: #888888;
            border: none;
            font-size: 18px;
            cursor: pointer;
            padding: 0;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .sidebar-close:hover {
            color: #ff0000;
        }
        .sidebar-section {
            margin-bottom: 20px;
            border-bottom: 1px solid #dda0dd;
            padding-bottom: 15px;
        }
        .sidebar-title {
            color: #ffffff;
            font-weight: bold;
            font-size: 14px;
        }
        .sidebar-stats {
            display: grid;
            grid-template-columns: 1fr;
            gap: 8px;
        }
        .sidebar-stat {
            background: #000000;
            padding: 6px;
            border: 1px solid #dda0dd;
            font-family: 'Courier New', 'Monaco', 'Consolas', monospace;
        }
        .sidebar-stat:hover {
            background: #000000;
            border-color: #dda0dd;
        }
        .sidebar-stat-label {
            color: #888888;
            font-size: 10px;
        }
        .sidebar-stat-value {
            color: #ffffff;
            font-weight: bold;
            font-size: 14px;
        }
        .sidebar-agents {
            background: #000000;
            padding: 10px;
            border: 1px solid #dda0dd;
        }
        .sidebar-agent {
            margin-bottom: 6px;
            padding: 4px;
            border-left: 2px solid #dda0dd;
            padding-left: 8px;
        }
        .sidebar-agent-name {
            color: #ffffff;
            font-weight: bold;
            font-size: 11px;
        }
        .sidebar-agent-status {
            color: #888888;
            font-size: 10px;
        }
        .sidebar-agent-status.online {
            color: #ffffff;
        }
        .sidebar-agent-status.offline {
            color: #ff0000;
        }
        .traffic-light {
            display: flex;
            gap: 15px;
        }
        .status-light {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            border: 1px solid #000000;
        }
        .status-light.online {
            background: #00ff00;
            box-shadow: 0 0 10px #00ff00;
        }
        .status-light.offline {
            background: #ff0000;
            box-shadow: 0 0 10px #ff0000;
        }
        .status-light.warning {
            background: #ffff00;
            box-shadow: 0 0 10px #ffff00;
        }
        .status-item {
            margin-bottom: 5px;
            color: #ffffff;
        }
        .status-label {
            color: #888888;
            font-size: 10px;
        }
    </style>
</head>
<body>
    <div class="topbar">
        <div class="topbar-left">
            <div style="color: #ffffff; font-weight: bold;">AI COMMUNICATION SYSTEM MONITOR</div>
        </div>
        
        <div class="topbar-right">
            <div class="traffic-light" id="traffic_light">
                <div class="status-item">
                    <span class="status-light offline" id="api_light"></span>
                    <span class="status-label">API SERVER</span>
                </div>
                <div class="status-item">
                    <span class="status-light offline" id="manager_light"></span>
                    <span class="status-label">MANAGER</span>
                </div>
            </div>
            <button id="sidebar-toggle" class="sidebar-toggle">Stats</button>
        </div>
    </div>
    
    <div class="sidebar" id="sidebar">
        <div class="sidebar-content">
            <div class="sidebar-header">
                <div class="sidebar-title">System Stats</div>
                <button id="sidebar-close" class="sidebar-close">&times;</button>
            </div>
            <div class="refresh-indicator" id="refresh_indicator">Auto-refresh 3s</div>
            <div class="sidebar-section">
                <div class="sidebar-stats">
                    <div class="sidebar-stat">
                        <div class="sidebar-stat-label">COMMUNICATIONS</div>
                        <div class="sidebar-stat-value" id="sidebar_total_communications">0</div>
                    </div>
                    <div class="sidebar-stat">
                        <div class="sidebar-stat-label">ACTIVE AGENTS</div>
                        <div class="sidebar-stat-value" id="sidebar_active_agents">0</div>
                    </div>
                    <div class="sidebar-stat">
                        <div class="sidebar-stat-label">API CALLS</div>
                        <div class="sidebar-stat-value" id="sidebar_api_calls">0</div>
                    </div>
                </div>
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-title">Registered Agents</div>
                <div class="sidebar-agents" id="sidebar_agents_display">
                    <div class="sidebar-agent">
                        <div class="sidebar-agent-name">Loading agents...</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="terminal">
        <div class="section">
            <div class="prompt">communication log</div>
            <div class="communications" id="communications_display">
                <div class="comm-item">
                    <div class="comm-timestamp">Loading communications...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Wait for DOM to be ready
        document.addEventListener('DOMContentLoaded', function() {
            // Sidebar functionality
            const sidebarToggle = document.getElementById('sidebar-toggle');
            const sidebarClose = document.getElementById('sidebar-close');
            const sidebar = document.getElementById('sidebar');
            
            function toggleSidebar() {
                sidebar.classList.toggle('open');
            }
            
            function closeSidebar() {
                sidebar.classList.remove('open');
            }
            
            if (sidebarToggle && sidebar) {
                sidebarToggle.addEventListener('click', toggleSidebar);
            } else {
                console.error('Sidebar toggle elements not found');
            }
            
            if (sidebarClose && sidebar) {
                sidebarClose.addEventListener('click', closeSidebar);
            } else {
                console.error('Sidebar close elements not found');
            }
            
            // Close sidebar when clicking outside
            document.addEventListener('click', function(event) {
                if (sidebar.classList.contains('open') && 
                    !sidebar.contains(event.target) && 
                    !sidebarToggle.contains(event.target)) {
                    closeSidebar();
                }
            });
        });

        async function updateTrafficLights() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                
                const apiLight = document.getElementById('api_light');
                const managerLight = document.getElementById('manager_light');
                
                if (data.monitoring_website === 'healthy' && data.backend_connection === 'connected') {
                    // API Server is online
                    apiLight.className = 'status-light online';
                    
                    // Check if AI Manager agent is registered and online
                    try {
                        const agentsResponse = await fetch('/api/agents');
                        const agentsData = await agentsResponse.json();
                        const contextManager = agentsData.find(agent => agent.id === 'ai-manager');
                        
                        if (contextManager && contextManager.status === 'online') {
                            managerLight.className = 'status-light online';
                        } else {
                            managerLight.className = 'status-light warning';
                        }
                    } catch (error) {
                        managerLight.className = 'status-light warning';
                    }
                } else {
                    // API Server offline
                    apiLight.className = 'status-light offline';
                    managerLight.className = 'status-light offline';
                }
            } catch (error) {
                // API Server offline
                document.getElementById('api_light').className = 'status-light offline';
                document.getElementById('manager_light').className = 'status-light offline';
            }
        }

        async function refreshData() {
            try {
                await updateTrafficLights();
                
                const statsResponse = await fetch('/api/stats');
                const stats = await statsResponse.json();
                
                // Update sidebar stats
                document.getElementById('sidebar_total_communications').textContent = stats.total_communications;
                document.getElementById('sidebar_active_agents').textContent = stats.active_agents;
                document.getElementById('sidebar_api_calls').textContent = stats.api_calls;

                const agentsResponse = await fetch('/api/agents');
                const agents = await agentsResponse.json();
                
                // Update sidebar agents
                const sidebarAgentsDiv = document.getElementById('sidebar_agents_display');
                sidebarAgentsDiv.innerHTML = '';
                
                // Filter out the AI Manager from the agents list (shown in traffic light)
                const otherAgents = agents.filter(agent => agent.id !== 'ai-manager');
                
                if (otherAgents.length === 0) {
                    sidebarAgentsDiv.innerHTML = '<div class="sidebar-agent"><div class="sidebar-agent-name">No other agents registered</div></div>';
                } else {
                    otherAgents.forEach(agent => {
                        const statusClass = agent.status === 'online' ? 'online' : 'offline';
                        const agentDiv = document.createElement('div');
                        agentDiv.className = 'sidebar-agent';
                        agentDiv.innerHTML = `
                            <div class="sidebar-agent-name">${agent.id}</div>
                            <div class="sidebar-agent-status ${statusClass}">${agent.status}</div>
                        `;
                        sidebarAgentsDiv.appendChild(agentDiv);
                    });
                }

                const commsResponse = await fetch('/api/communications');
                const communications = await commsResponse.json();
                const commsDiv = document.getElementById('communications_display');
                commsDiv.innerHTML = '';
                
                if (communications.length === 0) {
                    commsDiv.innerHTML = '<div class="comm-item"><div class="comm-timestamp">No communications yet</div></div>';
                } else {
                    // Sort by timestamp (newest first) without mutating original array
                    const sortedComms = [...communications].sort((a, b) => 
                        new Date(b.timestamp) - new Date(a.timestamp)
                    );
                    
                    sortedComms.forEach(comm => {
                        const commDiv = document.createElement('div');
                        // Add agent-specific CSS class for color coding
                        const agentClass = comm.from_agent.replace(/[^a-zA-Z0-9-]/g, '');
                        commDiv.className = `comm-item ${agentClass}`;
                        
                        // Get agent colors for text styling
                        const getAgentColor = (agentName) => {
                            const cleanName = agentName.replace(/[^a-zA-Z0-9-]/g, '');
                            switch(cleanName) {
                                case 'ai-manager': return '#00ff00';
                                case 'blaze-agent': return '#ff6b35';
                                case 'maya-agent': return '#20b2aa';
                                default: return '#888888';
                            }
                        };
                        
                        const fromAgentColor = getAgentColor(comm.from_agent);
                        const toAgentColor = getAgentColor(comm.to_agent);
                        
                        commDiv.innerHTML = `
                            <div class="comm-timestamp">[${new Date(comm.timestamp).toLocaleTimeString()}]</div>
                            <div class="comm-sender">
                                <span style="color: ${fromAgentColor}">${comm.from_agent}</span> -> 
                                <span style="color: ${toAgentColor}">${comm.to_agent}</span>
                            </div>
                            <div class="comm-message">${comm.message}</div>
                        `;
                        commsDiv.appendChild(commDiv);
                    });
                }

            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }

        setInterval(refreshData, 3000);
        refreshData();
    </script>
</body>
</html>
        """
        
    def start(self, port=8000):
        """Start the monitoring website"""
        logger.info("Starting AI Communication System Monitoring Website")
        logger.info(f"Monitoring website: http://localhost:{port}")
        logger.info(f"Backend API: {self.backend_url}")
        
        try:
            self.app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
        except KeyboardInterrupt:
            logger.info("Monitoring website stopped by user")

def main():
    """Main function"""
    website = MonitoringWebsite()
    website.start()

if __name__ == "__main__":
    main()
