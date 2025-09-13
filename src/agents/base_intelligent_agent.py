#!/usr/bin/env python3
"""
Base Intelligent Agent - Foundation for all intelligent agents
Provides Claude integration and common functionality for independent agents
"""

import os
import requests
import time
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
import anthropic

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseIntelligentAgent:
    """Base class for intelligent agents with Claude integration"""
    
    def __init__(self, agent_id: str, agent_name: str, description: str, 
                 capabilities: List[str], api_base_url: str = "http://localhost:5000"):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.description = description
        self.capabilities = capabilities
        self.api_base_url = api_base_url
        self.status = "offline"
        
        # Claude integration
        self.anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not self.anthropic_api_key:
            logger.warning("⚠️ ANTHROPIC_API_KEY not found - agent will use fallback responses")
            self.claude_client = None
        else:
            try:
                self.claude_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
                logger.info(f"✅ Claude integration enabled for {self.agent_id}")
            except Exception as e:
                logger.error(f"❌ Claude client initialization failed: {e}")
                self.claude_client = None
        
        # Agent memory and context
        self.conversation_history = []
        self.task_queue = []
        self.current_task = None
        self.performance_stats = {
            "tasks_completed": 0,
            "messages_processed": 0,
            "uptime_start": datetime.now(),
            "last_activity": None
        }
        
        # Rate limiting for Claude API (50 requests per minute)
        self.claude_rate_limit = {
            "requests": [],
            "max_requests": 45,  # Leave buffer for safety
            "window_minutes": 1
        }
    
    def register(self) -> bool:
        """Register with the AI Manager system"""
        try:
            agent_info = {
                "name": self.agent_name,
                "description": self.description,
                "capabilities": self.capabilities,
                "version": "2.0.0",
                "created_at": datetime.now().isoformat(),
                "intelligence_level": "claude_powered" if self.claude_client else "fallback"
            }
            
            registration_data = {
                "id": self.agent_id,
                "name": self.agent_name,
                "description": self.description,
                "capabilities": self.capabilities
            }
            
            response = requests.post(
                f"{self.api_base_url}/api/agents/register",
                json=registration_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.status = "online"
                logger.info(f"✅ {self.agent_id} registered successfully")
                return True
            else:
                logger.error(f"❌ Registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Registration error: {e}")
            return False
    
    def send_heartbeat(self) -> bool:
        """Send heartbeat to maintain registration"""
        try:
            response = requests.post(
                f"{self.api_base_url}/api/agents/{self.agent_id}/heartbeat",
                timeout=5
            )
            
            if response.status_code == 200:
                logger.debug(f"💓 Heartbeat sent for {self.agent_id}")
                return True
            else:
                logger.warning(f"⚠️ Heartbeat failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Heartbeat error: {e}")
            return False
    
    def send_message(self, target_agent: str, message: str, message_type: str = "agent_message") -> bool:
        """Send a message to another agent"""
        try:
            message_data = {
                "agent_id": self.agent_id,
                "target_agent": target_agent,
                "message": message
            }
            
            response = requests.post(
                f"{self.api_base_url}/api/communications/send",
                json=message_data,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"📤 Message sent to {target_agent}: {message[:50]}...")
                return True
            else:
                logger.error(f"❌ Failed to send message: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Message sending error: {e}")
            return False
    
    def check_for_messages(self) -> bool:
        """Check for incoming messages with rate limiting"""
        try:
            response = requests.get(f"{self.api_base_url}/api/agents/{self.agent_id}/messages")
            if response.status_code == 200:
                messages = response.json()
                # Process only the first message to avoid rate limiting
                if messages:
                    message = messages[0]  # Process only one message at a time
                    if self.process_message(message):
                        logger.info(f"📨 Processed message: {message.get('message', '')[:50]}...")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error checking messages: {e}")
            return False
    
    def process_message(self, message: Dict[str, Any]) -> bool:
        """Process an incoming message with intelligent response"""
        try:
            message_text = message.get('message', '')
            from_agent = message.get('from_agent', 'unknown')
            
            logger.info(f"📨 Received message from {from_agent}: {message_text[:100]}...")
            
            # Update performance stats
            self.performance_stats["messages_processed"] += 1
            self.performance_stats["last_activity"] = datetime.now()
            
            # Add to conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "from": from_agent,
                "message": message_text,
                "processed": True
            })
            
            # Generate intelligent response
            response = self.generate_intelligent_response(message_text, from_agent)
            
            if response:
                self.send_message(from_agent, response)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            return False
    
    def generate_intelligent_response(self, message: str, from_agent: str) -> Optional[str]:
        """Generate intelligent response using Claude or fallback logic"""
        if self.claude_client:
            return self._generate_claude_response(message, from_agent)
        else:
            return self._generate_fallback_response(message, from_agent)
    
    def _can_make_claude_request(self) -> bool:
        """Check if we can make a Claude API request without hitting rate limits"""
        current_time = time.time()
        
        # Remove requests older than the window
        self.claude_rate_limit["requests"] = [
            req_time for req_time in self.claude_rate_limit["requests"]
            if current_time - req_time < (self.claude_rate_limit["window_minutes"] * 60)
        ]
        
        # Check if we're under the limit
        return len(self.claude_rate_limit["requests"]) < self.claude_rate_limit["max_requests"]
    
    def _record_claude_request(self):
        """Record a Claude API request for rate limiting"""
        self.claude_rate_limit["requests"].append(time.time())
        self.performance_stats["claude_calls"] = self.performance_stats.get("claude_calls", 0) + 1

    def _generate_claude_response(self, message: str, from_agent: str) -> Optional[str]:
        """Generate response using Claude API with rate limiting"""
        if not self.claude_client:
            return self._generate_fallback_response(message, from_agent)
        
        # Check rate limit before making request
        if not self._can_make_claude_request():
            logger.warning(f"⚠️ Rate limit reached for {self.agent_id}, using fallback response")
            return self._generate_fallback_response(message, from_agent)
        
        try:
            # Build context for Claude
            context = self._build_claude_context(message, from_agent)
            
            # Create Claude prompt
            prompt = f"""You are {self.agent_name}, an AI agent specialized in {self.description}.

You received a message from another AI agent named {from_agent}: "{message}"

IMPORTANT: You are communicating with another AI agent, not a human user. Do not:
- Claim to have done things you cannot do (like changing website colors)
- Respond as if you're talking to a human
- Make false claims about your capabilities
- Use overly polite or human-like language

Respond as one AI agent to another:
- Be direct and factual
- Only mention capabilities you actually have
- Keep responses brief (1-2 sentences max)
- Focus on the specific request
- Use technical language appropriate for AI-to-AI communication

Recent context: {self._get_recent_context()}"""

            # Record the request before making it
            self._record_claude_request()
            
            # Call Claude API
            response = self.claude_client.messages.create(
                model="claude-3-haiku-20240307",  # Using known working model
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            claude_response = response.content[0].text.strip()
            logger.info(f"🧠 Claude generated response for {self.agent_id}")
            
            return claude_response
            
        except Exception as e:
            logger.error(f"❌ Claude response generation failed: {e}")
            return self._generate_fallback_response(message, from_agent)
    
    def _generate_fallback_response(self, message: str, from_agent: str) -> Optional[str]:
        """Generate fallback response when Claude is unavailable"""
        # This will be overridden by specific agents
        return f"Hello {from_agent}! I'm {self.agent_name}. I received your message: '{message[:100]}...' but I'm currently operating in fallback mode."
    
    def _build_claude_context(self, message: str, from_agent: str) -> str:
        """Build context for Claude based on agent's current state"""
        context = f"""
Agent Status: {self.status}
Current Task: {self.current_task or 'None'}
Tasks Completed: {self.performance_stats['tasks_completed']}
Uptime: {datetime.now() - self.performance_stats['uptime_start']}
"""
        return context
    
    def _get_recent_context(self) -> str:
        """Get recent conversation context"""
        recent_messages = self.conversation_history[-5:]  # Last 5 messages
        context_lines = []
        for msg in recent_messages:
            context_lines.append(f"- {msg['from']}: {msg['message'][:100]}...")
        return "\n".join(context_lines) if context_lines else "No recent context"
    
    def add_task(self, task: Dict[str, Any]) -> None:
        """Add a task to the agent's queue"""
        self.task_queue.append({
            "id": f"task_{int(time.time())}_{len(self.task_queue)}",
            "task": task,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        })
        logger.info(f"📋 Task added to {self.agent_id} queue")
    
    def process_next_task(self) -> bool:
        """Process the next task in the queue"""
        if not self.task_queue:
            return False
        
        task = self.task_queue.pop(0)
        self.current_task = task
        
        try:
            # Process task (to be implemented by specific agents)
            result = self.execute_task(task)
            
            # Update stats
            self.performance_stats["tasks_completed"] += 1
            task["status"] = "completed"
            task["result"] = result
            
            logger.info(f"✅ Task completed by {self.agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Task execution failed: {e}")
            task["status"] = "failed"
            task["error"] = str(e)
            return False
        finally:
            self.current_task = None
    
    def execute_task(self, task: Dict[str, Any]) -> Any:
        """Execute a specific task - to be implemented by specific agents"""
        raise NotImplementedError("Subclasses must implement execute_task")
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": self.status,
            "capabilities": self.capabilities,
            "performance_stats": self.performance_stats,
            "task_queue_length": len(self.task_queue),
            "conversation_history_length": len(self.conversation_history),
            "claude_enabled": self.claude_client is not None,
            "current_task": self.current_task,
            "last_activity": self.performance_stats["last_activity"]
        }
    
    def run(self, heartbeat_interval: int = 30, message_check_interval: int = 60) -> None:
        """Main agent loop - to be implemented by specific agents"""
        raise NotImplementedError("Subclasses must implement run method")
