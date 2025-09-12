"""
Core AI Context Manager functionality.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class AIContextManager:
    """Main AI Context Manager class."""
    
    def __init__(self, project_path: Optional[Path] = None):
        """Initialize the AI Context Manager."""
        self.project_path = project_path or Path.cwd()
        self.context_dir = self.project_path / "ai_context"
        self.config_file = self.project_path / ".ai-context.yaml"
        
    def init(self, project_name: str, project_type: str = "general") -> bool:
        """Initialize AI context for a project."""
        try:
            # Create context directory
            self.context_dir.mkdir(exist_ok=True)
            
            # Create configuration file
            config = {
                "project_name": project_name,
                "project_type": project_type,
                "created": datetime.now().isoformat(),
                "version": "1.0.0"
            }
            
            with open(self.config_file, "w") as f:
                yaml.dump(config, f, default_flow_style=False)
            
            # Create initial context files
            self._create_core_context(project_name, project_type)
            self._create_architecture_context()
            self._create_user_experience_context()
            self._create_troubleshooting_context()
            self._create_learning_history_context()
            
            return True
            
        except Exception as e:
            print(f"Error initializing AI context: {e}")
            return False
    
    def _create_core_context(self, project_name: str, project_type: str):
        """Create core.json context file."""
        core_data = {
            "ai_context": {
                "critical_read_first": True,
                "file_purpose": "Essential context for AI assistants working on this project",
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "project_name": project_name,
                "project_type": project_type
            },
            "project": {
                "name": project_name,
                "type": project_type,
                "description": f"AI context managed project: {project_name}",
                "tech_stack": [],
                "entry_points": [],
                "key_features": [],
                "target_users": []
            },
            "ai_assistant_rules": {
                "mandatory_context_usage": "CRITICAL: Always read ALL ai_context files when working on this project",
                "mandatory_frequent_context_review": [
                    "CRITICAL: Review ai_context every 30 minutes during development",
                    "Update context with new learnings and solutions"
                ]
            }
        }
        
        with open(self.context_dir / "core.json", "w") as f:
            json.dump(core_data, f, indent=2)
    
    def _create_architecture_context(self):
        """Create architecture.json context file."""
        architecture_data = {
            "project_structure": {
                "description": "Project structure and organization",
                "directories": {},
                "key_files": {},
                "dependencies": {
                    "required": [],
                    "optional": [],
                    "development": []
                }
            },
            "development_workflow": {
                "setup": [],
                "testing": [],
                "deployment": [],
                "maintenance": []
            }
        }
        
        with open(self.context_dir / "architecture.json", "w") as f:
            json.dump(architecture_data, f, indent=2)
    
    def _create_user_experience_context(self):
        """Create user_experience.json context file."""
        ux_data = {
            "target_users": {
                "primary_users": [],
                "user_needs": [],
                "pain_points": []
            },
            "user_journey": {
                "onboarding": [],
                "daily_usage": [],
                "advanced_usage": []
            }
        }
        
        with open(self.context_dir / "user_experience.json", "w") as f:
            json.dump(ux_data, f, indent=2)
    
    def _create_troubleshooting_context(self):
        """Create troubleshooting.json context file."""
        troubleshooting_data = {
            "common_issues": {
                "installation": [],
                "configuration": [],
                "runtime": [],
                "performance": []
            },
            "debugging_guides": {
                "logs": [],
                "tools": [],
                "commands": []
            },
            "known_solutions": {},
            "escalation_paths": []
        }
        
        with open(self.context_dir / "troubleshooting.json", "w") as f:
            json.dump(troubleshooting_data, f, indent=2)
    
    def _create_learning_history_context(self):
        """Create learning_history.json context file."""
        learning_data = {
            "conversation_learnings": {},
            "current_session_context": [],
            "ai_effectiveness_optimization": {
                "context_usage_patterns": {
                    "high_priority_sections": [],
                    "reference_frequency": []
                },
                "improvement_areas": {
                    "better_understanding": [],
                    "faster_problem_solving": [],
                    "better_decision_making": []
                },
                "context_maintenance": {
                    "update_triggers": [],
                    "update_frequency": "As needed",
                    "update_scope": "Targeted updates based on new learnings"
                }
            }
        }
        
        with open(self.context_dir / "learning_history.json", "w") as f:
            json.dump(learning_data, f, indent=2)
    
    def status(self) -> Dict[str, Any]:
        """Get status of AI context system."""
        status = {
            "project_path": str(self.project_path),
            "context_dir_exists": self.context_dir.exists(),
            "config_exists": self.config_file.exists(),
            "context_files": []
        }
        
        if self.context_dir.exists():
            for file_path in self.context_dir.glob("*.json"):
                status["context_files"].append({
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
        
        return status
    
    def maintain(self) -> bool:
        """Maintain the AI context system."""
        try:
            if not self.context_dir.exists():
                print("No AI context found. Run 'ai-context init' first.")
                return False
            
            # Update last_updated timestamp in core.json
            core_file = self.context_dir / "core.json"
            if core_file.exists():
                with open(core_file) as f:
                    core_data = json.load(f)
                
                core_data["ai_context"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
                
                with open(core_file, "w") as f:
                    json.dump(core_data, f, indent=2)
            
            print("AI context maintenance completed successfully.")
            return True
            
        except Exception as e:
            print(f"Error maintaining AI context: {e}")
            return False
