#!/usr/bin/env python3
"""
Blaze Backup Agent - Real Project Integration
Works with the actual blackblaze2-backup project
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.agents.base_intelligent_agent import BaseIntelligentAgent

class BlazeAgent(BaseIntelligentAgent):
    def __init__(self):
        super().__init__(
            agent_id="blaze-agent",
            agent_name="Blaze GUI Backup Agent",
            description="Intelligent agent for the BlackBlaze B2 Backup Tool - a cross-platform GUI application",
            capabilities=[
                "gui_development",
                "backup_management",
                "cloud_storage",
                "cross_platform_packaging",
                "pyside6_development",
                "aws_s3_integration"
            ]
        )
        self.project_path = Path("/home/yamnik/Projects/blackblaze-backup")
        self.api_base = "http://localhost:5000/api"
        
        # Set up logger
        import logging
        self.logger = logging.getLogger(f"blaze-agent")
    
    def process_message(self, message: Dict[str, Any]) -> bool:
        """Process messages - ONLY respond to @blaze mentions"""
        try:
            message_text = message.get('message', '')
            from_agent = message.get('from_agent', 'unknown')
            
            self.logger.info(f"📨 Received message from {from_agent}: {message_text[:100]}...")
            
            # STRICT RULE: Only respond if explicitly mentioned with @blaze
            if '@blaze' not in message_text.lower():
                self.logger.info("🚫 Message does not contain @blaze mention - IGNORING")
                return False
            
            # For @blaze messages, use the base intelligent response
            return super().process_message(message)
            
        except Exception as e:
            self.logger.error(f"❌ Error processing message: {e}")
            return False
        
    def get_project_status(self):
        """Get the current status of the backup project"""
        try:
            if not self.project_path.exists():
                return {"status": "project_not_found", "error": "Project directory not found"}
            
            # Check if main.py exists and is executable
            main_py = self.project_path / "main.py"
            if not main_py.exists():
                return {"status": "incomplete", "error": "main.py not found"}
            
            # Check git status
            git_status = self._run_command("git status --porcelain", cwd=self.project_path)
            
            # Check if there are any running backup processes
            backup_processes = self._run_command("ps aux | grep -E 'main.py|bb2backup' | grep -v grep")
            
            return {
                "status": "active",
                "project_path": str(self.project_path),
                "main_py_exists": main_py.exists(),
                "git_status": git_status.strip() if git_status else "clean",
                "backup_processes": len(backup_processes.strip().split('\n')) if backup_processes.strip() else 0,
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_backup_config(self):
        """Get backup configuration information"""
        try:
            config_files = [
                self.project_path / "sample.env",
                self.project_path / ".env",
                self.project_path / "pyproject.toml"
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
    
    def run_backup_check(self):
        """Run a backup status check"""
        try:
            # Check if the backup tool can be executed
            result = self._run_command("python3 main.py --help", cwd=self.project_path)
            return {
                "executable": True,
                "help_output": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "executable": False,
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
    
    def read_ai_context(self):
        """Read and parse AI context files to understand the real project"""
        try:
            context_path = self.project_path / "ai_context"
            if not context_path.exists():
                return {"error": "AI context directory not found"}
            
            context_data = {}
            
            # Read core.json
            core_file = context_path / "core.json"
            if core_file.exists():
                import json
                context_data["core"] = json.loads(core_file.read_text())
            
            # Read README.md
            readme_file = context_path / "README.md"
            if readme_file.exists():
                context_data["readme"] = readme_file.read_text()
            
            # Read architecture.json
            arch_file = context_path / "architecture.json"
            if arch_file.exists():
                context_data["architecture"] = json.loads(arch_file.read_text())
            
            return context_data
        except Exception as e:
            return {"error": str(e)}
    
    def get_project_overview(self):
        """Get comprehensive project overview from context files"""
        try:
            context = self.read_ai_context()
            if "error" in context:
                return context
            
            overview = {
                "project_name": "Unknown",
                "project_type": "Unknown", 
                "tech_stack": [],
                "version": "Unknown",
                "key_features": [],
                "description": "No description available"
            }
            
            # Extract from core.json
            if "core" in context:
                core = context["core"]
                if "project" in core:
                    project = core["project"]
                    overview["project_name"] = project.get("name", "Unknown")
                    overview["project_type"] = project.get("type", "Unknown")
                    overview["tech_stack"] = project.get("tech_stack", [])
                    overview["version"] = project.get("current_version", "Unknown")
                    overview["key_features"] = project.get("key_features", [])
            
            # Extract from README
            if "readme" in context:
                readme = context["readme"]
                # Extract description from README
                lines = readme.split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('#'):
                        overview["description"] = line.strip()
                        break
            
            return overview
        except Exception as e:
            return {"error": str(e)}
        """Build context for Claude with project-specific information"""
        try:
            project_status = self.get_project_status()
            backup_config = self.get_backup_config()
            
            context = f"""Project Information:
- Project Path: {self.project_path}
- Project Status: {project_status['status']}
- Main Executable: {project_status.get('main_py_exists', False)}
- Config Files: {len(backup_config.get('config_files', []))}
- Project Ready: {backup_config.get('project_ready', False)}

Available Commands:
- get_project_status(): Get current project status
- get_backup_config(): Get backup configuration
- run_backup_check(): Check if backup tool is executable
- analyze_project_files(): Analyze project structure

You are the Blaze Backup Agent managing the blackblaze2-backup project - a Python-based backup tool for BackBlaze B2 S3 storage."""
            
            return context
        except Exception as e:
            return f"Error building context: {e}"
    
    def _build_claude_context(self, message: str, from_agent: str) -> str:
        """Build context for Claude with project-specific information"""
        try:
            # Analyze project context
            project_context = self.analyze_project_context(str(self.project_path))
            
            context = f"""CRITICAL: You are about the BlackBlaze B2 Backup Tool - a GUI backup application.

Project Information:
- Project Path: {self.project_path}
- Files Found: {project_context.get('files_found', [])}
- AI Context Files: {project_context.get('ai_context_files', [])}

ACTUAL PROJECT DETAILS:"""
            
            # Add AI context information
            if 'config_files' in project_context:
                for file_name, file_data in project_context['config_files'].items():
                    if file_name == 'core.json' and 'project' in file_data:
                        project_info = file_data['project']
                        context += f"""
- Project Name: {project_info.get('name', 'Unknown')}
- Project Type: {project_info.get('type', 'Unknown')}
- Tech Stack: {project_info.get('tech_stack', [])}
- Version: {project_info.get('current_version', 'Unknown')}
- Key Features: {project_info.get('key_features', [])}
- Core Modules: {project_info.get('core_modules', [])}"""
            
            # Add README content
            if project_context.get('readme_content'):
                readme_lines = project_context['readme_content'].split('\n')[:10]
                context += f"\n- README Content:\n" + "\n".join(readme_lines)
            
            context += f"""

IMPORTANT: This is the BlackBlaze B2 Backup Tool - a cross-platform GUI backup application using Python, PySide6, and AWS S3 (BackBlaze B2).
It is NOT a generic backup agent - it is a specific GUI application for cloud backup.

You are the Blaze Backup Agent managing this specific GUI backup application project."""
            
            return context
        except Exception as e:
            return f"Error building context: {e}"
    def run(self):
        """Main agent loop"""
        self.logger.info("Blaze Backup Agent starting...")
        
        # Register with the API server
        if not self.register():
            self.logger.error("Failed to register with API server")
            return
        
        self.logger.info("Blaze Backup Agent registered successfully")
        
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
                        message=f"Backup project monitoring: {project_status['status']}. Ready for operations.",
                        status='online'
                    )
                else:
                    self.send_pulse_update(
                        message=f"Backup project status: {project_status['status']}",
                        status='warning'
                    )
                
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                self.logger.info("Blaze Backup Agent shutting down...")
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(60)  # Wait longer on error

if __name__ == "__main__":
    agent = BlazeAgent()
    agent.run()
