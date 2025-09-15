# AI Manager Environment Configuration
# This file ensures all agents have access to the Claude API key

import os
import sys
from pathlib import Path

def setup_environment():
    """Set up environment for AI agents"""
    
    # Load API key from .bashrc if not already set
    if not os.environ.get('ANTHROPIC_API_KEY'):
        bashrc_path = Path.home() / '.bashrc'
        if bashrc_path.exists():
            with open(bashrc_path, 'r') as f:
                for line in f:
                    if line.startswith('export ANTHROPIC_API_KEY='):
                        # Extract the key value
                        key_value = line.split('=', 1)[1].strip().strip('"').strip("'")
                        os.environ['ANTHROPIC_API_KEY'] = key_value
                        break
    
    # Set Python path
    ai_manager_path = Path(__file__).parent.parent
    if str(ai_manager_path) not in sys.path:
        sys.path.insert(0, str(ai_manager_path))
    
    # Verify API key is available
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found!")
        print("Please add it to your ~/.bashrc file:")
        print("export ANTHROPIC_API_KEY='your-key-here'")
        return False
    
    print(f"✅ Environment setup complete - API key loaded: {api_key[:10]}...")
    return True

if __name__ == "__main__":
    setup_environment()
