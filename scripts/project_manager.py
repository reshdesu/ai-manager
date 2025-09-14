#!/usr/bin/env python3
"""
AI Project Manager - Unified Management System
Manages both Maya 3D Game and BlackBlaze Backup Tool projects
"""

import json
import requests
import time
from datetime import datetime
from pathlib import Path

class AIProjectManager:
    def __init__(self):
        self.api_base = "http://localhost:5000/api"
        self.rules_file = Path("config/project_management_rules.json")
        self.load_management_rules()
        
    def load_management_rules(self):
        """Load project management rules and protocols"""
        try:
            with open(self.rules_file, 'r') as f:
                self.rules = json.load(f)
            print("✅ Management rules loaded successfully")
        except FileNotFoundError:
            print("❌ Management rules file not found")
            self.rules = {}
    
    def send_management_command(self, agent_id: str, command: str, context: str = ""):
        """Send a management command to a specific agent"""
        message = f"MANAGEMENT COMMAND: {command}\n\nContext: {context}\n\nPlease execute and report status."
        
        try:
            response = requests.post(
                f"{self.api_base}/communications/send",
                json={
                    "agent_id": "ai-manager",
                    "to_agent": agent_id,
                    "message": message
                }
            )
            return response.json()
        except Exception as e:
            print(f"❌ Error sending command: {e}")
            return None
    
    def get_project_status(self, project_name: str):
        """Get comprehensive status for a specific project"""
        agent_id = "maya-agent" if "maya" in project_name.lower() else "blaze-agent"
        
        command = f"""
        PROJECT STATUS REQUEST: {project_name}
        
        Please provide:
        1. Current development status
        2. Recent completed tasks
        3. Active work items
        4. Technical blockers or issues
        5. Next priority tasks
        6. Performance metrics
        7. Code quality status
        
        Format: Structured report with clear sections
        """
        
        return self.send_management_command(agent_id, "STATUS_REPORT", command)
    
    def assign_task(self, project_name: str, task_description: str, priority: str = "medium"):
        """Assign a task to a project agent"""
        agent_id = "maya-agent" if "maya" in project_name.lower() else "blaze-agent"
        
        command = f"""
        TASK ASSIGNMENT: {project_name}
        
        Task: {task_description}
        Priority: {priority}
        Deadline: To be determined based on complexity
        
        Please:
        1. Acknowledge task assignment
        2. Provide time estimate
        3. Identify any dependencies or blockers
        4. Suggest implementation approach
        """
        
        return self.send_management_command(agent_id, "TASK_ASSIGNMENT", command)
    
    def request_code_review(self, project_name: str, review_focus: str = "general"):
        """Request a code review for a project"""
        agent_id = "maya-agent" if "maya" in project_name.lower() else "blaze-agent"
        
        command = f"""
        CODE REVIEW REQUEST: {project_name}
        
        Review Focus: {review_focus}
        
        Please provide:
        1. Code quality assessment
        2. Architecture compliance review
        3. Performance optimization suggestions
        4. Security considerations
        5. Best practices recommendations
        6. Areas for improvement
        """
        
        return self.send_management_command(agent_id, "CODE_REVIEW", command)
    
    def coordinate_cross_project(self, shared_goal: str):
        """Coordinate activities between both projects"""
        command = f"""
        CROSS-PROJECT COORDINATION: {shared_goal}
        
        Both agents should:
        1. Identify shared requirements
        2. Coordinate technical approaches
        3. Share best practices
        4. Align on common standards
        5. Plan synchronized releases if applicable
        
        Please collaborate and report coordination status.
        """
        
        # Send to both agents
        maya_result = self.send_management_command("maya-agent", "COORDINATION", command)
        blaze_result = self.send_management_command("blaze-agent", "COORDINATION", command)
        
        return {"maya": maya_result, "blaze": blaze_result}
    
    def generate_management_report(self):
        """Generate a comprehensive management report"""
        print("\n" + "="*60)
        print("AI PROJECT MANAGER - COMPREHENSIVE REPORT")
        print("="*60)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get status from both projects
        print("\n📊 PROJECT STATUS OVERVIEW")
        print("-" * 40)
        
        maya_status = self.get_project_status("Maya 3D Game")
        blaze_status = self.get_project_status("BlackBlaze Backup")
        
        print("\n🎮 MAYA 3D LIFE SIMULATION GAME")
        print("-" * 40)
        if maya_status:
            print("✅ Status request sent to Maya agent")
        else:
            print("❌ Failed to get Maya project status")
        
        print("\n💾 BLACKBLAZE B2 BACKUP TOOL")
        print("-" * 40)
        if blaze_status:
            print("✅ Status request sent to Blaze agent")
        else:
            print("❌ Failed to get Blaze project status")
        
        print("\n📋 MANAGEMENT PROTOCOLS ACTIVE")
        print("-" * 40)
        print("✅ Daily status reporting")
        print("✅ Task prioritization system")
        print("✅ Technical review protocols")
        print("✅ Resource coordination")
        print("✅ Quality assurance standards")
        print("✅ Communication standards")
        
        print("\n🔧 AVAILABLE MANAGEMENT FUNCTIONS")
        print("-" * 40)
        print("• get_project_status(project_name)")
        print("• assign_task(project_name, task, priority)")
        print("• request_code_review(project_name, focus)")
        print("• coordinate_cross_project(shared_goal)")
        print("• generate_management_report()")
        
        print("\n" + "="*60)
    
    def interactive_management(self):
        """Interactive management interface"""
        print("\n🤖 AI PROJECT MANAGER - INTERACTIVE MODE")
        print("="*50)
        
        while True:
            print("\nAvailable Commands:")
            print("1. Get project status")
            print("2. Assign task")
            print("3. Request code review")
            print("4. Coordinate cross-project")
            print("5. Generate report")
            print("6. Exit")
            
            choice = input("\nEnter command (1-6): ").strip()
            
            if choice == "1":
                project = input("Project name (maya/blaze): ").strip()
                self.get_project_status(project)
                
            elif choice == "2":
                project = input("Project name (maya/blaze): ").strip()
                task = input("Task description: ").strip()
                priority = input("Priority (critical/high/medium/low): ").strip()
                self.assign_task(project, task, priority)
                
            elif choice == "3":
                project = input("Project name (maya/blaze): ").strip()
                focus = input("Review focus: ").strip()
                self.request_code_review(project, focus)
                
            elif choice == "4":
                goal = input("Shared coordination goal: ").strip()
                self.coordinate_cross_project(goal)
                
            elif choice == "5":
                self.generate_management_report()
                
            elif choice == "6":
                print("👋 Exiting AI Project Manager")
                break
                
            else:
                print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    manager = AIProjectManager()
    
    # Generate initial report
    manager.generate_management_report()
    
    # Start interactive mode
    manager.interactive_management()

