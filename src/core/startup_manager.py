#!/usr/bin/env python3
"""
Automated AI Manager Startup Script
Handles environment variables, model detection, and service startup automatically
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path
from .claude_model_manager import ClaudeModelManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutomatedAIContextManager:
    """Automated startup and management for AI Manager system"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.services = {
            'backend_api': 'src/services/api_server.py',
            'monitoring_website': 'src/services/monitoring_service.py', 
            'ai_context_manager_agent': 'src/core/ai_context_manager.py',
            'blaze': 'src/agents/blaze_agent.py',
            'maya': 'src/agents/maya_agent.py'
        }
        self.processes = {}
        self.api_key = None
        
    def setup_environment(self):
        """Automatically setup environment variables"""
        logger.info("🔧 Setting up environment...")
        
        # Try to get API key from various sources
        self.api_key = self._find_api_key()
        
        if self.api_key:
            os.environ['ANTHROPIC_API_KEY'] = self.api_key
            logger.info("✅ ANTHROPIC_API_KEY set successfully")
            return True
        else:
            logger.warning("⚠️ ANTHROPIC_API_KEY not found - Claude integration will be disabled")
            return False
    
    def _find_api_key(self):
        """Find API key from various sources"""
        # Check current environment
        if os.getenv('ANTHROPIC_API_KEY'):
            logger.info("📋 Found API key in current environment")
            return os.getenv('ANTHROPIC_API_KEY')
        
        # Check bashrc
        bashrc_path = Path.home() / '.bashrc'
        if bashrc_path.exists():
            try:
                with open(bashrc_path, 'r') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if 'ANTHROPIC_API_KEY' in line and 'export' in line:
                            # Extract the key from the line
                            key = line.split('=')[1].strip().strip('"').strip("'")
                            if key and key != 'your_api_key_here':
                                logger.info("📋 Found API key in ~/.bashrc")
                                return key
            except Exception as e:
                logger.debug(f"Could not read ~/.bashrc: {e}")
        
        # Check .env file
        env_path = self.project_root / '.env'
        if env_path.exists():
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('ANTHROPIC_API_KEY='):
                            key = line.split('=', 1)[1].strip().strip('"').strip("'")
                            if key and key != 'your_api_key_here':
                                logger.info("📋 Found API key in .env file")
                                return key
            except Exception as e:
                logger.debug(f"Could not read .env file: {e}")
        
        return None
    
    def test_claude_integration(self):
        """Test Claude integration with latest model"""
        if not self.api_key:
            logger.warning("⚠️ No API key available for Claude testing")
            return False
        
        try:
            logger.info("🧪 Testing Claude integration...")
            manager = ClaudeModelManager(self.api_key)
            latest_model = manager.get_recommended_model()
            
            logger.info(f"✅ Claude integration working with model: {latest_model}")
            return True
        except Exception as e:
            logger.error(f"❌ Claude integration test failed: {e}")
            return False
    
    def start_service(self, service_name: str, script_path: str):
        """Start a service with proper environment"""
        try:
            logger.info(f"🚀 Starting {service_name}...")
            
            # Prepare environment
            env = os.environ.copy()
            if self.api_key:
                env['ANTHROPIC_API_KEY'] = self.api_key
            
            # Start the service
            process = subprocess.Popen(
                ['uv', 'run', 'python3', script_path],
                cwd=self.project_root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes[service_name] = process
            logger.info(f"✅ {service_name} started (PID: {process.pid})")
            
            # Give it a moment to start
            time.sleep(2)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start {service_name}: {e}")
            return False
    
    def start_all_services(self):
        """Start all AI Manager services in correct order"""
        logger.info("🚀 Starting AI Manager system...")
        
        # Start services in dependency order
        startup_order = [
            'backend_api',
            'monitoring_website', 
            'ai_context_manager_agent',
            'blaze_agent',
            'maya_agent'
        ]
        
        for service_name in startup_order:
            if service_name in self.services:
                script_path = self.services[service_name]
                if not self.start_service(service_name, script_path):
                    logger.error(f"❌ Failed to start {service_name}, stopping startup")
                    self.stop_all_services()
                    return False
                
                # Wait between services
                time.sleep(3)
        
        logger.info("✅ All services started successfully!")
        return True
    
    def stop_all_services(self):
        """Stop all running services"""
        logger.info("🛑 Stopping all services...")
        
        for service_name, process in self.processes.items():
            try:
                logger.info(f"🛑 Stopping {service_name}...")
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"✅ {service_name} stopped")
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️ Force killing {service_name}")
                process.kill()
            except Exception as e:
                logger.error(f"❌ Error stopping {service_name}: {e}")
        
        self.processes.clear()
        logger.info("✅ All services stopped")
    
    def check_service_health(self):
        """Check if all services are healthy"""
        logger.info("🏥 Checking service health...")
        
        try:
            import requests
            
            # Check backend API
            try:
                response = requests.get('http://localhost:5000/health', timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Backend API healthy")
                else:
                    logger.warning(f"⚠️ Backend API unhealthy: {response.status_code}")
            except Exception as e:
                logger.error(f"❌ Backend API not responding: {e}")
            
            # Check monitoring website
            try:
                response = requests.get('http://localhost:8000', timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Monitoring website healthy")
                else:
                    logger.warning(f"⚠️ Monitoring website unhealthy: {response.status_code}")
            except Exception as e:
                logger.error(f"❌ Monitoring website not responding: {e}")
                
        except ImportError:
            logger.warning("⚠️ requests not available for health checks")
    
    def run(self):
        """Main run method"""
        logger.info("🤖 AI Manager Automated Startup")
        logger.info("=" * 50)
        
        try:
            # Setup environment
            if not self.setup_environment():
                logger.warning("⚠️ Continuing without API key...")
            
            # Test Claude integration
            if self.api_key:
                self.test_claude_integration()
            
            # Start all services
            if not self.start_all_services():
                logger.error("❌ Failed to start services")
                return False
            
            # Check health
            time.sleep(5)  # Give services time to start
            self.check_service_health()
            
            logger.info("🎉 AI Manager system is running!")
            logger.info("📊 Monitoring website: http://localhost:8000")
            logger.info("🔧 Backend API: http://localhost:5000")
            logger.info("Press Ctrl+C to stop all services")
            
            # Keep running until interrupted
            try:
                while True:
                    time.sleep(10)
                    # Optional: periodic health checks
            except KeyboardInterrupt:
                logger.info("🛑 Shutdown requested...")
                self.stop_all_services()
                logger.info("👋 Goodbye!")
                return True
                
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            self.stop_all_services()
            return False

def main():
    """Main entry point"""
    manager = AutomatedAIContextManager()
    success = manager.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
