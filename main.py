#!/usr/bin/env python3
"""
AI Context Manager - Main Launcher
Organized project structure with agent consultation
"""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def main():
    """Main entry point"""
    print("🤖 AI Context Manager - Organized Structure")
    print("=" * 50)
    print("📁 Project Structure:")
    print("├── src/core/          # Core AI Context Manager")
    print("├── src/agents/        # AI Agent implementations") 
    print("├── src/services/      # Backend services")
    print("├── src/interfaces/    # External interfaces")
    print("├── config/           # Configuration files")
    print("├── tests/            # Test suite")
    print("├── docs/             # Documentation")
    print("└── scripts/          # Utility scripts")
    print()
    
    # Import and run the startup manager
    try:
        from core.startup_manager import AutomatedAIContextManager
        
        manager = AutomatedAIContextManager()
        success = manager.run()
        
        if success:
            print("✅ AI Context Manager system completed successfully")
        else:
            print("❌ AI Context Manager system encountered errors")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed and paths are correct")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
