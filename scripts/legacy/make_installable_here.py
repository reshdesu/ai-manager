#!/usr/bin/env python3
"""
Make AI Context Manager installable from current location
"""

import shutil
from pathlib import Path


def make_installable():
    """Make the AI context manager installable from current project."""

    # 1. Create proper package structure in current project
    package_dir = Path("ai_context_manager_package")
    package_dir.mkdir(exist_ok=True)

    # 2. Copy package files
    shutil.copytree(
        "ai-context-manager", package_dir / "ai_context_manager", dirs_exist_ok=True
    )

    # 3. Create setup.py for local installation
    setup_content = """from setuptools import setup, find_packages

setup(
    name="ai-context-manager-local",
    version="1.0.0",
    description="AI context management system (local development)",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "ai-context-local=ai_context_manager.cli:main",
        ],
    },
)
"""

    with open(package_dir / "setup.py", "w") as f:
        f.write(setup_content)

    # 4. Create installation instructions
    install_instructions = """
# Install AI Context Manager locally

## Option 1: Install in development mode
cd ai_context_manager_package
pip install -e .

## Option 2: Install directly
pip install -e ./ai_context_manager_package

## Usage
ai-context-local init "My Project" --type web_application
ai-context-local maintain
"""

    with open(package_dir / "INSTALL.md", "w") as f:
        f.write(install_instructions)

    print("AI Context Manager made installable locally")
    print(f"Location: {package_dir}")
    print("Run: cd ai_context_manager_package && pip install -e .")


if __name__ == "__main__":
    make_installable()
