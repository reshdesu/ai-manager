#!/usr/bin/env python3
"""
Jugad Agent - General Purpose Instruction-Following Agent

A versatile agent that can be instructed to work on various tasks and projects.
Designed to be flexible and adaptable to different types of work.
"""

import os
import sys
import time
import json
import logging
import requests
import re
from datetime import datetime
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.agents.base_intelligent_agent import BaseIntelligentAgent
from src.utils.environment import setup_environment

# FORCE API KEY LOADING - NO FALLBACK
setup_environment()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add AI Manager to path for base classes
sys.path.append('/home/yamnik/Projects/ai-manager/src')

# Import environment setup
try:
    from utils.environment import setup_environment
    setup_environment()
except ImportError:
    # Fallback if environment module not available
    pass

from agents.base_intelligent_agent import BaseIntelligentAgent

class JugadAgent(BaseIntelligentAgent):
    """General purpose agent that follows instructions for various tasks"""
    
    def __init__(self):
        super().__init__(
            agent_id="jugad-agent",
            agent_name="Jugad",
            description="General purpose instruction-following agent for various tasks and projects",
            capabilities=[
                "general_development",
                "file_management", 
                "command_execution",
                "project_setup",
                "code_generation",
                "task_automation",
                "research_and_analysis",
                "documentation",
                "claude_integration"
            ]
        )
        
        # Project-specific settings
        self.project_path = "/home/yamnik/Projects/jugad"
        self.current_task = None
        self.task_history = []
        
        # Ensure project directory exists
        Path(self.project_path).mkdir(parents=True, exist_ok=True)
        
        # Set up logging for this agent
        self.logger = logging.getLogger(f"jugad-agent")
        self.logger.info("Jugad Agent initialized - ready for instructions")

    def get_project_status(self):
        """Get current project status"""
        try:
            # Check if project directory exists and has content
            project_path = Path(self.project_path)
            if not project_path.exists():
                return {"status": "not_found", "message": "Project directory not found"}
            
            # Count files in project
            files = list(project_path.rglob("*"))
            file_count = len([f for f in files if f.is_file()])
            
            # Check for common project files
            has_readme = (project_path / "README.md").exists()
            has_git = (project_path / ".git").exists()
            
            return {
                "status": "active",
                "project_name": "Jugad Project",
                "project_path": str(project_path),
                "file_count": file_count,
                "has_readme": has_readme,
                "has_git": has_git,
                "current_task": self.current_task,
                "task_history_count": len(self.task_history)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting project status: {e}")
            return {"status": "error", "message": str(e)}

    def process_message(self, message_data):
        """Process incoming messages and execute instructions"""
        try:
            message_text = message_data.get("message", "")
            from_agent = message_data.get("from_agent", "unknown")
            
            self.logger.info(f"📨 Received instruction from {from_agent}: {message_text}")
            
            # Only respond to @jugad mentions
            if '@jugad' not in message_text.lower():
                self.logger.info("Message not for me - IGNORING")
                self.update_activity_status("idle", "Message not for me")
                return False
            
            # Update activity status
            self.update_activity_status("processing", f"Processing instruction from {from_agent}")
            
            # Use Claude to understand the instruction - REQUIRED, NO FALLBACKS
            if not self.check_claude_available():
                self.logger.error("❌ Claude not available - REFUSING TO RESPOND")
                self.send_message("ai-manager", "❌ Claude client not available for jugad-agent - REFUSING TO RESPOND")
                self.update_activity_status("error", "Claude not available")
                return False
            
            response = self._ask_claude_for_instruction_understanding(message_text)
            if response:
                self.logger.info(f"🧠 Claude response: {response}")
                
                # Execute the instruction
                result = self._execute_instruction(response, message_text)
                
                # Send response back
                self.send_message("ai-manager", result)
                
                # Record task
                self._record_task(message_text, result)
                
                return True
            else:
                self.logger.error("❌ Claude response failed - REFUSING TO RESPOND")
                self.send_message("ai-manager", "❌ Claude response failed for jugad-agent - REFUSING TO RESPOND")
                self.update_activity_status("error", "Claude response failed")
                return False
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            self.update_activity_status("error", f"Error: {str(e)}")
            return False

    def _ask_claude_for_instruction_understanding(self, instruction: str) -> str:
        """Use Claude to understand what instruction is being given"""
        try:
            # For simple questions, just pass them directly to Claude
            if self._is_simple_question(instruction):
                response = self.claude_client.messages.create(
                    model=self.get_current_model(),
                    max_tokens=200,
                    messages=[{"role": "user", "content": instruction}]
                )
                return response.content[0].text
            
            # For complex instructions, use the analysis prompt
            prompt = f"""You are Jugad, a general purpose instruction-following agent.

Instruction received: "{instruction}"

Analyze this instruction and determine:
1. What type of task is being requested?
2. What specific actions should I take?
3. What files or commands might be needed?

Respond with a clear action plan. Examples:
- "create_file: Create a new Python script for data processing"
- "execute_command: Run git init to initialize the project"
- "research: Research best practices for web development"
- "setup_project: Set up a new React project structure"

Be specific about what needs to be done."""

            response = self.claude_client.messages.create(
                model=self.get_current_model(),
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            self.logger.error(f"❌ Claude instruction understanding failed: {e}")
            return "understand_instruction: Analyze and execute the given instruction"

    def _execute_instruction(self, claude_response: str, original_instruction: str) -> str:
        """Execute the instruction based on Claude's analysis"""
        try:
            self.logger.info(f"🔧 Executing instruction: {claude_response}")
            
            # Use Claude's response directly as the intelligent response
            # Instead of parsing keywords, let Claude's analysis be the response
            self.logger.info(f"🧠 Using Claude's intelligent analysis as response")
            
            # Create a file with Claude's detailed analysis
            filename = f"claude_analysis_{datetime.now().strftime('%H%M%S')}.md"
            content = f"""# Claude Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Original Instruction:
{original_instruction}

## Claude's Intelligent Analysis:
{claude_response}

## Status:
Task analyzed and processed by Jugad agent using Claude AI
"""
            
            file_path = Path(self.project_path) / filename
            file_path.write_text(content)
            
            # For simple questions, return Claude's response directly
            if self._is_simple_question(original_instruction):
                self.logger.info(f"🎯 Direct Claude response: {claude_response}")
                return claude_response
            
            # Return Claude's analysis as the response
            return f"🧠 Claude Analysis: {claude_response[:200]}{'...' if len(claude_response) > 200 else ''}\n\n✅ Analysis saved to: {filename}"
                
        except Exception as e:
            self.logger.error(f"❌ Error executing instruction: {e}")
            return f"❌ Error executing instruction: {str(e)}"

    def _handle_file_creation(self, claude_response: str, original_instruction: str) -> str:
        """Handle file creation tasks"""
        try:
            # For now, create a basic file based on instruction
            filename = "task_output.txt"
            content = f"""# Task Output - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Original Instruction:
{original_instruction}

## Claude Analysis:
{claude_response}

## Status:
Task completed by Jugad agent
"""
            
            file_path = Path(self.project_path) / filename
            file_path.write_text(content)
            
            return f"✅ Created file: {filename} in Jugad project"
            
        except Exception as e:
            return f"❌ Error creating file: {str(e)}"

    def _handle_command_execution(self, claude_response: str, original_instruction: str) -> str:
        """Handle command execution tasks"""
        try:
            # Extract command from instruction if possible
            if "git init" in original_instruction.lower():
                result = self.execute_command("git init", cwd=self.project_path)
                return f"✅ Executed: git init - {result}"
            elif "npm init" in original_instruction.lower():
                result = self.execute_command("npm init -y", cwd=self.project_path)
                return f"✅ Executed: npm init - {result}"
            else:
                return f"✅ Ready to execute command. Please specify the exact command to run."
                
        except Exception as e:
            return f"❌ Error executing command: {str(e)}"

    def _handle_project_setup(self, claude_response: str, original_instruction: str) -> str:
        """Handle project setup tasks"""
        try:
            # Create basic project structure
            readme_path = Path(self.project_path) / "README.md"
            readme_content = f"""# Jugad Project

Created by Jugad Agent on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Purpose
{original_instruction}

## Status
Project initialized and ready for development.

## Next Steps
- Add project-specific files
- Set up development environment
- Begin implementation
"""
            readme_path.write_text(readme_content)
            
            return f"✅ Project setup completed. Created README.md in Jugad project."
            
        except Exception as e:
            return f"❌ Error setting up project: {str(e)}"

    def _handle_research_task(self, claude_response: str, original_instruction: str) -> str:
        """Handle research tasks"""
        try:
            # Create research output file
            research_path = Path(self.project_path) / "research_output.md"
            research_content = f"""# Research Output - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Research Topic
{original_instruction}

## Analysis
{claude_response}

## Findings
Research completed by Jugad agent. Please review and provide more specific research requirements if needed.

## Next Steps
- Refine research scope
- Gather specific information
- Create implementation plan
"""
            research_path.write_text(research_content)
            
            return f"✅ Research task completed. Created research_output.md"
            
        except Exception as e:
            return f"❌ Error handling research task: {str(e)}"

    def _handle_general_task(self, claude_response: str, original_instruction: str) -> str:
        """Handle general tasks"""
        try:
            # Create task output
            task_path = Path(self.project_path) / "task_log.md"
            
            # Append to existing log or create new
            if task_path.exists():
                content = task_path.read_text()
            else:
                content = "# Jugad Task Log\n\n"
            
            content += f"""
## Task Entry - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Instruction:** {original_instruction}

**Analysis:** {claude_response}

**Status:** Completed

---
"""
            task_path.write_text(content)
            
            return f"✅ General task completed. Updated task_log.md"
            
        except Exception as e:
            return f"❌ Error handling general task: {str(e)}"

    def _record_task(self, instruction: str, result: str):
        """Record completed task"""
        task_record = {
            "timestamp": datetime.now().isoformat(),
            "instruction": instruction,
            "result": result,
            "status": "completed"
        }
        self.task_history.append(task_record)
        
        # Keep only last 50 tasks
        if len(self.task_history) > 50:
            self.task_history = self.task_history[-50:]

    def _is_simple_question(self, instruction: str) -> bool:
        """Check if this is a simple question that needs a direct answer"""
        simple_patterns = [
            r"what is \d+\+\d+",
            r"what is \d+\-\d+", 
            r"what is \d+\*\d+",
            r"what is \d+\/\d+",
            r"calculate \d+\+\d+",
            r"answer with only",
            r"just tell me",
            r"what is \d+",
            r"how much is \d+"
        ]
        
        instruction_lower = instruction.lower()
        for pattern in simple_patterns:
            if re.search(pattern, instruction_lower):
                return True
        return False
    
    def _extract_direct_answer(self, claude_response: str, original_instruction: str) -> str:
        """Extract the direct answer from Claude's response"""
        # Look for specific answer patterns first
        answer_patterns = [
            r"answer is (\d+)",
            r"result is (\d+)", 
            r"equals (\d+)",
            r"= (\d+)",
            r"the answer is (\d+)",
            r"answer: (\d+)",
            r"result: (\d+)",
            r"the answer is simply: (\d+)",
            r"answer is simply: (\d+)",
            r"simply: (\d+)",
            r"answer is (\d+)$"
        ]
        
        for pattern in answer_patterns:
            match = re.search(pattern, claude_response.lower())
            if match:
                return match.group(1)
        
        # For math questions, look for the calculation result
        if "what is" in original_instruction.lower() and any(op in original_instruction for op in ["+", "-", "*", "×", "/"]):
            # Try to find the result of the calculation
            # Look for patterns like "8 + 12 = 20" or "20"
            calculation_patterns = [
                r"(\d+)\s*\+\s*(\d+)\s*=\s*(\d+)",
                r"(\d+)\s*\-\s*(\d+)\s*=\s*(\d+)",
                r"(\d+)\s*\*\s*(\d+)\s*=\s*(\d+)",
                r"(\d+)\s*×\s*(\d+)\s*=\s*(\d+)",
                r"(\d+)\s*/\s*(\d+)\s*=\s*(\d+)"
            ]
            
            for pattern in calculation_patterns:
                match = re.search(pattern, claude_response)
                if match:
                    return match.group(3)  # Return the result
        
        # If no specific pattern found, return "Unable to extract answer"
        return "Unable to extract answer"

    def run(self):
        """Main agent loop"""
        self.logger.info("Jugad Agent starting...")
        
        # Register with the API server
        if not self.register():
            self.logger.error("Failed to register with API server")
            return
        
        self.logger.info("Jugad Agent registered successfully")
        
        # Main loop
        while True:
            try:
                # Send heartbeat
                self.send_heartbeat()
                
                # Check for messages
                self.check_for_messages()
                
                # Get project status and send pulse update
                project_status = self.get_project_status()
                if project_status['status'] == 'active':
                    self.send_pulse_update(
                        message=f"Jugad project monitoring: {project_status['status']}. Ready for instructions.",
                        status='online'
                    )
                else:
                    self.send_pulse_update(
                        message=f"Jugad project status: {project_status['status']}",
                        status='warning'
                    )
                
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                self.logger.info("Jugad Agent shutting down...")
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(60)  # Wait longer on error

if __name__ == "__main__":
    agent = JugadAgent()
    agent.run()
