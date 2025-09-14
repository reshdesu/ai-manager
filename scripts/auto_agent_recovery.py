#!/usr/bin/env python3
"""
Auto Agent Recovery System
Automatically detects when agents go down and restarts them
"""

import subprocess
import time
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_recovery.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoAgentRecovery:
    def __init__(self):
        self.agents = {
            'api_server': {
                'process_name': 'api_server',
                'command': 'uv run python3 -m src.services.api_server',
                'log_file': 'logs/api_server.log',
                'port': 5000
            },
            'maya_agent': {
                'process_name': 'maya_agent',
                'command': 'uv run python3 -m src.agents.maya_agent',
                'log_file': 'logs/maya_agent.log',
                'port': None
            },
            'blaze_agent': {
                'process_name': 'blaze_agent',
                'command': 'uv run python3 -m src.agents.blaze_agent',
                'log_file': 'logs/blaze_agent.log',
                'port': None
            },
            'ai_manager': {
                'process_name': 'ai-context-manager',
                'command': 'uv run python3 -m src.agents.ai_context_manager_agent',
                'log_file': 'logs/ai_manager.log',
                'port': None
            }
        }
        self.restart_counts = {}
        
    def check_process_running(self, process_name):
        """Check if a process is running"""
        try:
            result = subprocess.run(
                ['pgrep', '-f', process_name],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking process {process_name}: {e}")
            return False
    
    def check_api_server_health(self):
        """Check if API server is responding"""
        try:
            import requests
            response = requests.get('http://localhost:5000/health', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def restart_agent(self, agent_name, agent_config):
        """Restart a specific agent"""
        try:
            logger.info(f"🔄 Restarting {agent_name}...")
            
            # Kill existing process
            subprocess.run(['pkill', '-f', agent_config['process_name']], 
                         capture_output=True)
            time.sleep(2)
            
            # Start new process
            cmd = f"nohup bash -c 'source ~/.bashrc && {agent_config['command']}' > {agent_config['log_file']} 2>&1 &"
            subprocess.run(cmd, shell=True)
            
            # Update restart count
            self.restart_counts[agent_name] = self.restart_counts.get(agent_name, 0) + 1
            
            logger.info(f"✅ {agent_name} restarted successfully (restart #{self.restart_counts[agent_name]})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to restart {agent_name}: {e}")
            return False
    
    def check_and_recover(self):
        """Check all agents and recover if needed"""
        logger.info("🔍 Checking agent health...")
        
        for agent_name, agent_config in self.agents.items():
            is_running = self.check_process_running(agent_config['process_name'])
            
            if not is_running:
                logger.warning(f"⚠️ {agent_name} is DOWN - attempting recovery")
                self.restart_agent(agent_name, agent_config)
            else:
                # Special check for API server
                if agent_name == 'api_server':
                    if not self.check_api_server_health():
                        logger.warning(f"⚠️ {agent_name} is running but not responding - restarting")
                        self.restart_agent(agent_name, agent_config)
                    else:
                        logger.debug(f"✅ {agent_name} is healthy")
                else:
                    logger.debug(f"✅ {agent_name} is running")
    
    def run_continuous_monitoring(self):
        """Run continuous monitoring"""
        logger.info("🚀 Auto Agent Recovery System started")
        logger.info(f"Monitoring {len(self.agents)} agents: {list(self.agents.keys())}")
        
        while True:
            try:
                self.check_and_recover()
                time.sleep(30)  # Check every 30 seconds
            except KeyboardInterrupt:
                logger.info("🛑 Auto recovery system stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error

if __name__ == "__main__":
    recovery = AutoAgentRecovery()
    recovery.run_continuous_monitoring()
