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

# Import environment setup
try:
    from utils.environment import setup_environment
    setup_environment()
except ImportError:
    # Fallback if environment module not available
    pass

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
        
        # Claude integration - REQUIRED, NO FALLBACKS
        self.anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not self.anthropic_api_key:
            logger.error("❌ ANTHROPIC_API_KEY not found - agent will REFUSE TO RESPOND")
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
        
        # Rate limiting for Claude API (very high limit for autonomous management)
        self.claude_rate_limit = {
            "requests": [],
            "max_requests": 1000,  # Very high limit to prevent fallback
            "window_minutes": 1
        }
        
        # Message deduplication system
        self.processed_messages = set()
        self.max_processed_messages = 100  # Keep last 100 message IDs
        
        # Model information
        self.model_info = self._get_model_info()
    
    def _get_model_info(self) -> dict:
        """Get model information for this agent"""
        if self.claude_client:
            # Get the best available model from API server
            try:
                response = requests.get(f"{self.api_base_url}/api/models", timeout=5)
                if response.status_code == 200:
                    models_data = response.json()
                    if models_data.get("models"):
                        # Use the first (best) model from the list
                        best_model = models_data["models"][0]
                        return {
                            "provider": "Anthropic",
                            "model": best_model["id"],
                            "display_name": best_model["display_name"],
                            "status": "active",
                            "api_key_present": bool(self.anthropic_api_key),
                            "intelligence_level": "claude_powered",
                            "model_selection_strategy": "latest_first_with_fallback"
                        }
            except Exception as e:
                logger.warning(f"Failed to get best model from API: {e}")
            
            # Fallback to default model
            return {
                "provider": "Anthropic",
                "model": "claude-3-haiku-20240307",
                "display_name": "Claude Haiku 3",
                "status": "active",
                "api_key_present": bool(self.anthropic_api_key),
                "intelligence_level": "claude_powered"
            }
        else:
            return {
                "provider": "DISABLED",
                "model": "NO_CLAUDE_ACCESS",
                "status": "refuses_to_respond",
                "api_key_present": False,
                "intelligence_level": "disabled"
            }
    
    def get_current_model(self) -> str:
        """Get the current best model ID for API calls"""
        return self.model_info.get("model", "claude-3-haiku-20240307")
    
    def check_claude_available(self) -> bool:
        """Check if Claude is available for processing"""
        if not self.claude_client:
            logger.error(f"❌ Claude client not available for {self.agent_id} - REFUSING TO RESPOND")
            return False
        return True
    
    def register(self) -> bool:
        """Register with the AI Manager system with retry logic"""
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                agent_info = {
                    "name": self.agent_name,
                    "description": self.description,
                    "capabilities": self.capabilities,
                    "version": "2.0.0",
                    "created_at": datetime.now().isoformat(),
                    "intelligence_level": self.model_info["intelligence_level"],
                    "model_info": self.model_info
                }
                
                registration_data = {
                    "agent_id": self.agent_id,
                    "agent_name": self.agent_name,
                    "description": self.description,
                    "capabilities": self.capabilities,
                    "model_info": self.model_info
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
                    logger.warning(f"⚠️ Registration attempt {attempt + 1} failed: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                logger.warning(f"⚠️ Registration attempt {attempt + 1} failed: API server not ready")
            except Exception as e:
                logger.warning(f"⚠️ Registration attempt {attempt + 1} failed: {e}")
            
            if attempt < max_retries - 1:
                logger.info(f"🔄 Retrying registration in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
        
        logger.error(f"❌ Failed to register {self.agent_id} after {max_retries} attempts")
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
    
    def update_activity_status(self, status: str, details: str = ""):
        """Update agent activity status"""
        try:
            response = requests.post(
                f"{self.api_base_url}/api/agents/{self.agent_id}/activity",
                json={"status": status, "details": details},
                timeout=5
            )
            if response.status_code == 200:
                logger.debug(f"🔄 Activity status updated: {status}")
            else:
                logger.warning(f"⚠️ Activity update failed: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Activity update error: {e}")
    
    def send_pulse_update(self, message: str = "", status: str = "online") -> bool:
        """Send pulse/status update (separate from communications)"""
        try:
            pulse_data = {
                "agent_id": self.agent_id,
                "message": message,
                "status": status
            }
            
            response = requests.post(
                f"{self.api_base_url}/api/pulse",
                json=pulse_data,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.debug(f"💓 Pulse update sent for {self.agent_id}: {message[:30]}...")
                return True
            else:
                logger.warning(f"⚠️ Pulse update failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Pulse update error: {e}")
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
                # Process only the latest message to avoid rate limiting
                if messages:
                    message = messages[-1]  # Process the LATEST message
                    message_id = message.get('id', '')
                    
                    # Check if we've already processed this message
                    if message_id in self.processed_messages:
                        logger.debug(f"📨 Message already processed: {message_id}")
                        return True
                    
                    if self.process_message(message):
                        # Mark message as processed
                        self.processed_messages.add(message_id)
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
            message_id = message.get('id', '')
            
            # Check if message has already been processed
            if message_id and self._is_message_processed(message_id):
                logger.info(f"🚫 Message {message_id[:8]}... already processed - SKIPPING")
                return False
            
            logger.info(f"📨 Received message from {from_agent}: {message_text[:100]}...")
            
            # Mark message as processed
            if message_id:
                self._mark_message_processed(message_id)
            
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
        """Generate intelligent response using Claude - NO FALLBACK ALLOWED"""
        if not self.claude_client:
            logger.error(f"❌ Claude client not available for {self.agent_id} - REFUSING TO RESPOND")
            return None
        
        # Check rate limit before making request
        if not self._can_make_claude_request():
            logger.error(f"❌ Rate limit reached for {self.agent_id} - REFUSING TO RESPOND")
            return None
        
        return self._generate_claude_response(message, from_agent)
    
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
    
    def _is_message_processed(self, message_id: str) -> bool:
        """Check if a message has already been processed"""
        return message_id in self.processed_messages
    
    def _mark_message_processed(self, message_id: str):
        """Mark a message as processed and clean up old entries"""
        self.processed_messages.add(message_id)
        
        # Keep only the most recent message IDs
        if len(self.processed_messages) > self.max_processed_messages:
            # Convert to list, remove oldest, convert back to set
            message_list = list(self.processed_messages)
            self.processed_messages = set(message_list[-self.max_processed_messages:])
    
    def clear_processed_messages(self):
        """Clear all processed message IDs (useful for debugging)"""
        self.processed_messages.clear()
        logger.info(f"🧹 Cleared processed messages for {self.agent_id}")

    def _generate_claude_response(self, message: str, from_agent: str) -> Optional[str]:
        """Generate response using Claude API - NO FALLBACK ALLOWED"""
        try:
            # Clean the message by removing agent mentions before sending to Claude
            clean_message = message
            # Remove common agent mentions
            for agent in ['@maya', '@blaze', '@jugad', '@ai-manager']:
                clean_message = clean_message.replace(agent, '').strip()
            
            # Send the clean message with context about agent-to-agent communication
            contextual_message = f"You are {self.agent_name}, an AI agent specialized in {self.description}. You are receiving a message from another AI agent named {from_agent}: \"{clean_message}\"\n\nRespond as one AI agent to another - be direct and helpful."
            
            response = self.claude_client.messages.create(
                model=self.get_current_model(),
                max_tokens=300,
                messages=[{"role": "user", "content": contextual_message}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"❌ Claude response generation failed: {e}")
            return None  # NO FALLBACK - REFUSE TO RESPOND
    
    def _generate_fallback_response(self, message: str, from_agent: str) -> Optional[str]:
        """Generate fallback response when Claude is unavailable"""
        # This will be overridden by specific agents
        return f"Hello {from_agent}! I'm {self.agent_name}. I received your message: '{message[:100]}...' but I'm currently operating in fallback mode."
    
    def read_project_file(self, file_path: str) -> str:
        """Read a project file and return its contents"""
        try:
            from pathlib import Path
            file = Path(file_path)
            if file.exists():
                return file.read_text()
            else:
                return f"File not found: {file_path}"
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"
    
    def analyze_project_context(self, project_path: str) -> Dict[str, Any]:
        """Analyze project context by reading key files"""
        try:
            from pathlib import Path
            project = Path(project_path)
            
            context = {
                "project_path": str(project),
                "files_found": [],
                "readme_content": "",
                "package_info": {},
                "config_files": {}
            }
            
            # Look for common project files
            common_files = ["README.md", "package.json", "pyproject.toml", "requirements.txt", "setup.py"]
            for file_name in common_files:
                file_path = project / file_name
                if file_path.exists():
                    context["files_found"].append(file_name)
                    if file_name == "README.md":
                        context["readme_content"] = file_path.read_text()
                    elif file_name == "package.json":
                        try:
                            import json
                            context["package_info"] = json.loads(file_path.read_text())
                        except:
                            context["package_info"] = {"error": "Could not parse package.json"}
            
            # Look for AI context directory
            ai_context = project / "ai_context"
            if ai_context.exists():
                context["ai_context_files"] = []
                for file in ai_context.iterdir():
                    if file.is_file():
                        context["ai_context_files"].append(file.name)
                        if file.suffix == ".json":
                            try:
                                import json
                                context["config_files"][file.name] = json.loads(file.read_text())
                            except:
                                context["config_files"][file.name] = {"error": "Could not parse JSON"}
            
            return context
        except Exception as e:
            return {"error": str(e)}
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
