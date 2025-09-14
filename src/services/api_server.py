#!/usr/bin/env python3
"""
Simplified Backend REST API Service for AI Communication System
Runs on port 5000 - handles agent communication monitoring only
"""

import json
import os
import time
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Web framework
from flask import Flask, jsonify, request
from flask_cors import CORS

# Database
try:
    from .database import SupabaseDatabaseManager
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from services.database import SupabaseDatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleBackendAPIService:
    """Simplified backend REST API service for AI agent communication monitoring"""
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Temporarily disable database integration
        logger.info("⚠️ Database integration temporarily disabled for testing")
        self.db = None
        
        # Load existing data from database
        self.registered_agents = {}
        self.communication_log = []
        self._load_from_database()
        
        if self.db:
            self.system_stats = self.db.get_system_stats()
        else:
            self.system_stats = {"total_communications": 0, "active_agents": 0, "api_calls": 0}
        
        self._setup_routes()
        logger.info("Simple Backend REST API Service initialized")
    
    def _load_from_database(self):
        """Load existing data from database"""
        if not self.db:
            logger.info("No database connection - starting with empty data")
            return
            
        try:
            # Load agents
            agents = self.db.get_agents()
            for agent in agents:
                self.registered_agents[agent['id']] = {
                    'id': agent['id'],
                    'name': agent['name'],
                    'description': agent['description'],
                    'capabilities': agent['capabilities'],
                    'status': agent['status'],
                    'last_heartbeat': agent['last_heartbeat'],
                    'registered_at': agent['registered_at']
                }
            
            # Load recent communications (last 1000)
            self.communication_log = self.db.get_communications(limit=1000)
            
            logger.info(f"Loaded {len(self.registered_agents)} agents and {len(self.communication_log)} communications from database")
            
        except Exception as e:
            logger.error(f"Failed to load data from database: {e}")
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "active_agents": f"{len([agent for agent, data in {k: v for k, v in self.registered_agents.items() if k != 'ai-context-manager'}.items() if data['status'] == 'online'])}/{len([agent for agent in self.registered_agents.keys() if agent != 'ai-context-manager'])}",
                "total_communications": self.system_stats["total_communications"]
            })
        
        @self.app.route('/api/stats', methods=['GET'])
        def get_stats():
            """Get system statistics"""
            self.system_stats["api_calls"] += 1
            self.system_stats["last_update"] = datetime.now().isoformat()
            
            # Count active agents excluding the core AI Manager
            non_core_agents = {k: v for k, v in self.registered_agents.items() if k != 'ai-context-manager'}
            online_count = len([agent for agent, data in non_core_agents.items() if data["status"] == "online"])
            total_count = len(non_core_agents)
            self.system_stats["active_agents"] = f"{online_count}/{total_count}"
            
            return jsonify(self.system_stats)
        
        @self.app.route('/api/agents', methods=['GET'])
        def get_agents():
            """Get list of registered agents"""
            self.system_stats["api_calls"] += 1
            agents = []
            for agent_id, agent_data in self.registered_agents.items():
                agents.append({
                    "id": agent_id,
                    "status": agent_data["status"],
                    "last_seen": agent_data.get("last_seen", "unknown"),
                    "capabilities": agent_data.get("capabilities", [])
                })
            return jsonify(agents)
        
        @self.app.route('/api/agents/register', methods=['POST'])
        def register_agent():
            """Register a new agent"""
            self.system_stats["api_calls"] += 1
            data = request.get_json()
            
            agent_id = data.get('agent_id')
            agent_name = data.get('agent_name', agent_id)
            description = data.get('description', '')
            capabilities = data.get('capabilities', [])
            
            if not agent_id:
                return jsonify({"error": "agent_id required"}), 400
            
            # Register in database
            agent_data = {
                'id': agent_id,
                'name': agent_name,
                'description': description,
                'capabilities': capabilities
            }
            
            # Register in database if available
            db_success = True
            if self.db:
                try:
                    db_success = self.db.register_agent(agent_data)
                except Exception as e:
                    logger.warning(f"Database registration failed: {e}")
                    db_success = True  # Continue without database
            
            if db_success:
                # Update in-memory cache
                self.registered_agents[agent_id] = {
                    "id": agent_id,
                    "name": agent_name,
                    "description": description,
                    "status": "online",
                    "last_heartbeat": datetime.now().isoformat(),
                    "capabilities": capabilities,
                    "registered_at": datetime.now().isoformat()
                }
            
            # Count active agents excluding the core AI Manager
            non_core_agents = {k: v for k, v in self.registered_agents.items() if k != 'ai-context-manager'}
            online_count = len([agent for agent, data in non_core_agents.items() if data["status"] == "online"])
            total_count = len(non_core_agents)
            self.system_stats["active_agents"] = f"{online_count}/{total_count}"
            
            logger.info(f"Agent {agent_id} registered")
            
            return jsonify({"status": "registered", "agent_id": agent_id})
        
        @self.app.route('/api/agents/<agent_id>/heartbeat', methods=['POST'])
        def agent_heartbeat(agent_id):
            """Agent heartbeat to maintain online status"""
            self.system_stats["api_calls"] += 1
            
            if agent_id in self.registered_agents:
                self.registered_agents[agent_id]["last_seen"] = datetime.now().isoformat()
                self.registered_agents[agent_id]["status"] = "online"
                return jsonify({"status": "heartbeat_received"})
            else:
                return jsonify({"error": "Agent not found"}), 404
        
        @self.app.route('/api/agents/<agent_id>/send', methods=['POST'])
        def send_message(agent_id):
            """Send a message from one agent to another"""
            self.system_stats["api_calls"] += 1
            data = request.get_json()
            
            target_agent = data.get('target_agent')
            message = data.get('message')
            
            if not target_agent or not message:
                return jsonify({"error": "target_agent and message required"}), 400
            
            # Log the communication
            communication = {
                "id": f"comm_{int(time.time())}",
                "timestamp": datetime.now().isoformat(),
                "sender": agent_id,
                "target": target_agent,
                "message": message,
                "type": "direct_message"
            }
            
            self.communication_log.append(communication)
            self.system_stats["total_communications"] += 1
            
            logger.info(f"Message from {agent_id} to {target_agent}: {message}")
            
            return jsonify({"status": "message_sent", "communication_id": communication["id"]})
        
        @self.app.route('/api/agents/<agent_id>/broadcast', methods=['POST'])
        def broadcast_message(agent_id):
            """Broadcast a message to all agents"""
            self.system_stats["api_calls"] += 1
            data = request.get_json()
            
            message = data.get('message')
            if not message:
                return jsonify({"error": "message required"}), 400
            
            # Log the broadcast
            communication = {
                "id": f"broadcast_{int(time.time())}",
                "timestamp": datetime.now().isoformat(),
                "sender": agent_id,
                "target": "all_agents",
                "message": message,
                "type": "broadcast"
            }
            
            self.communication_log.append(communication)
            self.system_stats["total_communications"] += 1
            
            logger.info(f"Broadcast from {agent_id}: {message}")
            
            return jsonify({"status": "broadcast_sent", "communication_id": communication["id"]})
        
        @self.app.route('/api/communications/send', methods=['POST'])
        def send_communication():
            """Send a communication message"""
            self.system_stats["api_calls"] += 1
            data = request.get_json()
            
            agent_id = data.get('agent_id')
            message = data.get('message')
            target_agent = data.get('target_agent')
            
            if not agent_id or not message:
                return jsonify({"error": "agent_id and message required"}), 400
            
            # Create communication entry
            communication = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "from_agent": agent_id,
                "to_agent": target_agent or "broadcast",
                "message": message,
                "type": "direct" if target_agent else "broadcast"
            }
            
            self.communication_log.append(communication)
            self.system_stats["total_communications"] += 1
            
            logger.info(f"Communication from {agent_id} to {target_agent or 'broadcast'}: {message}")
            
            return jsonify({"status": "message_sent", "communication_id": communication["id"]})
        
        @self.app.route('/api/communications', methods=['GET'])
        def get_communications():
            """Get communication log"""
            self.system_stats["api_calls"] += 1
            
            # Return last 50 communications
            recent_communications = self.communication_log[-50:] if len(self.communication_log) > 50 else self.communication_log
            return jsonify(recent_communications)
        
        @self.app.route('/api/agents/<agent_id>/messages', methods=['GET'])
        def get_agent_messages(agent_id):
            """Get messages for a specific agent"""
            self.system_stats["api_calls"] += 1
            
            # Filter messages for this agent
            agent_messages = []
            for comm in self.communication_log:
                if comm.get('to_agent') == agent_id or comm.get('to_agent') == 'broadcast':
                    agent_messages.append(comm)
            
            # Return last 20 messages for this agent
            recent_messages = agent_messages[-20:] if len(agent_messages) > 20 else agent_messages
            return jsonify(recent_messages)
        
        @self.app.route('/api/agents/<agent_id>/status', methods=['PUT'])
        def update_agent_status(agent_id):
            """Update agent status"""
            self.system_stats["api_calls"] += 1
            data = request.get_json()
            
            status = data.get('status')
            if not status:
                return jsonify({"error": "status required"}), 400
            
            if agent_id in self.registered_agents:
                self.registered_agents[agent_id]["status"] = status
                self.registered_agents[agent_id]["last_seen"] = datetime.now().isoformat()
                return jsonify({"status": "updated"})
            else:
                return jsonify({"error": "Agent not found"}), 404
        
        @self.app.route('/api/agents/activity', methods=['GET'])
        def get_agent_activity():
            """Get agent activity status"""
            self.system_stats["api_calls"] += 1
            
            activity_data = {}
            for agent_id, agent_data in self.registered_agents.items():
                activity_data[agent_id] = {
                    "status": agent_data.get("activity_status", "idle"),
                    "last_activity": agent_data.get("last_activity", agent_data.get("last_seen", "unknown"))
                }
            
            return jsonify({"activity": activity_data})
        
        @self.app.route('/api/pulse', methods=['GET'])
        def get_pulse_updates():
            """Get pulse updates"""
            self.system_stats["api_calls"] += 1
            
            # Return empty list for now - pulse updates will be added by agents
            return jsonify([])
        
        @self.app.route('/api/pulse', methods=['POST'])
        def add_pulse_update():
            """Add a pulse update"""
            self.system_stats["api_calls"] += 1
            data = request.get_json()
            
            pulse_update = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "agent_id": data.get("agent_id", "unknown"),
                "message": data.get("message", ""),
                "status": data.get("status", "info")
            }
            
            # For now, just log it - in a real implementation, this would be stored
            logger.info(f"Pulse update from {pulse_update['agent_id']}: {pulse_update['message']}")
            
            return jsonify(pulse_update)
        
        @self.app.route('/api/communications/clear', methods=['DELETE'])
        def clear_communications():
            """Clear communication log"""
            self.system_stats["api_calls"] += 1
            
            self.communication_log.clear()
            self.system_stats["total_communications"] = 0
            
            logger.info("Communication log cleared")
            
            return jsonify({"status": "cleared"})
        
    
    def cleanup_inactive_agents(self):
        """Mark agents as offline if they haven't sent heartbeat in 30 seconds"""
        cutoff_time = datetime.now() - timedelta(seconds=30)
        
        for agent_id, agent_data in self.registered_agents.items():
            last_seen = datetime.fromisoformat(agent_data["last_seen"])
            if last_seen < cutoff_time and agent_data["status"] == "online":
                agent_data["status"] = "offline"
                logger.info(f"Agent {agent_id} marked as offline")
    
    def start(self, port=5000):
        """Start the backend API service"""
        logger.info("Starting Simple Backend REST API Service")
        logger.info(f"Starting Backend API on port {port}")
        logger.info(f"API endpoints: http://localhost:{port}/api/")
        logger.info(f"Health check: http://localhost:{port}/health")
        
        # Start cleanup thread
        import threading
        def cleanup_thread():
            while True:
                time.sleep(10)  # Check every 10 seconds
                self.cleanup_inactive_agents()
        
        cleanup_thread = threading.Thread(target=cleanup_thread, daemon=True)
        cleanup_thread.start()
        
        self.app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    service = SimpleBackendAPIService()
    service.start()
