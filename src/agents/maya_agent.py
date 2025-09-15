#!/usr/bin/env python3
"""
Maya 3D Agent - Real Project Integration
Works with the actual Maya 3D Life Simulation Game project
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.agents.base_intelligent_agent import BaseIntelligentAgent
from src.utils.environment import setup_environment

# FORCE API KEY LOADING - NO FALLBACK
setup_environment()

class MayaAgent(BaseIntelligentAgent):
    def __init__(self):
        super().__init__(
            agent_id="maya-agent",
            agent_name="Maya",
            description="Intelligent agent for Maya - a web-based Three.js game",
            capabilities=[
                "3d_life_simulation",
                "three_js_development",
                "react_development",
                "typescript_development",
                "vite_build_management",
                "web_3d_rendering",
                "physics_simulation"
            ]
        )
        self.project_path = Path("/home/yamnik/Projects/maya")
        self.api_base = "http://localhost:5000/api"
        
        # Set up logger
        import logging
        self.logger = logging.getLogger(f"maya-agent")
        
    def get_project_status(self):
        """Get the current status of the Maya 3D project"""
        try:
            if not self.project_path.exists():
                return {"status": "project_not_found", "error": "Project directory not found"}
            
            # Check if package.json exists
            package_json = self.project_path / "package.json"
            if not package_json.exists():
                return {"status": "incomplete", "error": "package.json not found"}
            
            # Check if node_modules exists
            node_modules = self.project_path / "node_modules"
            dependencies_installed = node_modules.exists()
            
            # Check git status
            git_status = self._run_command("git status --porcelain", cwd=self.project_path)
            
            # Check if there are any running dev servers
            dev_processes = self._run_command("ps aux | grep -E 'vite|npm|node.*maya' | grep -v grep")
            
            # Check package.json for project info
            package_info = {}
            if package_json.exists():
                try:
                    package_info = json.loads(package_json.read_text())
                except:
                    package_info = {"error": "Could not parse package.json"}
            
            return {
                "status": "active",
                "project_path": str(self.project_path),
                "package_json_exists": package_json.exists(),
                "dependencies_installed": dependencies_installed,
                "git_status": git_status.strip() if git_status else "clean",
                "dev_processes": len(dev_processes.strip().split('\n')) if dev_processes.strip() else 0,
                "project_name": package_info.get("name", "unknown"),
                "project_version": package_info.get("version", "unknown"),
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_project_config(self):
        """Get project configuration information"""
        try:
            config_files = [
                self.project_path / "package.json",
                self.project_path / "tsconfig.json",
                self.project_path / "vite.config.ts",
                self.project_path / "README.md"
            ]
            
            config_data = {}
            for config_file in config_files:
                if config_file.exists():
                    if config_file.suffix == '.json':
                        config_data[config_file.name] = json.loads(config_file.read_text())
                    else:
                        config_data[config_file.name] = config_file.read_text()
            
            return {
                "config_files": list(config_data.keys()),
                "config_data": config_data,
                "project_ready": len(config_data) > 0
            }
        except Exception as e:
            return {"error": str(e)}
    
    def create_file(self, file_path: str, content: str):
        """Create a file with the given content"""
        try:
            full_path = self.project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            self.logger.info(f"✅ Created file: {file_path}")
            return {"success": True, "file_path": str(full_path)}
        except Exception as e:
            self.logger.error(f"❌ Failed to create file {file_path}: {e}")
            return {"success": False, "error": str(e)}
    
    def install_dependencies(self):
        """Install project dependencies using pnpm"""
        try:
            import subprocess
            import os
            
            # Change to project directory and run pnpm install
            result = subprocess.run(
                ['pnpm', 'install'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                self.logger.info("✅ Dependencies installed successfully")
                return {"success": True, "message": "Dependencies installed with pnpm"}
            else:
                self.logger.error(f"❌ pnpm install failed: {result.stderr}")
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            self.logger.error(f"❌ Failed to install dependencies: {e}")
            return {"success": False, "error": str(e)}
    
    def start_development_server(self):
        """Start the development server using pnpm"""
        try:
            import subprocess
            import os
            
            # Check if dependencies are installed
            if not (self.project_path / "node_modules").exists():
                self.logger.info("📦 Installing dependencies first...")
                install_result = self.install_dependencies()
                if not install_result.get("success"):
                    return install_result
            
            # Start development server in background
            process = subprocess.Popen(
                ['pnpm', 'run', 'dev'],
                cwd=self.project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.logger.info("🚀 Development server started with pnpm run dev")
            return {"success": True, "message": "Server started on http://localhost:5173", "process": process}
                
        except Exception as e:
            self.logger.error(f"❌ Failed to start development server: {e}")
            return {"success": False, "error": str(e)}
    
    def implement_character_creator(self):
        """Implement the CharacterCreator.tsx component"""
        try:
            # Use Claude to generate the CharacterCreator component
            if not self.claude_client:
                return {"error": "Claude client not available"}
            
            prompt = """Create a React TypeScript component called CharacterCreator.tsx for a 3D life simulation game using Three.js and React.

Requirements:
- Component should be in maya/src/ui/ folder
- Use React hooks (useState, useEffect)
- Include character customization options: name, age, gender, appearance (skin color, hair color, eye color, body size)
- Include stats sliders: intelligence, creativity, physical, social
- Include personality traits selection
- Use Three.js for 3D character preview
- Use Framer Motion for animations
- Integrate with existing Character type from game.ts
- Include save/cancel buttons
- Use modern React patterns and TypeScript

Generate the complete component code."""

            response = self.claude_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            component_code = response.content[0].text.strip()
            
            # Create the file
            result = self.create_file("src/ui/CharacterCreator.tsx", component_code)
            
            if result["success"]:
                self.logger.info("🎉 CharacterCreator.tsx component created successfully!")
                return {"success": True, "file_created": "CharacterCreator.tsx"}
            else:
                return result
                
        except Exception as e:
            self.logger.error(f"❌ Failed to implement CharacterCreator: {e}")
            return {"error": str(e)}
        """Check if project dependencies are installed"""
        try:
            node_modules = self.project_path / "node_modules"
            if not node_modules.exists():
                return {
                    "installed": False,
                    "message": "Dependencies not installed. Run 'npm install' to install.",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Check if package-lock.json exists
            package_lock = self.project_path / "package-lock.json"
            
            return {
                "installed": True,
                "node_modules_exists": True,
                "package_lock_exists": package_lock.exists(),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "installed": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_dev_server(self):
        """Check if dev server can be started"""
        try:
            # Check if npm is available
            npm_check = self._run_command("npm --version")
            if "Error" in npm_check:
                return {
                    "can_run": False,
                    "error": "npm not available",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Check if vite is available in package.json
            package_json = self.project_path / "package.json"
            if package_json.exists():
                package_data = json.loads(package_json.read_text())
                scripts = package_data.get("scripts", {})
                has_dev_script = "dev" in scripts
                
                return {
                    "can_run": True,
                    "npm_version": npm_check.strip(),
                    "has_dev_script": has_dev_script,
                    "dev_command": scripts.get("dev", "npm run dev"),
                    "timestamp": datetime.now().isoformat()
                }
            
            return {
                "can_run": False,
                "error": "package.json not found",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "can_run": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _run_command(self, command, cwd=None):
        """Run a shell command and return output"""
        import subprocess
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=cwd
            )
            return result.stdout
        except Exception as e:
            return f"Error: {e}"
    
    def _build_claude_context(self, message: str, from_agent: str) -> str:
        """Build context for Claude with project-specific information"""
        try:
            # Analyze project context
            project_context = self.analyze_project_context(str(self.project_path))
            
            # Get key project info
            pkg_info = project_context.get('package_info', {})
            readme_content = project_context.get('readme_content', '')
            
            context = f"""PROJECT FACTS:
- Name: {pkg_info.get('name', 'Unknown')}
- Description: {pkg_info.get('description', 'Unknown')}
- Type: {pkg_info.get('type', 'Unknown')}
- Main Dependencies: {list(pkg_info.get('dependencies', {}).keys())[:5]}
- Keywords: {pkg_info.get('keywords', [])}

README SUMMARY: {readme_content[:200]}...

CRITICAL: This is a web-based 3D life simulation game using Three.js and React, NOT Maya 3D software."""
            
            return context
        except Exception as e:
            return f"Error building context: {e}"
    
    def process_message(self, message: Dict[str, Any]) -> bool:
        """Process messages - DIRECT ACTION MODE (no hallucination)"""
        try:
            message_text = message.get('message', '')
            from_agent = message.get('from_agent', 'unknown')
            message_id = message.get('id', '')
            
            # Check if message has already been processed
            if message_id and self._is_message_processed(message_id):
                self.logger.info(f"🚫 Message {message_id[:8]}... already processed - SKIPPING")
                return False
            
            self.logger.info(f"📨 Received message from {from_agent}: {message_text[:100]}...")
            
            # Mark message as processed
            if message_id:
                self._mark_message_processed(message_id)
            
            # DIRECT ACTION MODE - Respond to @maya mentions OR direct messages from ai-manager
            if '@maya' in message_text.lower() or from_agent == 'ai-manager':
                
                # Use Claude to understand and respond to the message naturally
                if self.claude_client:
                    try:
                        # Clean the message by removing agent mentions before sending to Claude
                        clean_message = message_text
                        # Remove common agent mentions
                        for agent in ['@maya', '@blaze', '@jugad', '@ai-manager']:
                            clean_message = clean_message.replace(agent, '').strip()
                        
                        # Send the clean message with context about agent-to-agent communication
                        contextual_message = f"You are Maya, an AI agent specialized in 3D game development. You are receiving a message from another AI agent named {from_agent}: \"{clean_message}\"\n\nRespond as one AI agent to another - be direct and helpful."
                        
                        response = self.claude_client.messages.create(
                            model=self.get_current_model(),
                            max_tokens=300,
                            messages=[{"role": "user", "content": contextual_message}]
                        )
                        
                        claude_response = response.content[0].text
                        self.logger.info(f"🧠 Claude response: {claude_response}")
                        
                        self.send_message(from_agent, claude_response)
                        return True
                        
                    except Exception as e:
                        self.logger.error(f"❌ Claude error: {e}")
                        self.send_message(from_agent, f"❌ Error processing message: {str(e)}")
                        return True
                else:
                    self.logger.error("❌ Claude client not available")
                    self.send_message(from_agent, "❌ Claude client not available")
                    return True
            
            # For non-@maya messages, ignore completely
            self.logger.info("🚫 Message not for me - IGNORING")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error processing message: {e}")
            return False
    
    def _ask_claude_for_task_understanding(self, message: str) -> str:
        """Use Claude to understand what task is being requested"""
        try:
            prompt = f"""You are Maya, an AI agent for a 3D life simulation game built with Three.js and React.

Message received: "{message}"

Analyze this message and determine:
1. Is this asking me to create/implement something?
2. What specific task is being requested?
3. Should I implement code or just respond?

Respond with the specific task if it's a development request, or "no task" if it's just a question.

Examples:
- "create CharacterCreator.tsx" -> "charactercreator"
- "implement character creation" -> "charactercreator" 
- "how are you?" -> "no task"
"""

            response = self.claude_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            self.logger.error(f"❌ Claude task understanding failed: {e}")
            return "no task"

    def run(self):
        """Main agent loop"""
        self.logger.info("Maya Agent starting...")
        
        # Register with the API server
        if not self.register():
            self.logger.error("Failed to register with API server")
            return
        
        self.logger.info("Maya Agent registered successfully")
        
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
                        message=f"Maya 3D project monitoring: {project_status['status']}. Project: {project_status.get('project_name', 'unknown')}.",
                        status='online'
                    )
                else:
                    self.send_pulse_update(
                        message=f"Maya 3D project status: {project_status['status']}",
                        status='warning'
                    )
                
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                self.logger.info("Maya 3D Agent shutting down...")
                return
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(60)  # Wait longer on error

if __name__ == "__main__":
    agent = MayaAgent()
    agent.run()
