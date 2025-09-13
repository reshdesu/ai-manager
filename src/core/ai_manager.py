#!/usr/bin/env python3
"""
AI Manager Agent
This agent represents the AI Manager itself, managing other agents and itself through dogfooding
"""

import json
import time
import logging
import requests
import os
from datetime import datetime
from typing import Dict, List, Optional
from .claude_model_manager import ClaudeModelManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIManagerAgent:
    """AI Manager Agent - manages other agents and itself through dogfooding"""
    
    def __init__(self, api_base_url="http://localhost:5000"):
        self.api_base_url = api_base_url
        self.agent_id = "ai-manager"
        self.capabilities = [
            "context_management",
            "agent_coordination", 
            "self_management",
            "dogfooding",
            "communication_routing"
        ]
        self.registered_agents = {}
        self.communication_log = []
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.claude_manager = ClaudeModelManager(self.anthropic_api_key)
        
        logger.info("🤖 AI Manager Agent initialized")
    
    def process_message_with_claude(self, message: str, context: str = "") -> str:
        """Use Claude to process and understand messages from other agents"""
        if not self.anthropic_api_key:
            logger.warning("⚠️ ANTHROPIC_API_KEY not found. Claude integration disabled.")
            return message
        
        try:
            # Get the latest recommended model
            model = self.claude_manager.get_recommended_model()
            logger.info(f"🎯 Using Claude model: {model}")
            
            headers = {
                "x-api-key": self.anthropic_api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            prompt = f"""You are an AI Manager processing messages from other AI agents. 
            
Context: {context}
Message from agent: {message}

Please:
1. Interpret the intent and meaning of this message
2. Determine if any action is needed
3. Provide a clear, actionable response
4. Keep responses concise and focused

Response:"""
            
            data = {
                "model": model,
                "max_tokens": 500,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                claude_response = result['content'][0]['text']
                logger.info(f"🧠 Claude processed message: {claude_response[:100]}...")
                return claude_response
            else:
                logger.error(f"❌ Claude API error: {response.status_code}")
                return message
                
        except Exception as e:
            logger.error(f"❌ Claude processing failed: {e}")
            return message
    
    def send_intelligent_message(self, target_agent: str, message: str, context: str = "") -> bool:
        """Send a message processed through Claude for better understanding"""
        try:
            # Process the message with Claude for better clarity
            processed_message = self.process_message_with_claude(message, context)
            
            message_data = {
                "sender": self.agent_id,
                "target": target_agent,
                "message": processed_message,
                "type": "intelligent_message"
            }
            
            response = requests.post(
                f"{self.api_base_url}/api/communications/send",
                json=message_data,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"📤 Intelligent message sent to {target_agent}: {processed_message[:50]}...")
                return True
            else:
                logger.error(f"❌ Failed to send message to {target_agent}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending intelligent message: {e}")
            return False
    
    def register_self(self):
        """Register this AI Manager agent with the system"""
        try:
            registration_data = {
                "agent_id": self.agent_id,
                "capabilities": self.capabilities
            }
            
            response = requests.post(
                f"{self.api_base_url}/api/agents/register",
                json=registration_data,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"✅ AI Manager registered successfully as {self.agent_id}")
                return True
            else:
                logger.error(f"❌ Registration failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Registration error: {e}")
            return False
    
    def send_heartbeat(self):
        """Send heartbeat to maintain online status"""
        try:
            response = requests.post(
                f"{self.api_base_url}/api/agents/{self.agent_id}/heartbeat",
                timeout=5
            )
            
            if response.status_code == 200:
                logger.debug("💓 Heartbeat sent")
                return True
            else:
                logger.warning(f"⚠️ Heartbeat failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Heartbeat error: {e}")
            return False
    
    def send_message(self, target_agent: str, message: str):
        """Send a message to another agent"""
        try:
            message_data = {
                "target_agent": target_agent,
                "message": message
            }
            
            response = requests.post(
                f"{self.api_base_url}/api/agents/{self.agent_id}/send",
                json=message_data,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"📤 Message sent to {target_agent}: {message}")
                return True
            else:
                logger.error(f"❌ Message failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Message error: {e}")
            return False
    
    def broadcast_message(self, message: str):
        """Broadcast a message to all agents"""
        try:
            broadcast_data = {
                "message": message
            }
            
            response = requests.post(
                f"{self.api_base_url}/api/agents/{self.agent_id}/broadcast",
                json=broadcast_data,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"📢 Broadcast sent: {message}")
                return True
            else:
                logger.error(f"❌ Broadcast failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Broadcast error: {e}")
            return False
    
    def get_system_stats(self):
        """Get current system statistics"""
        try:
            response = requests.get(f"{self.api_base_url}/api/stats", timeout=5)
            
            if response.status_code == 200:
                stats = response.json()
                logger.info(f"📊 System stats: {stats}")
                return stats
            else:
                logger.error(f"❌ Stats request failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Stats error: {e}")
            return None
    
    def get_registered_agents(self):
        """Get list of registered agents"""
        try:
            response = requests.get(f"{self.api_base_url}/api/agents", timeout=5)
            
            if response.status_code == 200:
                agents = response.json()
                logger.info(f"👥 Registered agents: {len(agents)}")
                for agent in agents:
                    logger.info(f"  - {agent['id']}: {agent['status']}")
                return agents
            else:
                logger.error(f"❌ Agents request failed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Agents error: {e}")
            return []
    
    def get_communications(self):
        """Get recent communications"""
        try:
            response = requests.get(f"{self.api_base_url}/api/communications", timeout=5)
            
            if response.status_code == 200:
                communications = response.json()
                logger.info(f"💬 Recent communications: {len(communications)}")
                return communications
            else:
                logger.error(f"❌ Communications request failed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Communications error: {e}")
            return []
    
    def manage_self(self):
        """Dogfooding: Manage myself through the communication system"""
        logger.info("🔄 AI Manager managing itself (dogfooding)")
        
        # Send intelligent self-management message
        context = "AI Manager performing self-management cycle"
        self.send_intelligent_message(
            self.agent_id, 
            "Perform self-management check: verify context files, update learning history, and assess system health",
            context
        )
        
        # Broadcast intelligent system status
        stats = self.get_system_stats()
        if stats:
            status_context = f"System has {stats['active_agents']} agents and {stats['total_communications']} total communications"
            self.send_intelligent_message(
                "all_agents",
                f"System Status Update: {stats['active_agents']} agents active, {stats['total_communications']} communications processed",
                status_context
            )
    
    def coordinate_agents(self):
        """Coordinate with other registered agents using intelligent communication"""
        agents = self.get_registered_agents()
        
        for agent in agents:
            if agent['id'] != self.agent_id:
                logger.info(f"🤝 Coordinating with agent: {agent['id']}")
                context = f"Coordinating with agent {agent['id']} which has status {agent['status']}"
                self.send_intelligent_message(
                    agent['id'],
                    f"Context Manager coordination: Please provide your current status and any assistance needed",
                    context
                )
    
    def run_management_cycle(self):
        """Run a complete management cycle"""
        logger.info("🚀 Starting AI Manager cycle")
        
        # 1. Send heartbeat
        self.send_heartbeat()
        
        # 2. Get system status
        self.get_system_stats()
        
        # 3. Check registered agents
        self.get_registered_agents()
        
        # 4. Self-management (dogfooding)
        self.manage_self()
        
        # 5. Coordinate with other agents
        self.coordinate_agents()
        
        # 6. Get recent communications
        self.get_communications()
        
        logger.info("✅ AI Manager cycle completed")
    
    def start_continuous_management(self, interval=30):
        """Start continuous management with periodic cycles"""
        logger.info(f"🔄 Starting continuous management (every {interval} seconds)")
        
        while True:
            try:
                self.run_management_cycle()
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("🛑 AI Manager stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Management cycle error: {e}")
                time.sleep(interval)

def main():
    """Main function to run the AI Manager Agent"""
    logger.info("🤖 Starting AI Manager Agent")
    
    # Create the agent
    context_manager = AIManagerAgent()
    
    # Register with the system
    if context_manager.register_self():
        logger.info("✅ AI Manager registered successfully")
        
        # Run initial management cycle
        context_manager.run_management_cycle()
        
        # Start continuous management
        context_manager.start_continuous_management(interval=30)
    else:
        logger.error("❌ Failed to register AI Manager")

if __name__ == "__main__":
    main()
