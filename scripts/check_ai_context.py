#!/usr/bin/env python3
"""
Pre-commit hook to ensure AI Context Manager is properly configured.
This script validates that the AI Context Manager project maintains its own context.
"""

import json
import sys
from pathlib import Path


def check_ai_context():
    """Check if AI Context Manager has proper AI context configuration."""

    print("Checking AI Context Manager configuration...")

    # Check if self-hosted context exists
    self_context_dir = Path("ai_context_self")
    if not self_context_dir.exists():
        print("ERROR: Self-hosted AI context not found!")
        print("Run: python3 self_hosted_ai_context.py")
        return False

    # Check required context files
    required_files = [
        "core.json",
        "architecture.json",
        "user_experience.json",
        "troubleshooting.json",
        "learning_history.json",
    ]

    missing_files = []
    for file_name in required_files:
        file_path = self_context_dir / file_name
        if not file_path.exists():
            missing_files.append(file_name)

    if missing_files:
        print(f"ERROR: Missing required context files: {missing_files}")
        return False

    # Check if core.json has self-hosting configuration
    core_file = self_context_dir / "core.json"
    try:
        with open(core_file) as f:
            core_data = json.load(f)

        ai_context = core_data.get("ai_context", {})
        if not ai_context.get("self_hosted"):
            print("ERROR: Self-hosting not enabled in core.json!")
            return False

        if ai_context.get("project_name") != "AI Context Manager":
            print("ERROR: Project name mismatch in core.json!")
            return False

    except (json.JSONDecodeError, KeyError) as e:
        print(f"ERROR: Invalid core.json: {e}")
        return False

    # Check if learning_history.json has recent entries
    learning_file = self_context_dir / "learning_history.json"
    try:
        with open(learning_file) as f:
            learning_data = json.load(f)

        learnings = learning_data.get("conversation_learnings", {})
        if len(learnings) == 0:
            print("WARNING: No learning entries found in learning_history.json")
        else:
            print(f"Found {len(learnings)} learning entries")

    except (json.JSONDecodeError, KeyError) as e:
        print(f"ERROR: Invalid learning_history.json: {e}")
        return False

    print("AI Context Manager configuration is valid!")
    return True


def check_mandatory_requirements():
    """Check mandatory AI Context Manager requirements."""

    print("Checking mandatory AI Context Manager requirements...")

    requirements = [
        ("Self-hosted context exists", Path("ai_context_self").exists()),
        ("Core functionality implemented", Path("ai_context_manager/core.py").exists()),
        ("CLI interface implemented", Path("ai_context_manager/cli.py").exists()),
        ("Package configuration exists", Path("setup.py").exists()),
        ("Modern packaging configured", Path("pyproject.toml").exists()),
        ("Documentation exists", Path("README.md").exists()),
        ("License exists", Path("LICENSE").exists()),
    ]

    all_passed = True
    for requirement, passed in requirements:
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {requirement}")
        if not passed:
            all_passed = False

    if not all_passed:
        print("ERROR: Some mandatory requirements are missing!")
        return False

    print("All mandatory requirements satisfied!")
    return True


def main():
    """Main function for pre-commit hook."""

    print("=" * 60)
    print("AI CONTEXT MANAGER PRE-COMMIT VALIDATION")
    print("=" * 60)

    # Check AI context configuration
    context_valid = check_ai_context()

    # Check mandatory requirements
    requirements_valid = check_mandatory_requirements()

    print("=" * 60)

    if context_valid and requirements_valid:
        print("SUCCESS: AI Context Manager is properly configured!")
        return 0
    else:
        print("FAILURE: AI Context Manager validation failed!")
        print()
        print("To fix:")
        print("1. Run: python3 self_hosted_ai_context.py")
        print("2. Ensure all required files are present")
        print("3. Check that self-hosting is properly configured")
        return 1


if __name__ == "__main__":
    sys.exit(main())
