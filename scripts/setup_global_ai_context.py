#!/usr/bin/env python3
"""
Setup script to make AI Context Manager globally available for all projects.
This ensures every project can use AI Context Manager.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def setup_global_ai_context():
    """Set up AI Context Manager to be globally available."""

    print("Setting up global AI Context Manager availability...")

    # Get the AI Context Manager directory
    ai_context_manager_dir = Path(__file__).parent.parent.absolute()

    # Create a global script that can be used from anywhere
    global_script_content = f'''#!/usr/bin/env python3
"""
Global AI Context Manager script.
This script makes AI Context Manager available from any directory.
"""

import sys
import subprocess
from pathlib import Path

# AI Context Manager location
AI_CONTEXT_MANAGER_DIR = Path("{ai_context_manager_dir}")

def main():
    """Run AI Context Manager from any location."""

    if len(sys.argv) < 2:
        print("Usage: ai-context <command> [args...]")
        print("Available commands: init, status, maintain, version")
        sys.exit(1)

    # Activate virtual environment and run command
    venv_python = AI_CONTEXT_MANAGER_DIR / "venv" / "bin" / "python"

    if not venv_python.exists():
        print("ERROR: AI Context Manager virtual environment not found!")
        print(f"Expected: {{venv_python}}")
        sys.exit(1)

    # Run the command
    cmd = [str(venv_python), "-m", "ai_context_manager.cli"] + sys.argv[1:]

    try:
        result = subprocess.run(cmd, check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: AI Context Manager command failed: {{e}}")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"ERROR: Failed to run AI Context Manager: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

    # Write the global script
    global_script_path = ai_context_manager_dir / "ai-context-global.py"
    with open(global_script_path, "w") as f:
        f.write(global_script_content)

    # Make it executable
    global_script_path.chmod(0o755)

    print(f"Global script created: {global_script_path}")

    # Create a symlink in a directory that's in PATH (if possible)
    try:
        # Try to create symlink in /usr/local/bin (requires sudo)
        symlink_path = Path("/usr/local/bin/ai-context")
        if not symlink_path.exists():
            print(f"To make AI Context Manager globally available, run:")
            print(f"sudo ln -s {global_script_path} {symlink_path}")
        else:
            print(f"Global symlink already exists: {symlink_path}")
    except PermissionError:
        print("Note: Cannot create global symlink without sudo privileges")

    return global_script_path


def create_project_template():
    """Create a project template with mandatory AI Context Manager integration."""

    print("Creating project template with mandatory AI Context Manager...")

    ai_context_manager_dir = Path(__file__).parent.parent.absolute()

    # Create project template directory
    template_dir = ai_context_manager_dir / "templates" / "mandatory_ai_context"
    template_dir.mkdir(exist_ok=True)

    # Create .ai-context-mandatory file
    mandatory_config = f'''# MANDATORY AI CONTEXT MANAGER INTEGRATION
# This file ensures AI Context Manager is always available for this project

# AI Context Manager location
AI_CONTEXT_MANAGER_DIR = "{ai_context_manager_dir}"

# Mandatory requirements
MANDATORY_AI_CONTEXT = true
SELF_HOSTING_REQUIRED = true
CONTEXT_MAINTENANCE_REQUIRED = true

# Integration script location
INTEGRATION_SCRIPT = "{ai_context_manager_dir}/ai-context-global.py"
'''

    with open(template_dir / ".ai-context-mandatory", "w") as f:
        f.write(mandatory_config)

    # Create project setup script
    setup_script_content = f'''#!/usr/bin/env python3
"""
Mandatory AI Context Manager setup for new projects.
This script MUST be run when setting up any new project.
"""

import sys
import subprocess
from pathlib import Path

# AI Context Manager location
AI_CONTEXT_MANAGER_DIR = Path("{ai_context_manager_dir}")

def setup_mandatory_ai_context():
    """Set up mandatory AI Context Manager for this project."""

    print("Setting up MANDATORY AI Context Manager for this project...")
    print("=" * 60)

    # Get project name from current directory or user input
    project_name = Path.cwd().name
    if len(sys.argv) > 1:
        project_name = sys.argv[1]

    print(f"Project: {{project_name}}")
    print(f"AI Context Manager: {{AI_CONTEXT_MANAGER_DIR}}")

    # Check if AI Context Manager is available
    venv_python = AI_CONTEXT_MANAGER_DIR / "venv" / "bin" / "python"
    if not venv_python.exists():
        print("ERROR: AI Context Manager not found!")
        print(f"Expected: {{venv_python}}")
        print("Please ensure AI Context Manager is properly installed.")
        sys.exit(1)

    # Initialize AI context for this project
    print("\\nInitializing AI context for this project...")
    cmd = [str(venv_python), "-m", "ai_context_manager.cli", "init", project_name]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to initialize AI context: {{e}}")
        print(e.stderr)
        sys.exit(1)

    # Create integration script for this project
    integration_script = f'''#!/usr/bin/env python3
"""
AI Context Manager integration for {{project_name}}.
This script ensures AI Context Manager is always available for this project.
"""

import subprocess
import sys
from pathlib import Path

AI_CONTEXT_MANAGER_DIR = Path("{ai_context_manager_dir}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python ai_context.py <command> [args...]")
        print("Available commands: init, status, maintain, version")
        sys.exit(1)

    venv_python = AI_CONTEXT_MANAGER_DIR / "venv" / "bin" / "python"
    cmd = [str(venv_python), "-m", "ai_context_manager.cli"] + sys.argv[1:]

    try:
        result = subprocess.run(cmd, check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {{e}}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
'''

    integration_script_path = Path("ai_context.py")
    with open(integration_script_path, "w") as f:
        f.write(integration_script)

    integration_script_path.chmod(0o755)

    print(f"\\nIntegration script created: {{integration_script_path}}")

    # Create mandatory note
    mandatory_note = f"""# MANDATORY AI CONTEXT MANAGER INTEGRATION

This project MUST use AI Context Manager for development.

## Requirements:
- AI Context Manager is MANDATORY for all development work
- All AI assistants working on this project MUST read the ai_context/ files
- Context must be maintained and updated regularly
- Self-hosting principles apply - use AI Context Manager on itself

## Usage:
```bash
# Check status
python ai_context.py status

# Maintain context
python ai_context.py maintain

# Initialize (if not done already)
python ai_context.py init "{project_name}"
```

## AI Context Manager Location:
{ai_context_manager_dir}

## Integration Script:
./ai_context.py

This integration is MANDATORY and cannot be removed.
"""

    with open("AI_CONTEXT_MANDATORY.md", "w") as f:
        f.write(mandatory_note)

    print("\\n" + "=" * 60)
    print("MANDATORY AI CONTEXT MANAGER SETUP COMPLETE")
    print("=" * 60)
    print(f"Project: {{project_name}}")
    print(f"AI Context: ./ai_context/")
    print(f"Integration: ./ai_context.py")
    print(f"Documentation: ./AI_CONTEXT_MANDATORY.md")
    print("\\nAI Context Manager is now MANDATORY for this project!")
    print("All development work must use the AI context system.")

if __name__ == "__main__":
    setup_mandatory_ai_context()
'''

    with open(template_dir / "setup_mandatory_ai_context.py", "w") as f:
        f.write(setup_script_content)

    # Create README for the template
    template_readme = f'''# Mandatory AI Context Manager Project Template

This template ensures that AI Context Manager is MANDATORY for all projects.

## Setup Instructions

1. Copy the files from this template to your new project
2. Run: `python setup_mandatory_ai_context.py <project_name>`
3. AI Context Manager will be integrated and mandatory for the project

## Files Included

- `.ai-context-mandatory` - Mandatory configuration
- `setup_mandatory_ai_context.py` - Setup script
- `AI_CONTEXT_MANDATORY.md` - Documentation (created during setup)
- `ai_context.py` - Integration script (created during setup)

## Requirements

- AI Context Manager must be installed at: {ai_context_manager_dir}
- All projects using this template MUST use AI Context Manager
- Self-hosting principles apply

This ensures consistent AI context management across all projects.
'''

    with open(template_dir / "README.md", "w") as f:
        f.write(template_readme)

    print(f"Project template created: {template_dir}")

    return template_dir


def main():
    """Main setup function."""

    print("=" * 60)
    print("GLOBAL AI CONTEXT MANAGER SETUP")
    print("=" * 60)

    # Set up global availability
    global_script = setup_global_ai_context()

    # Create project template
    template_dir = create_project_template()

    print("=" * 60)
    print("GLOBAL SETUP COMPLETE")
    print("=" * 60)
    print(f"Global script: {global_script}")
    print(f"Project template: {template_dir}")
    print()
    print("To make AI Context Manager globally available:")
    print(f"sudo ln -s {global_script} /usr/local/bin/ai-context")
    print()
    print("For new projects, use the mandatory template:")
    print(f"cp -r {template_dir}/* /path/to/new/project/")
    print("cd /path/to/new/project")
    print("python setup_mandatory_ai_context.py <project_name>")


if __name__ == "__main__":
    main()
